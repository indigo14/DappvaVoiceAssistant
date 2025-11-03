"""
Mock TTS Provider

A mock Text-to-Speech provider for testing without making actual API calls.
Allows simulation of different latencies and audio generation.

Useful for:
- Testing latency tracking without API costs
- Simulating different provider performance
- Development and debugging
- Testing without network dependencies

Configuration:
    mock_tts:
      mock_latency: 1.5  # Simulated processing time in seconds
      audio_format: "mp3"  # Format (mp3, wav, pcm)
      sample_rate: 24000  # Sample rate (Hz)
"""

import asyncio
import logging
import struct

from ..base import TTSProvider, TTSResult

logger = logging.getLogger(__name__)


class MockTTSProvider(TTSProvider):
    """Mock TTS provider for testing."""

    def __init__(self, config: dict):
        """
        Initialize mock TTS provider.

        Args:
            config: Configuration dictionary with:
                - mock_latency: Simulated processing time (default: 1.0s)
                - audio_format: Format to simulate (default: "mp3")
                - sample_rate: Sample rate (default: 24000)
        """
        super().__init__(config)
        self.latency = config.get('mock_latency', 1.0)
        self.audio_format = config.get('audio_format', 'mp3')
        self.sample_rate = config.get('sample_rate', 24000)

        logger.info(
            f"Initialized MockTTSProvider "
            f"(latency={self.latency}s, format={self.audio_format}, "
            f"rate={self.sample_rate}Hz)"
        )

    async def synthesize(self, text: str) -> TTSResult:
        """
        Simulate TTS synthesis with configurable latency.

        Args:
            text: Text to synthesize (determines output size)

        Returns:
            TTSResult with mock audio data
        """
        # Simulate processing time
        await asyncio.sleep(self.latency)

        # Generate mock audio data
        # Size based on text length (rough approximation)
        audio_duration = len(text) * 0.05  # ~50ms per character
        num_samples = int(audio_duration * self.sample_rate)

        # Create silence (all zeros) as mock audio
        if self.audio_format == 'pcm':
            # 16-bit PCM
            audio_bytes = b'\x00' * (num_samples * 2)
        else:
            # Fake MP3 header + silence
            # This won't be valid MP3, but size is realistic
            estimated_bitrate = 128000  # 128 kbps
            audio_size = int((audio_duration * estimated_bitrate) / 8)
            audio_bytes = b'\x00' * audio_size

        logger.debug(
            f"Mock TTS: Generated {len(audio_bytes)} bytes "
            f"for '{text[:30]}...' ({audio_duration:.2f}s) in {self.latency:.2f}s"
        )

        return TTSResult(
            audio_bytes=audio_bytes,
            sample_rate=self.sample_rate,
            format=self.audio_format,
            duration=audio_duration
        )

    def __repr__(self) -> str:
        return (f"MockTTSProvider(latency={self.latency}s, "
                f"format={self.audio_format}, rate={self.sample_rate}Hz)")
