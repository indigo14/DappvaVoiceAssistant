"""
Base class for Text-to-Speech providers
VCA 1.0 - Phase 1
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class TTSResult:
    """Result from TTS synthesis"""
    audio_bytes: bytes
    format: str  # e.g., 'mp3', 'wav', 'pcm'
    sample_rate: Optional[int] = None
    duration: Optional[float] = None  # seconds


class TTSProvider(ABC):
    """Abstract base class for TTS providers"""

    def __init__(self, config: dict):
        """
        Initialize TTS provider.

        Args:
            config: Provider-specific configuration
        """
        self.config = config

    @abstractmethod
    async def synthesize(self, text: str) -> TTSResult:
        """
        Synthesize speech from text.

        Args:
            text: Text to convert to speech

        Returns:
            TTSResult with audio bytes and metadata

        Raises:
            Exception: If synthesis fails
        """
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"
