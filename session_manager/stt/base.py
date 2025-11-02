"""
Base class for Speech-to-Text providers
VCA 1.0 - Phase 1
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class TranscriptionResult:
    """Result from STT transcription"""
    text: str
    confidence: Optional[float] = None
    language: Optional[str] = None
    duration: Optional[float] = None  # seconds


class STTProvider(ABC):
    """Abstract base class for STT providers"""

    def __init__(self, config: dict):
        """
        Initialize STT provider.

        Args:
            config: Provider-specific configuration
        """
        self.config = config

    @abstractmethod
    async def transcribe(self, audio_bytes: bytes) -> TranscriptionResult:
        """
        Transcribe audio bytes to text.

        Args:
            audio_bytes: Audio data (format depends on provider)

        Returns:
            TranscriptionResult with text and metadata

        Raises:
            Exception: If transcription fails
        """
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"
