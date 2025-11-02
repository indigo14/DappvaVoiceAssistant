"""
Session state management
VCA 1.0 - Phase 1
"""

import time
from enum import Enum
from dataclasses import dataclass
from typing import Optional


class SessionState(Enum):
    """Session states"""
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    RESPONDING = "responding"


@dataclass
class Session:
    """Voice assistant session"""
    session_id: str
    device_id: str
    state: SessionState
    start_time: float
    last_activity: float
    audio_buffer: bytes = b""
    transcript: str = ""
    response: str = ""

    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = time.time()

    def duration(self) -> float:
        """Get session duration in seconds"""
        return time.time() - self.start_time

    def is_expired(self, max_duration: float) -> bool:
        """Check if session has exceeded max duration"""
        return self.duration() >= max_duration

    def append_audio(self, audio_chunk: bytes):
        """Append audio chunk to buffer"""
        self.audio_buffer += audio_chunk
        self.update_activity()

    def clear_audio_buffer(self):
        """Clear audio buffer after processing"""
        self.audio_buffer = b""

    def __repr__(self) -> str:
        return (
            f"Session(id='{self.session_id}', "
            f"state={self.state.value}, "
            f"duration={self.duration():.1f}s)"
        )


class SessionManager:
    """Manage voice assistant sessions"""

    def __init__(self, max_session_duration: float = 300):
        """
        Initialize session manager.

        Args:
            max_session_duration: Maximum session duration in seconds
        """
        self.max_session_duration = max_session_duration
        self.sessions: dict[str, Session] = {}

    def create_session(self, session_id: str, device_id: str) -> Session:
        """
        Create a new session.

        Args:
            session_id: Unique session identifier
            device_id: Device identifier

        Returns:
            New Session object
        """
        session = Session(
            session_id=session_id,
            device_id=device_id,
            state=SessionState.IDLE,
            start_time=time.time(),
            last_activity=time.time()
        )

        self.sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """Get session by ID"""
        return self.sessions.get(session_id)

    def end_session(self, session_id: str):
        """End and remove session"""
        if session_id in self.sessions:
            del self.sessions[session_id]

    def cleanup_expired_sessions(self):
        """Remove expired sessions"""
        expired = [
            sid for sid, session in self.sessions.items()
            if session.is_expired(self.max_session_duration)
        ]

        for session_id in expired:
            self.end_session(session_id)

    def get_active_sessions_count(self) -> int:
        """Get count of active sessions"""
        return len(self.sessions)

    def __repr__(self) -> str:
        return f"SessionManager(active_sessions={self.get_active_sessions_count()})"
