"""
Local Whisper STT Provider
Runs Whisper model locally on GPU for reduced latency.
VCA 1.0 - Phase 3 (Session 10)
"""

import asyncio
import io
import logging
import wave
import numpy as np
from faster_whisper import WhisperModel
from typing import Optional

from ..base import STTProvider, TranscriptionResult

logger = logging.getLogger(__name__)


class LocalWhisperProvider(STTProvider):
    """Local Whisper STT provider using GPU acceleration via faster-whisper"""

    def __init__(self, config: dict):
        super().__init__(config)

        # Extract config parameters
        self.model_size = config.get('model_size', 'small')
        self.device = config.get('device', 'cuda')
        self.compute_type = config.get('compute_type', 'float16')
        self.language = config.get('language', 'en')
        self.beam_size = config.get('beam_size', 5)
        self.vad_filter = config.get('vad_filter', True)

        # Log initialization
        logger.info(
            f"Initializing LocalWhisperProvider: model={self.model_size}, "
            f"device={self.device}, compute_type={self.compute_type}"
        )

        # Load Whisper model (this will download on first run)
        try:
            self.model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type
            )
            logger.info(
                f"✓ Whisper model '{self.model_size}' loaded successfully on {self.device}"
            )
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise

    async def transcribe(self, audio_bytes: bytes) -> TranscriptionResult:
        """
        Transcribe audio using local Whisper model.

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

            # Convert to float32 array (faster-whisper expects this)
            audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

            # If stereo, convert to mono by averaging channels
            if n_channels == 2:
                audio_np = audio_np.reshape(-1, 2).mean(axis=1)

            # Transcribe using faster-whisper
            segments, info = self.model.transcribe(
                audio_np,
                language=self.language,
                beam_size=self.beam_size,
                vad_filter=self.vad_filter,
                # No temperature parameter in faster-whisper
            )

            # Combine all segments into single text
            text = " ".join([segment.text for segment in segments])

            # Calculate average confidence if available
            segments_list = list(segments)
            if segments_list:
                avg_confidence = sum(
                    getattr(seg, 'avg_logprob', 0.0) for seg in segments_list
                ) / len(segments_list)
                # Convert log probability to confidence (approximate)
                # avg_logprob ranges from ~-1 (high conf) to -10+ (low conf)
                confidence = max(0.0, min(1.0, 1.0 + (avg_confidence / 10.0)))
            else:
                confidence = 0.0

            # Calculate duration
            duration = len(audio_np) / sample_rate if sample_rate > 0 else None

            logger.debug(
                f"Transcribed {duration:.2f}s audio → '{text[:50]}...' "
                f"(confidence={confidence:.2f})"
            )

            return TranscriptionResult(
                text=text.strip(),
                confidence=confidence,
                language=info.language,
                duration=duration
            )

        except Exception as e:
            logger.error(f"Local Whisper transcription failed: {e}")
            raise

    def __repr__(self) -> str:
        return (
            f"LocalWhisperProvider(model='{self.model_size}', "
            f"device='{self.device}', compute='{self.compute_type}')"
        )
