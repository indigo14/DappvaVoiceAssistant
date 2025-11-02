"""
Voice Activity Detection using webrtcvad
VCA 1.0 - Phase 1
"""

import webrtcvad
from typing import List, Tuple


class VoiceActivityDetector:
    """Detect speech activity in audio stream"""

    def __init__(
        self,
        sample_rate: int = 16000,
        frame_duration_ms: int = 30,
        aggressiveness: int = 3,
        silence_threshold_sec: float = 2.0
    ):
        """
        Initialize VAD.

        Args:
            sample_rate: Audio sample rate (8000, 16000, 32000, or 48000 Hz)
            frame_duration_ms: Frame duration (10, 20, or 30 ms)
            aggressiveness: VAD aggressiveness (0-3, higher = more aggressive)
            silence_threshold_sec: Seconds of silence to detect end of speech
        """
        if sample_rate not in [8000, 16000, 32000, 48000]:
            raise ValueError(f"Invalid sample rate: {sample_rate}")

        if frame_duration_ms not in [10, 20, 30]:
            raise ValueError(f"Invalid frame duration: {frame_duration_ms}")

        self.vad = webrtcvad.Vad(aggressiveness)
        self.sample_rate = sample_rate
        self.frame_duration_ms = frame_duration_ms
        self.silence_threshold_sec = silence_threshold_sec

        # Calculate frame size in bytes
        samples_per_frame = int(sample_rate * frame_duration_ms / 1000)
        self.frame_size = samples_per_frame * 2  # 2 bytes per sample (PCM16)

        # Calculate frames per second
        self.frames_per_second = 1000 / frame_duration_ms

        # Calculate silence threshold in frames
        self.silence_threshold_frames = int(silence_threshold_sec * self.frames_per_second)

        # State
        self.consecutive_silent_frames = 0
        self.has_speech_started = False

    def is_speech(self, audio_frame: bytes) -> bool:
        """
        Check if audio frame contains speech.

        Args:
            audio_frame: Audio data (must be frame_size bytes)

        Returns:
            True if speech detected, False otherwise
        """
        if len(audio_frame) != self.frame_size:
            raise ValueError(
                f"Invalid frame size: {len(audio_frame)} bytes "
                f"(expected {self.frame_size})"
            )

        return self.vad.is_speech(audio_frame, self.sample_rate)

    def process_frame(self, audio_frame: bytes) -> Tuple[bool, bool]:
        """
        Process audio frame and update VAD state.

        Args:
            audio_frame: Audio data

        Returns:
            Tuple of (is_speech, is_end_of_speech)
            - is_speech: True if current frame contains speech
            - is_end_of_speech: True if silence threshold exceeded (end of speech detected)
        """
        is_speech_frame = self.is_speech(audio_frame)

        if is_speech_frame:
            self.consecutive_silent_frames = 0
            self.has_speech_started = True
        else:
            if self.has_speech_started:
                self.consecutive_silent_frames += 1

        # Check if silence threshold exceeded
        is_end_of_speech = (
            self.has_speech_started and
            self.consecutive_silent_frames >= self.silence_threshold_frames
        )

        return is_speech_frame, is_end_of_speech

    def reset(self):
        """Reset VAD state"""
        self.consecutive_silent_frames = 0
        self.has_speech_started = False

    def __repr__(self) -> str:
        return (
            f"VoiceActivityDetector("
            f"sample_rate={self.sample_rate}, "
            f"frame_duration_ms={self.frame_duration_ms}, "
            f"silence_threshold_sec={self.silence_threshold_sec})"
        )
