"""
Stop phrase detection
VCA 1.0 - Phase 1
"""

from typing import List


class StopPhraseDetector:
    """Detect stop phrases in transcribed text"""

    def __init__(self, stop_phrases: List[str]):
        """
        Initialize stop phrase detector.

        Args:
            stop_phrases: List of phrases that end the session
        """
        self.stop_phrases = [phrase.lower() for phrase in stop_phrases]

    def is_stop_phrase(self, text: str) -> bool:
        """
        Check if text contains a stop phrase.

        Args:
            text: Transcribed text

        Returns:
            True if stop phrase detected
        """
        text_lower = text.lower().strip()

        for phrase in self.stop_phrases:
            if phrase in text_lower:
                return True

        return False

    def get_matched_phrase(self, text: str) -> str:
        """
        Get the stop phrase that was matched.

        Args:
            text: Transcribed text

        Returns:
            Matched stop phrase or empty string
        """
        text_lower = text.lower().strip()

        for phrase in self.stop_phrases:
            if phrase in text_lower:
                return phrase

        return ""

    def __repr__(self) -> str:
        return f"StopPhraseDetector(phrases={self.stop_phrases})"
