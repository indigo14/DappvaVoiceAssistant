"""
Mock STT Provider

A mock Speech-to-Text provider for testing without making actual API calls.
Allows simulation of different latencies and transcription results.

Useful for:
- Testing latency tracking without API costs
- Simulating different provider performance
- Development and debugging
- Testing error handling

Configuration:
    mock_stt:
      mock_latency: 2.5  # Simulated processing time in seconds
      mock_text: "This is a mock transcription"  # Fixed response (optional)
      mock_confidence: 0.95  # Simulated confidence score
"""

import asyncio
import logging
from typing import Optional

from ..base import STTProvider, TranscriptionResult

logger = logging.getLogger(__name__)


class MockSTTProvider(STTProvider):
    """Mock STT provider for testing."""

    def __init__(self, config: dict):
        """
        Initialize mock STT provider.

        Args:
            config: Configuration dictionary with:
                - mock_latency: Simulated processing time (default: 1.0s)
                - mock_text: Fixed response text (default: "Mock transcription")
                - mock_confidence: Confidence score (default: 0.95)
                - mock_language: Language code (default: "en")
        """
        super().__init__(config)
        self.latency = config.get('mock_latency', 1.0)
        self.mock_text = config.get('mock_text', "Mock transcription")
        self.confidence = config.get('mock_confidence', 0.95)
        self.language = config.get('mock_language', 'en')

        logger.info(
            f"Initialized MockSTTProvider "
            f"(latency={self.latency}s, confidence={self.confidence})"
        )

    async def transcribe(self, audio_bytes: bytes) -> TranscriptionResult:
        """
        Simulate transcription with configurable latency.

        Args:
            audio_bytes: Audio data (ignored for mock)

        Returns:
            TranscriptionResult with mock data
        """
        # Simulate processing time
        await asyncio.sleep(self.latency)

        # Calculate mock duration based on audio size
        # Assuming 16kHz, mono, 16-bit PCM
        audio_duration = len(audio_bytes) / (16000 * 2)  # bytes / (sample_rate * bytes_per_sample)

        logger.debug(
            f"Mock STT: Processed {len(audio_bytes)} bytes "
            f"({audio_duration:.2f}s audio) in {self.latency:.2f}s"
        )

        return TranscriptionResult(
            text=self.mock_text,
            confidence=self.confidence,
            language=self.language,
            duration=audio_duration
        )

    def __repr__(self) -> str:
        return f"MockSTTProvider(latency={self.latency}s, text='{self.mock_text[:30]}...')"
