"""
PyTorch Whisper STT Provider
Native OpenAI Whisper implementation with CUDA support for GTX 970 (Maxwell).
Uses FP32 mode for optimal performance on Maxwell architecture.
VCA 1.0 - Session 10
"""

import asyncio
import io
import logging
import wave
import numpy as np
import whisper
import torch
from typing import Optional

from ..base import STTProvider, TranscriptionResult

logger = logging.getLogger(__name__)


class PyTorchWhisperProvider(STTProvider):
    """PyTorch Whisper STT provider with CUDA acceleration (FP32 for GTX 970)"""

    def __init__(self, config: dict):
        super().__init__(config)

        # Extract config parameters
        self.model_size = config.get('model_size', 'small')
        self.device = config.get('device', 'cuda')
        self.fp16 = config.get('fp16', False)  # CRITICAL: Must be False for Maxwell
        self.language = config.get('language', 'en')
        self.temperature = config.get('temperature', 0.0)
        self.beam_size = config.get('beam_size', 5)
        self.initial_prompt = config.get('initial_prompt', None)
        self.condition_on_previous_text = config.get('condition_on_previous_text', True)

        logger.info(
            f"Initializing PyTorchWhisperProvider: model={self.model_size}, "
            f"device={self.device}, fp16={self.fp16}"
        )

        # Verify CUDA availability if requested
        if self.device == 'cuda' and not torch.cuda.is_available():
            logger.warning(
                "CUDA device requested but not available. Falling back to CPU."
            )
            self.device = 'cpu'

        # Load Whisper model
        try:
            logger.info(f"Loading Whisper model '{self.model_size}' on {self.device}...")
            self.model = whisper.load_model(self.model_size, device=self.device)

            # Log device info
            if self.device == 'cuda':
                gpu_name = torch.cuda.get_device_name(0)
                gpu_capability = torch.cuda.get_device_capability(0)
                logger.info(
                    f"✓ Whisper model loaded on GPU: {gpu_name} "
                    f"(CC {gpu_capability[0]}.{gpu_capability[1]})"
                )
            else:
                logger.info(f"✓ Whisper model loaded on CPU")

        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise

    async def transcribe(self, audio_bytes: bytes) -> TranscriptionResult:
        """
        Transcribe audio using PyTorch Whisper.

        Args:
            audio_bytes: Raw audio bytes (WAV format, PCM16, 16kHz recommended)

        Returns:
            TranscriptionResult with transcribed text

        Raises:
            Exception: If transcription fails
        """
        # Run transcription in thread pool (Whisper is CPU/GPU intensive)
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            self._transcribe_sync,
            audio_bytes
        )

        return result

    def _transcribe_sync(self, audio_bytes: bytes) -> TranscriptionResult:
        """
        Synchronous transcription (runs in thread pool).

        Args:
            audio_bytes: Raw audio bytes in WAV format

        Returns:
            TranscriptionResult with text and metadata
        """
        try:
            # Convert WAV bytes to numpy array
            with io.BytesIO(audio_bytes) as wav_io:
                with wave.open(wav_io, 'rb') as wav_file:
                    sample_rate = wav_file.getframerate()
                    n_channels = wav_file.getnchannels()
                    audio_data = wav_file.readframes(wav_file.getnframes())

            # Convert to float32 array (Whisper expects this)
            audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

            # Convert stereo to mono by averaging channels
            if n_channels == 2:
                audio_np = audio_np.reshape(-1, 2).mean(axis=1)

            # Transcribe using PyTorch Whisper
            result = self.model.transcribe(
                audio_np,
                language=self.language,
                fp16=self.fp16,  # CRITICAL: False for Maxwell (FP32 mode)
                temperature=self.temperature,
                beam_size=self.beam_size,
                initial_prompt=self.initial_prompt,
                condition_on_previous_text=self.condition_on_previous_text,
            )

            # Extract text and metadata
            text = result.get('text', '')
            detected_language = result.get('language', self.language)

            # Calculate confidence from segments
            segments = result.get('segments', [])
            if segments:
                # avg_logprob is typically -0.1 to -1.0 (higher = better)
                avg_logprob = np.mean([seg.get('avg_logprob', -1.0) for seg in segments])
                # Convert to 0-1 scale (higher = more confident)
                # avg_logprob around -0.3 is very good, -1.0 is okay
                confidence = max(0.0, min(1.0, 1.0 + (avg_logprob / 2.0)))
            else:
                confidence = 0.5  # Unknown

            # Calculate duration
            duration = len(audio_np) / sample_rate if sample_rate > 0 else None

            logger.debug(
                f"Transcribed {duration:.2f}s audio → '{text[:50]}...' "
                f"(confidence={confidence:.2f}, language={detected_language})"
            )

            return TranscriptionResult(
                text=text.strip(),
                confidence=confidence,
                language=detected_language,
                duration=duration
            )

        except Exception as e:
            logger.error(f"PyTorch Whisper transcription failed: {e}")
            raise

    def __repr__(self) -> str:
        return (
            f"PyTorchWhisperProvider(model='{self.model_size}', "
            f"device='{self.device}', fp16={self.fp16})"
        )
