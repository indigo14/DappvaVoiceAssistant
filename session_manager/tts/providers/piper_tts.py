"""
Piper TTS Provider
Fast, lightweight local TTS using ONNX Runtime (CPU-optimized).
VCA 1.0 - Session 11
"""

import asyncio
import io
import logging
import wave
import json
from pathlib import Path
from typing import Optional

import numpy as np

from ..base import TTSProvider, TTSResult

logger = logging.getLogger(__name__)


class PiperTTSProvider(TTSProvider):
    """Piper TTS provider with ONNX Runtime (CPU-optimized)"""

    def __init__(self, config: dict):
        super().__init__(config)

        # Extract config parameters
        self.model_path = Path(config.get('model_path', 'models/piper/en_US-lessac-medium.onnx'))
        self.config_path = Path(config.get('config_path', str(self.model_path) + '.json'))
        self.speaker_id = config.get('speaker_id', None)  # Optional multi-speaker support
        self.length_scale = config.get('length_scale', 1.0)  # Speed control (1.0 = normal)
        self.noise_scale = config.get('noise_scale', 0.667)  # Variability
        self.noise_w = config.get('noise_w', 0.8)  # Phoneme duration variability
        self.sample_rate_target = config.get('sample_rate', 16000)  # VCA expects 16kHz

        logger.info(
            f"Initializing PiperTTSProvider: model={self.model_path.name}, "
            f"speed={self.length_scale}, target_rate={self.sample_rate_target}Hz"
        )

        # Validate model files exist
        if not self.model_path.exists():
            raise FileNotFoundError(f"Piper model not found: {self.model_path}")
        if not self.config_path.exists():
            raise FileNotFoundError(f"Piper config not found: {self.config_path}")

        # Load model config
        with open(self.config_path, 'r') as f:
            self.model_config = json.load(f)

        # Get native sample rate from model config
        self.sample_rate_native = self.model_config.get('audio', {}).get('sample_rate', 22050)

        # Initialize Piper model
        try:
            from piper import PiperVoice
            from piper.config import SynthesisConfig

            logger.info(f"Loading Piper model from {self.model_path}...")
            self.voice = PiperVoice.load(
                str(self.model_path),
                config_path=str(self.config_path),
                use_cuda=False  # CPU-only as recommended by experts
            )

            # Store SynthesisConfig class for later use
            self.SynthesisConfig = SynthesisConfig

            logger.info(
                f"✓ Piper model loaded: {self.model_path.name} "
                f"({self.sample_rate_native}Hz native)"
            )

        except Exception as e:
            logger.error(f"Failed to load Piper model: {e}")
            raise

    async def synthesize(self, text: str) -> TTSResult:
        """
        Synthesize speech from text using Piper TTS.

        Args:
            text: Text to convert to speech

        Returns:
            TTSResult with audio bytes in WAV format (PCM16, 16kHz mono)

        Raises:
            Exception: If synthesis fails
        """
        # Run synthesis in thread pool (Piper uses CPU-intensive operations)
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
            # Create synthesis config
            syn_config = self.SynthesisConfig(
                speaker_id=self.speaker_id,
                length_scale=self.length_scale,
                noise_scale=self.noise_scale,
                noise_w_scale=self.noise_w  # Note: parameter is noise_w_scale in config
            )

            # Synthesize audio - returns iterable of AudioChunk objects
            audio_chunks = []
            for audio_chunk in self.voice.synthesize(text, syn_config=syn_config):
                # AudioChunk has 'audio_int16_array' attribute containing int16 numpy array
                audio_chunks.append(audio_chunk.audio_int16_array)

            # Concatenate all chunks
            audio_np = np.concatenate(audio_chunks)

            # Resample if needed (Piper native rate -> VCA target rate)
            if self.sample_rate_native != self.sample_rate_target:
                audio_np = self._resample(
                    audio_np,
                    self.sample_rate_native,
                    self.sample_rate_target
                )
                sample_rate = self.sample_rate_target
            else:
                sample_rate = self.sample_rate_native

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
            logger.error(f"Piper TTS synthesis failed: {e}")
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
            audio: Audio array (int16)
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

            return resampled.astype(np.int16)

        except Exception as e:
            logger.error(f"Resampling failed: {e}")
            # Return original if resampling fails
            return audio

    def _to_wav(self, audio_np: np.ndarray, sample_rate: int) -> bytes:
        """
        Convert numpy array to WAV bytes (PCM16 format).

        Args:
            audio_np: Audio array (int16)
            sample_rate: Sample rate in Hz

        Returns:
            WAV file as bytes
        """
        # Piper returns int16, so no conversion needed
        audio_int16 = audio_np.astype(np.int16)

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
            f"PiperTTSProvider(model='{self.model_path.name}', "
            f"speed={self.length_scale}, rate={self.sample_rate_target}Hz)"
        )
