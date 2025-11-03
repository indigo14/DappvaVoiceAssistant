"""
Coqui TTS Provider (XTTS-v2)
Local neural TTS with PyTorch CUDA acceleration for GTX 970 (Maxwell).
Uses FP32 mode for optimal performance on Maxwell architecture.
VCA 1.0 - Session 11
"""

import asyncio
import io
import logging
import wave
import numpy as np
import torch
from pathlib import Path
from typing import Optional

from TTS.api import TTS

from ..base import TTSProvider, TTSResult

logger = logging.getLogger(__name__)


class CoquiTTSProvider(TTSProvider):
    """Coqui TTS provider (XTTS-v2) with GPU acceleration via PyTorch"""

    def __init__(self, config: dict):
        super().__init__(config)

        # Extract config parameters
        self.model_name = config.get('model_name', 'tts_models/multilingual/multi-dataset/xtts_v2')
        self.use_gpu = config.get('use_gpu', True)
        self.language = config.get('language', 'en')
        self.speed = config.get('speed', 1.0)
        self.reference_audio = config.get('reference_audio', None)  # For voice cloning
        self.speaker_id = config.get('speaker_id', None)  # For pre-trained voice selection
        self.sample_rate_target = config.get('sample_rate', 16000)  # VCA expects 16kHz

        logger.info(
            f"Initializing CoquiTTSProvider: model={self.model_name}, "
            f"gpu={self.use_gpu}, target_rate={self.sample_rate_target}Hz"
        )

        # Verify GPU availability if requested
        if self.use_gpu and not torch.cuda.is_available():
            logger.warning(
                "GPU requested but CUDA not available. Falling back to CPU."
            )
            self.use_gpu = False

        # Load TTS model
        try:
            logger.info(f"Loading Coqui TTS model '{self.model_name}'...")
            self.tts = TTS(self.model_name, gpu=self.use_gpu)

            # Log device info
            if self.use_gpu:
                gpu_name = torch.cuda.get_device_name(0)
                gpu_capability = torch.cuda.get_device_capability(0)
                logger.info(
                    f"✓ XTTS-v2 model loaded on GPU: {gpu_name} "
                    f"(CC {gpu_capability[0]}.{gpu_capability[1]})"
                )
            else:
                logger.info("✓ XTTS-v2 model loaded on CPU")

        except Exception as e:
            logger.error(f"Failed to load Coqui TTS model: {e}")
            raise

    async def synthesize(self, text: str) -> TTSResult:
        """
        Synthesize speech from text using Coqui TTS.

        Args:
            text: Text to convert to speech

        Returns:
            TTSResult with audio bytes in WAV format (PCM16, 16kHz mono)

        Raises:
            Exception: If synthesis fails
        """
        # Run synthesis in thread pool (TTS is CPU/GPU intensive)
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            self._synthesize_sync,
            text
        )

        return result

    def _synthesize_sync(self, text: str) -> TTSResult:
        """
        Synchronous synthesis (runs in thread pool).

        Args:
            text: Text to synthesize

        Returns:
            TTSResult with audio bytes and metadata
        """
        try:
            # Generate audio
            if self.reference_audio:
                # Voice cloning mode
                logger.debug(f"Synthesizing with voice cloning: {self.reference_audio}")
                audio_np = self.tts.tts(
                    text=text,
                    speaker_wav=self.reference_audio,
                    language=self.language
                )
            elif self.speaker_id:
                # Use pre-trained speaker
                logger.debug(f"Synthesizing with speaker_id: {self.speaker_id}")
                audio_np = self.tts.tts(
                    text=text,
                    speaker=self.speaker_id,
                    language=self.language
                )
            else:
                # Use first available speaker from the model
                logger.debug("Synthesizing with default speaker")
                # XTTS models have speaker manager with pre-trained voices
                speaker_id = self.tts.speakers[0] if hasattr(self.tts, 'speakers') and self.tts.speakers else None
                audio_np = self.tts.tts(
                    text=text,
                    speaker=speaker_id,
                    language=self.language
                )

            # XTTS native sample rate (typically 24kHz)
            native_sample_rate = 24000

            # Resample to target rate if needed (VCA expects 16kHz)
            if native_sample_rate != self.sample_rate_target:
                audio_np = self._resample(
                    audio_np,
                    native_sample_rate,
                    self.sample_rate_target
                )
                sample_rate = self.sample_rate_target
            else:
                sample_rate = native_sample_rate

            # Convert to PCM16 WAV format
            audio_wav = self._to_wav(audio_np, sample_rate)

            # Calculate duration
            duration = len(audio_np) / sample_rate

            logger.debug(
                f"Synthesized {len(text)} chars → {duration:.2f}s audio "
                f"({sample_rate}Hz)"
            )

            return TTSResult(
                audio_bytes=audio_wav,
                format='wav',
                sample_rate=sample_rate,
                duration=duration
            )

        except Exception as e:
            logger.error(f"Coqui TTS synthesis failed: {e}")
            raise

    def _resample(
        self,
        audio: np.ndarray,
        orig_sr: int,
        target_sr: int
    ) -> np.ndarray:
        """
        Resample audio to target sample rate using scipy.

        Args:
            audio: Audio array (float32)
            orig_sr: Original sample rate
            target_sr: Target sample rate

        Returns:
            Resampled audio array
        """
        if orig_sr == target_sr:
            return audio

        try:
            from scipy import signal

            # Calculate resampling ratio
            num_samples = int(len(audio) * target_sr / orig_sr)

            # Use scipy's resample for high-quality resampling
            resampled = signal.resample(audio, num_samples)

            logger.debug(
                f"Resampled audio: {orig_sr}Hz → {target_sr}Hz "
                f"({len(audio)} → {len(resampled)} samples)"
            )

            return resampled

        except Exception as e:
            logger.error(f"Resampling failed: {e}")
            # Return original if resampling fails
            return audio

    def _to_wav(self, audio_np: np.ndarray, sample_rate: int) -> bytes:
        """
        Convert numpy array to WAV bytes (PCM16 format).

        Args:
            audio_np: Audio array (float32, range -1.0 to 1.0)
            sample_rate: Sample rate in Hz

        Returns:
            WAV file as bytes
        """
        # Convert float32 (-1.0 to 1.0) to int16 (-32768 to 32767)
        audio_int16 = (audio_np * 32767).astype(np.int16)

        # Create WAV file in memory
        wav_io = io.BytesIO()
        with wave.open(wav_io, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_int16.tobytes())

        return wav_io.getvalue()

    def __repr__(self) -> str:
        return (
            f"CoquiTTSProvider(model='{self.model_name}', "
            f"gpu={self.use_gpu}, rate={self.sample_rate_target}Hz)"
        )
