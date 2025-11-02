# Phase 1: Audio & Wake Pipeline - Implementation Plan
**VCA 1.0**
**Start Date:** 2025-11-01
**Status:** In Progress

## Overview

Build hands-free voice activation system for Dad's voice assistant:
- **Wake-word detection**: "Hey Assistant" triggers listening
- **Audio streaming**: Phone → PC over network
- **Silence detection**: 2-3 second auto-stop
- **Stop controls**: Phrase-based immediate termination
- **Bluetooth support**: Works with Promate Engage-Pro headset

## Objectives (From vca1.0-implementation-plan.md)

**Phase 1 Goals:**
- Build Android service for wake-word detection + audio streaming
- Implement PC endpoint to receive audio streams
- Add VAD-driven auto-stop (2-3 second silence detection)
- Implement immediate "stop listening" guard via phrase recognition
- Log all wake events with session tracking

**Success Criteria:**
- Wake phrase "Hey Assistant" triggers listening ≥95% of attempts
- 2-3 second silence automatically stops recording
- "Cancel that" or "Stop for now" terminates session <1 second
- Audio streams from Samsung A05 to PC without dropouts
- No push-to-talk required (hands-free operation mandatory)
- Works with Bluetooth headset (Promate Engage-Pro)

## Implementation Strategy: Quick MVP First

### Recommended Approach
**Start with Home Assistant Companion App** (existing app, no custom development)

**Rationale:**
- Fastest path to Dad testing (1 week vs 2-3 weeks)
- Validates critical unknowns:
  - Wake-word accuracy with Dad's NZ accent
  - STT performance with Dad's slurred speech
  - Latency acceptable for conversation
- Lower risk (no custom app maintenance)
- Battle-tested (HA Companion App used by thousands)
- Can build custom Android app later if needed

**Decision Point After Week 1:**
- If Companion App works well → Continue, move to Phase 2
- If limitations found → Invest 1-2 weeks in custom Kotlin app

## Week 1: Quick MVP Implementation

### Days 1-2: Home Assistant Assist Pipeline Setup
**Time Estimate:** 6-8 hours

#### Step 1: Install Wyoming Add-ons
1. Access Home Assistant: `http://localhost:8123`
2. Navigate to Settings → Add-ons → Add-on Store
3. Search and install:
   - **Wyoming openWakeWord** (wake-word detection engine)
   - **Wyoming Whisper** (optional, for Phase 3+ local STT)
   - **Wyoming Piper** (optional, for Phase 3+ local TTS)

4. Configure Wyoming openWakeWord:
   - Start add-on
   - Open Web UI
   - Select wake-word model: "hey_jarvis" or "ok_nabu" (test both for NZ accent)
   - Note: May need custom model training for "Hey Assistant" phrase
   - Configure sensitivity threshold (balance false positives vs misses)
   - Save configuration

5. Verify Wyoming protocol ports:
   - openWakeWord: Port 10400 (default)
   - Whisper: Port 10300 (if installed)
   - Piper: Port 10200 (if installed)

#### Step 2: Create Assist Pipeline
1. Go to Settings → Voice Assistants
2. Click "Add Assistant"
3. Configure "Dad VCA Pipeline":
   - **Name:** Dad VCA Pipeline
   - **Language:** English (en-NZ if available, else en-US)
   - **Conversation Agent:** Home Assistant (default, will replace with custom webhook later)
   - **Wake Word Engine:** Wyoming Protocol (localhost:10400)
   - **Wake Word:** Select wake-word model from Step 1
   - **Speech-to-Text:**
     - Phase 1: Use HA Cloud or configure OpenAI Whisper API
     - Phase 3+: Wyoming Protocol (localhost:10300)
   - **Text-to-Speech:**
     - Phase 1: Use HA Cloud or configure OpenAI TTS
     - Phase 3+: Wyoming Protocol (localhost:10200)

4. Test pipeline:
   - Use HA's built-in Assist test tool
   - Speak wake-word → verify detection
   - Speak test phrase → verify transcription
   - Adjust sensitivity if needed

#### Step 3: Configure Custom Intents
Create custom intent scripts for stop controls.

**Edit:** `/home/indigo/homeassistant/config/configuration.yaml`

Add intent handling:
```yaml
# Custom intents for VCA stop controls
intent_script:
  StopAssistant:
    speech:
      text: "Stopping assistant for 5 minutes"
    action:
      - service: rest_command.session_manager_pause
        data:
          duration: 300

  CancelSession:
    speech:
      text: "Session cancelled"
    action:
      - service: rest_command.session_manager_cancel

# REST commands to session manager
rest_command:
  session_manager_pause:
    url: "http://localhost:5000/api/session/pause"
    method: POST
    content_type: "application/json"
    payload: '{"duration": {{ duration | default(300) }}}'
    timeout: 5

  session_manager_cancel:
    url: "http://localhost:5000/api/session/cancel"
    method: POST
    timeout: 5
```

**Create:** `/home/indigo/homeassistant/config/custom_sentences/en/vca_intents.yaml`

```yaml
language: "en"
intents:
  StopAssistant:
    data:
      - sentences:
          - "stop for now"
          - "pause assistant"
          - "be quiet"
          - "that's enough"

  CancelSession:
    data:
      - sentences:
          - "cancel that"
          - "never mind"
          - "forget it"
```

**Reload configuration:**
```bash
# Restart Home Assistant to load new configs
docker restart homeassistant
```

#### Step 4: Test WebSocket API Access
Create test script to verify session manager can connect to HA.

**File:** `/home/indigo/my-project3/Dappva/test_ha_websocket.py`

```python
#!/usr/bin/env python3
"""Test Home Assistant WebSocket API connectivity"""
import asyncio
import websockets
import json
import os

# Use token generated in Phase 0
HA_TOKEN = os.getenv("HA_LONG_LIVED_TOKEN", "YOUR_TOKEN_HERE")
HA_URL = "ws://localhost:8123/api/websocket"

async def test_connection():
    print(f"Connecting to {HA_URL}...")

    async with websockets.connect(HA_URL) as websocket:
        # 1. Receive auth_required message
        msg = await websocket.recv()
        print(f"Received: {msg}")

        # 2. Send authentication
        await websocket.send(json.dumps({
            "type": "auth",
            "access_token": HA_TOKEN
        }))

        # 3. Receive auth result
        auth_result = await websocket.recv()
        print(f"Auth result: {auth_result}")

        result = json.loads(auth_result)
        if result.get("type") == "auth_ok":
            print("✅ Authentication successful!")

            # 4. Test subscribing to events
            await websocket.send(json.dumps({
                "id": 1,
                "type": "subscribe_events",
                "event_type": "state_changed"
            }))

            # 5. Receive subscription result
            sub_result = await websocket.recv()
            print(f"Subscription result: {sub_result}")

            print("\n✅ WebSocket API test successful!")
            print("Session manager can connect to Home Assistant.")

        else:
            print(f"❌ Authentication failed: {result}")

if __name__ == "__main__":
    try:
        asyncio.run(test_connection())
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure:")
        print("1. Home Assistant is running (docker ps | grep homeassistant)")
        print("2. HA_LONG_LIVED_TOKEN environment variable is set")
        print("3. Token is valid (check HA → Profile → Long-Lived Access Tokens)")
```

**Run test:**
```bash
cd /home/indigo/my-project3/Dappva
export HA_LONG_LIVED_TOKEN="your_session_manager_token_here"
python3 test_ha_websocket.py
```

**Expected output:**
```
Connecting to ws://localhost:8123/api/websocket...
Received: {"type":"auth_required","ha_version":"2025.10.4"}
Auth result: {"type":"auth_ok","ha_version":"2025.10.4"}
✅ Authentication successful!
Subscription result: {"id":1,"type":"result","success":true,"result":null}

✅ WebSocket API test successful!
Session manager can connect to Home Assistant.
```

**Deliverable:** HA Assist pipeline configured and tested, WebSocket API accessible

---

### Days 3-4: Session Manager Backend
**Time Estimate:** 12-16 hours

#### Step 1: Project Setup
```bash
cd /home/indigo/my-project3/Dappva
mkdir -p session_manager
cd session_manager

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install \
    fastapi \
    uvicorn[standard] \
    websockets \
    python-multipart \
    webrtcvad \
    openai \
    pydantic \
    pydantic-settings \
    python-dotenv \
    pyyaml

# Save requirements
pip freeze > requirements.txt
```

#### Step 2: Configuration File Structure
**File:** `session_manager/config.yaml`

```yaml
# VCA Session Manager Configuration
app:
  name: "VCA Session Manager"
  version: "1.0.0"
  host: "0.0.0.0"
  port: 5000
  debug: true

home_assistant:
  url: "ws://localhost:8123/api/websocket"
  token: "${HA_SESSION_MANAGER_TOKEN}"  # From environment
  pipeline: "dad_vca_pipeline"

stt:
  # Primary STT provider
  primary: "openai_whisper"

  # Fallback if primary fails
  fallback: "openai_whisper"

  # Minimum confidence to accept result
  confidence_threshold: 0.6

  # Test mode: run multiple providers in parallel
  test_mode: false

  # Provider configurations
  providers:
    openai_whisper:
      api_key: "${OPENAI_API_KEY}"
      model: "whisper-1"
      language: "en"
      temperature: 0.0  # More deterministic
      response_format: "verbose_json"  # Get confidence scores

tts:
  # Primary TTS provider
  primary: "openai_tts"

  # Fallback if primary fails
  fallback: "openai_tts"

  # Provider configurations
  providers:
    openai_tts:
      api_key: "${OPENAI_API_KEY}"
      model: "tts-1"
      voice: "nova"  # Dad may prefer different voice
      speed: 1.0

vad:
  # Voice Activity Detection settings
  aggressiveness: 2  # 0-3, higher = more aggressive silence detection
  frame_duration_ms: 30  # Frame size for VAD
  silence_duration_s: 2.5  # Seconds of silence to auto-stop
  sample_rate: 16000  # Audio sample rate

session:
  # Session management
  max_duration_s: 300  # 5 minutes max per session
  pause_duration_s: 300  # Default pause duration (5 minutes)
  log_events: true
  log_path: "./logs"

audio:
  # Audio format requirements
  sample_rate: 16000
  channels: 1  # Mono
  sample_width: 2  # 16-bit

logging:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "./logs/session_manager.log"
```

**File:** `session_manager/.env.example`

```bash
# Home Assistant
HA_SESSION_MANAGER_TOKEN=your_session_manager_long_lived_token_here

# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Development overrides
DEBUG=true
LOG_LEVEL=DEBUG
```

#### Step 3: Core Architecture Files

**File:** `session_manager/main.py`

```python
#!/usr/bin/env python3
"""VCA Session Manager - Main entry point"""
import asyncio
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config import load_config
from logger import setup_logging
from websocket_server import setup_websocket_routes
from ha_client import HomeAssistantClient
from api import setup_api_routes

# Load configuration
config = load_config()
logger = setup_logging(config)

# Global HA client
ha_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    global ha_client

    # Startup
    logger.info("Starting VCA Session Manager...")
    ha_client = HomeAssistantClient(config)
    await ha_client.connect()
    logger.info("Connected to Home Assistant")

    yield

    # Shutdown
    logger.info("Shutting down...")
    if ha_client:
        await ha_client.disconnect()

# Create FastAPI app
app = FastAPI(
    title=config["app"]["name"],
    version=config["app"]["version"],
    lifespan=lifespan
)

# CORS middleware (for web dashboard in future)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup routes
setup_websocket_routes(app, config)
setup_api_routes(app, config)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": config["app"]["name"],
        "version": config["app"]["version"],
        "status": "running",
        "ha_connected": ha_client.is_connected() if ha_client else False
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=config["app"]["host"],
        port=config["app"]["port"],
        reload=config["app"]["debug"],
        log_level=config["logging"]["level"].lower()
    )
```

**File:** `session_manager/config.py`

```python
"""Configuration management"""
import yaml
import os
from pathlib import Path
from string import Template

def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration with environment variable substitution"""
    with open(config_path, 'r') as f:
        config_template = f.read()

    # Substitute environment variables
    config_str = Template(config_template).substitute(os.environ)

    # Parse YAML
    config = yaml.safe_load(config_str)

    # Ensure log directory exists
    log_path = config.get("session", {}).get("log_path", "./logs")
    Path(log_path).mkdir(parents=True, exist_ok=True)

    return config
```

**File:** `session_manager/logger.py`

```python
"""Logging setup"""
import logging
import sys
from pathlib import Path

def setup_logging(config: dict) -> logging.Logger:
    """Configure application logging"""
    log_config = config.get("logging", {})
    log_level = getattr(logging, log_config.get("level", "INFO"))
    log_format = log_config.get("format", "%(asctime)s - %(levelname)s - %(message)s")
    log_file = log_config.get("file", "./logs/session_manager.log")

    # Ensure log directory exists
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

    logger = logging.getLogger("session_manager")
    logger.setLevel(log_level)

    return logger
```

#### Step 4: STT Provider Implementation

**File:** `session_manager/stt/base.py`

```python
"""STT Provider base class (from modular-stt-tts-pipeline-design.md)"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Segment:
    """Word-level segment with timing"""
    start: float
    end: float
    text: str
    confidence: float

@dataclass
class TranscriptionResult:
    """STT transcription result"""
    text: str
    confidence: float
    language: str
    processing_time: float
    provider: str
    model: str
    metadata: dict
    segments: List[Segment] = None

class STTProvider(ABC):
    """Abstract base class for STT providers"""

    @abstractmethod
    async def transcribe(self, audio_data: bytes) -> TranscriptionResult:
        """
        Transcribe audio to text.

        Args:
            audio_data: Raw audio bytes (16kHz, 16-bit, mono PCM)

        Returns:
            TranscriptionResult with text, confidence, metadata
        """
        pass

    @abstractmethod
    def get_metadata(self) -> dict:
        """Return provider name, model, version, capabilities"""
        pass
```

**File:** `session_manager/stt/providers/openai_whisper.py`

```python
"""OpenAI Whisper API STT Provider"""
import time
import io
import logging
from openai import OpenAI
from ..base import STTProvider, TranscriptionResult, Segment

logger = logging.getLogger(__name__)

class OpenAIWhisperProvider(STTProvider):
    """OpenAI Whisper API STT implementation"""

    def __init__(self, config: dict):
        self.config = config
        self.client = OpenAI(api_key=config["api_key"])
        self.model = config.get("model", "whisper-1")
        self.language = config.get("language", "en")
        self.temperature = config.get("temperature", 0.0)

    async def transcribe(self, audio_data: bytes) -> TranscriptionResult:
        """Transcribe audio using OpenAI Whisper API"""
        start_time = time.time()

        try:
            # Create file-like object from bytes
            audio_file = io.BytesIO(audio_data)
            audio_file.name = "audio.wav"

            # Call OpenAI Whisper API
            response = self.client.audio.transcriptions.create(
                model=self.model,
                file=audio_file,
                language=self.language,
                temperature=self.temperature,
                response_format="verbose_json"
            )

            processing_time = time.time() - start_time

            # Extract segments if available
            segments = []
            if hasattr(response, "segments") and response.segments:
                segments = [
                    Segment(
                        start=seg.get("start", 0),
                        end=seg.get("end", 0),
                        text=seg.get("text", ""),
                        confidence=seg.get("no_speech_prob", 0)
                    )
                    for seg in response.segments
                ]

            return TranscriptionResult(
                text=response.text,
                confidence=1.0 - response.get("no_speech_prob", 0),
                language=response.language,
                processing_time=processing_time,
                provider="openai_whisper",
                model=self.model,
                metadata={
                    "duration": response.duration if hasattr(response, "duration") else 0
                },
                segments=segments
            )

        except Exception as e:
            logger.error(f"OpenAI Whisper API error: {e}")
            raise

    def get_metadata(self) -> dict:
        """Return provider metadata"""
        return {
            "provider": "openai_whisper",
            "model": self.model,
            "language": self.language,
            "type": "cloud"
        }
```

**File:** `session_manager/stt/router.py`

```python
"""STT Router - Model selection and fallback logic"""
import logging
from typing import Dict
from .base import STTProvider, TranscriptionResult
from .providers.openai_whisper import OpenAIWhisperProvider

logger = logging.getLogger(__name__)

class STTRouter:
    """Routes transcription requests to appropriate STT provider"""

    def __init__(self, config: dict):
        self.config = config
        self.providers: Dict[str, STTProvider] = {}
        self.primary = config["primary"]
        self.fallback = config["fallback"]
        self.confidence_threshold = config.get("confidence_threshold", 0.6)

        # Initialize providers
        self._init_providers()

    def _init_providers(self):
        """Initialize STT providers from config"""
        provider_configs = self.config.get("providers", {})

        for name, provider_config in provider_configs.items():
            if name == "openai_whisper":
                self.providers[name] = OpenAIWhisperProvider(provider_config)
                logger.info(f"Initialized STT provider: {name}")

    async def transcribe(self, audio_data: bytes) -> TranscriptionResult:
        """
        Transcribe audio using primary provider with fallback.

        Args:
            audio_data: Raw audio bytes (16kHz, 16-bit, mono)

        Returns:
            TranscriptionResult from best available provider
        """
        # Try primary provider
        try:
            result = await self.providers[self.primary].transcribe(audio_data)

            # Check confidence threshold
            if result.confidence < self.confidence_threshold:
                logger.warning(
                    f"Low confidence ({result.confidence:.2f}) from {self.primary}, "
                    f"trying fallback"
                )

                # Try fallback if different from primary
                if self.fallback != self.primary and self.fallback in self.providers:
                    fallback_result = await self.providers[self.fallback].transcribe(audio_data)
                    if fallback_result.confidence > result.confidence:
                        logger.info(f"Fallback provider gave better result")
                        return fallback_result

            return result

        except Exception as e:
            logger.error(f"Primary STT provider failed: {e}")

            # Try fallback
            if self.fallback in self.providers and self.fallback != self.primary:
                try:
                    logger.info(f"Attempting fallback provider: {self.fallback}")
                    return await self.providers[self.fallback].transcribe(audio_data)
                except Exception as fallback_error:
                    logger.error(f"Fallback STT provider also failed: {fallback_error}")
                    raise
            else:
                raise
```

**Deliverable:** Session manager STT pipeline with modular provider architecture

---

### Days 5-6: Integration, Testing & Companion App Setup
**Time Estimate:** 8-12 hours

#### Step 1: Complete WebSocket Server Implementation

**File:** `session_manager/websocket_server.py`

```python
"""WebSocket server for audio streaming"""
import logging
import asyncio
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict

from stt.router import STTRouter
from vad import VoiceActivityDetector
from session import SessionManager

logger = logging.getLogger(__name__)

# Active WebSocket connections
active_connections: Dict[str, WebSocket] = {}

def setup_websocket_routes(app, config):
    """Setup WebSocket routes"""

    stt_router = STTRouter(config["stt"])
    vad = VoiceActivityDetector(config["vad"])
    session_mgr = SessionManager(config)

    @app.websocket("/ws/audio")
    async def websocket_audio(websocket: WebSocket):
        """Handle audio streaming WebSocket"""
        await websocket.accept()
        client_id = id(websocket)
        active_connections[client_id] = websocket

        logger.info(f"Client {client_id} connected")

        audio_buffer = bytearray()
        session_id = session_mgr.create_session(client_id)

        try:
            while True:
                # Receive audio chunk
                data = await websocket.receive_bytes()
                audio_buffer.extend(data)

                # Check for voice activity
                is_speech = vad.is_speech(data)

                if not is_speech:
                    # Silence detected, check duration
                    if vad.silence_duration() >= config["vad"]["silence_duration_s"]:
                        logger.info(f"Session {session_id}: Silence timeout, processing audio")

                        # Transcribe accumulated audio
                        result = await stt_router.transcribe(bytes(audio_buffer))

                        logger.info(
                            f"Session {session_id}: Transcribed '{result.text}' "
                            f"(confidence: {result.confidence:.2f})"
                        )

                        # Check for stop phrases
                        if session_mgr.is_stop_phrase(result.text):
                            logger.info(f"Session {session_id}: Stop phrase detected")
                            await websocket.send_json({
                                "type": "stop",
                                "reason": "stop_phrase",
                                "transcript": result.text
                            })
                            audio_buffer.clear()
                            continue

                        # Send transcription result
                        await websocket.send_json({
                            "type": "transcription",
                            "text": result.text,
                            "confidence": result.confidence,
                            "session_id": session_id
                        })

                        audio_buffer.clear()
                        vad.reset()
                else:
                    vad.reset_silence()

        except WebSocketDisconnect:
            logger.info(f"Client {client_id} disconnected")
            session_mgr.end_session(session_id, "disconnect")
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            session_mgr.end_session(session_id, "error")
        finally:
            if client_id in active_connections:
                del active_connections[client_id]
```

#### Step 2: Voice Activity Detection

**File:** `session_manager/vad.py`

```python
"""Voice Activity Detection using WebRTC VAD"""
import webrtcvad
import time
import logging

logger = logging.getLogger(__name__)

class VoiceActivityDetector:
    """Detect voice activity and silence in audio stream"""

    def __init__(self, config: dict):
        self.config = config
        self.vad = webrtcvad.Vad(config.get("aggressiveness", 2))
        self.sample_rate = config.get("sample_rate", 16000)
        self.frame_duration_ms = config.get("frame_duration_ms", 30)
        self.silence_start = None

    def is_speech(self, audio_frame: bytes) -> bool:
        """
        Check if audio frame contains speech.

        Args:
            audio_frame: Raw audio bytes (must be 10/20/30ms of 16kHz audio)

        Returns:
            True if speech detected, False otherwise
        """
        try:
            return self.vad.is_speech(audio_frame, self.sample_rate)
        except Exception as e:
            logger.error(f"VAD error: {e}")
            return True  # Assume speech on error (don't cut off)

    def silence_duration(self) -> float:
        """
        Get duration of current silence period.

        Returns:
            Seconds of silence, or 0 if currently speaking
        """
        if self.silence_start is None:
            self.silence_start = time.time()
        return time.time() - self.silence_start

    def reset_silence(self):
        """Reset silence timer (speech detected)"""
        self.silence_start = None

    def reset(self):
        """Reset VAD state"""
        self.silence_start = None
```

#### Step 3: Session Management

**File:** `session_manager/session.py`

```python
"""Session state management and logging"""
import uuid
import time
import json
import logging
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class SessionManager:
    """Manage VCA sessions and event logging"""

    def __init__(self, config: dict):
        self.config = config
        self.sessions: Dict[str, dict] = {}
        self.log_events = config.get("session", {}).get("log_events", True)
        self.log_path = Path(config.get("session", {}).get("log_path", "./logs"))

        # Stop phrases (from Dad's requirements)
        self.stop_phrases = [
            "cancel that",
            "never mind",
            "forget it",
            "stop for now",
            "pause assistant",
            "be quiet",
            "that's enough"
        ]

    def create_session(self, client_id: int) -> str:
        """Create new session"""
        session_id = str(uuid.uuid4())

        self.sessions[session_id] = {
            "session_id": session_id,
            "client_id": client_id,
            "start_time": time.time(),
            "end_time": None,
            "stop_reason": None,
            "events": []
        }

        logger.info(f"Created session {session_id} for client {client_id}")
        self._log_event(session_id, "session_start", {})

        return session_id

    def end_session(self, session_id: str, reason: str):
        """End session and log results"""
        if session_id not in self.sessions:
            return

        session = self.sessions[session_id]
        session["end_time"] = time.time()
        session["stop_reason"] = reason
        session["duration"] = session["end_time"] - session["start_time"]

        logger.info(
            f"Ended session {session_id}: reason={reason}, "
            f"duration={session['duration']:.2f}s"
        )

        self._log_event(session_id, "session_end", {"reason": reason})

        # Write session log to file
        if self.log_events:
            self._write_session_log(session_id)

        # Clean up
        del self.sessions[session_id]

    def is_stop_phrase(self, text: str) -> bool:
        """Check if text contains a stop phrase"""
        text_lower = text.lower().strip()

        for phrase in self.stop_phrases:
            if phrase in text_lower:
                logger.info(f"Stop phrase detected: '{phrase}' in '{text}'")
                return True

        return False

    def _log_event(self, session_id: str, event_type: str, data: dict):
        """Log event to session"""
        if session_id not in self.sessions:
            return

        event = {
            "timestamp": time.time(),
            "type": event_type,
            "data": data
        }

        self.sessions[session_id]["events"].append(event)

    def _write_session_log(self, session_id: str):
        """Write session log to file"""
        if session_id not in self.sessions:
            return

        session = self.sessions[session_id]
        log_file = self.log_path / f"session_{session_id}.json"

        with open(log_file, 'w') as f:
            json.dump(session, f, indent=2)

        logger.debug(f"Wrote session log to {log_file}")
```

#### Step 4: REST API Endpoints

**File:** `session_manager/api.py`

```python
"""REST API endpoints"""
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Request/Response models
class PauseRequest(BaseModel):
    duration: int = 300  # seconds

class PauseResponse(BaseModel):
    status: str
    duration: int
    message: str

class CancelResponse(BaseModel):
    status: str
    message: str

def setup_api_routes(app, config):
    """Setup REST API routes"""

    router = APIRouter(prefix="/api")

    @router.post("/session/pause", response_model=PauseResponse)
    async def pause_session(request: PauseRequest):
        """Pause assistant for specified duration"""
        logger.info(f"Pause request: {request.duration}s")

        # TODO: Implement actual pause logic
        # For now, just acknowledge

        return PauseResponse(
            status="paused",
            duration=request.duration,
            message=f"Assistant paused for {request.duration} seconds"
        )

    @router.post("/session/cancel", response_model=CancelResponse)
    async def cancel_session():
        """Cancel current session immediately"""
        logger.info("Cancel request received")

        # TODO: Implement actual cancel logic

        return CancelResponse(
            status="cancelled",
            message="Session cancelled"
        )

    @router.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "service": config["app"]["name"],
            "version": config["app"]["version"]
        }

    app.include_router(router)
```

#### Step 5: Home Assistant Companion App Setup

**On Samsung A05:**

1. **Install Home Assistant Companion App**
   - Open Google Play Store
   - Search "Home Assistant Companion"
   - Install official app (by Home Assistant)

2. **Configure App**
   - Open app
   - Enter Home Assistant URL: `http://<WINDOWS_IP>:8123`
   - Login with Dad VCA credentials
   - Allow permissions:
     - Microphone (required for voice)
     - Notifications (for assistant responses)
     - Location (optional)

3. **Enable Assist Pipeline**
   - In app, tap Settings
   - Tap "Assist"
   - Select "Dad VCA Pipeline"
   - Enable wake-word detection
   - Test: Say "Hey Assistant"

4. **Configure Audio Routing**
   - Connect Bluetooth headset (Promate Engage-Pro)
   - In app settings, verify audio routes to headset
   - Test microphone input from headset

#### Step 6: End-to-End Testing

**Test Checklist:**

1. **Wake-Word Test**
   ```
   - Say "Hey Assistant"
   - Expected: App shows "Listening..." indicator
   - Result: Pass / Fail
   ```

2. **Transcription Test**
   ```
   - Say "Hey Assistant"
   - Say "What is the weather today?"
   - Wait 2-3 seconds
   - Expected: Transcription appears in HA/logs
   - Result: Pass / Fail
   ```

3. **Silence Detection Test**
   ```
   - Say "Hey Assistant"
   - Say "Hello there"
   - Stay silent for 3 seconds
   - Expected: Session auto-stops, transcription saved
   - Result: Pass / Fail
   ```

4. **Stop Phrase Test**
   ```
   - Say "Hey Assistant"
   - Say "Cancel that"
   - Expected: Session terminates immediately (<1s)
   - Result: Pass / Fail
   ```

5. **Bluetooth Headset Test**
   ```
   - Connect headset via Bluetooth
   - Trigger wake-word through headset mic
   - Expected: Audio captured from headset
   - Result: Pass / Fail
   ```

6. **Dad's Speech Test**
   ```
   - Have Dad trigger wake-word
   - Have Dad speak with natural (potentially slurred) speech
   - Check transcription accuracy
   - Note: Record samples for STT model comparison
   - Result: Accuracy %
   ```

**Logging Review:**
```bash
# Check session logs
cd /home/indigo/my-project3/Dappva/session_manager
tail -f logs/session_manager.log

# Check HA logs
docker logs homeassistant --tail 100 -f
```

**Deliverable:** Working end-to-end MVP with HA Companion App

---

### Day 7: Bug Fixes, Documentation & Review
**Time Estimate:** 4-6 hours

#### Bug Fix Priority List
1. Wake-word false positives/misses
2. Audio quality issues (choppy, low volume)
3. Latency >2 seconds
4. Silence detection cutting off mid-sentence
5. Stop phrases not recognized
6. Bluetooth audio routing failures

#### Documentation Tasks
1. **Create Phase 1 completion report**
   - What works / what doesn't
   - Dad's feedback
   - STT accuracy metrics with slurred speech
   - Latency measurements
   - Decision: Continue with Companion App or build custom?

2. **Update testing protocol**
   - Document test results
   - Record audio samples for future model comparison
   - Note edge cases (background noise, interruptions)

3. **Log findings for Phase 2**
   - STT model performance with Dad's speech
   - Areas needing improvement
   - Feature requests from Dad

#### Decision Point: Custom Android App?

**Continue with HA Companion App if:**
- ✅ Wake-word works reliably (≥90% accuracy)
- ✅ STT understands Dad's speech reasonably well
- ✅ Latency acceptable (<2 seconds)
- ✅ Battery drain reasonable (<10% per hour)
- ✅ Dad comfortable with UX

**Build Custom Android App if:**
- ❌ Wake-word accuracy insufficient
- ❌ Need more control over audio preprocessing
- ❌ Battery drain excessive
- ❌ UI/UX limitations frustrating Dad
- ❌ Need offline wake-word detection

---

## Week 2+ (If Needed): Custom Android App

### Custom App Development Plan
**Only proceed if HA Companion App has critical limitations**

**Time Estimate:** 16-24 hours

#### Components:
1. **Kotlin Android Studio project**
   - Foreground Service for always-on listening
   - AudioRecord API for audio capture
   - OkHttp WebSocket client to session manager

2. **Wake-word SDK integration**
   - Option A: Picovoice Porcupine (commercial, $$ per month)
   - Option B: Snowboy (deprecated but works offline)
   - Option C: Continue using HA openWakeWord via Companion App

3. **Audio preprocessing**
   - Noise cancellation
   - Automatic Gain Control (AGC)
   - Echo cancellation (if needed)

4. **Battery optimization**
   - Doze mode handling
   - Wake locks (minimize)
   - Audio batching/buffering

5. **UI/UX**
   - Simple status indicator (listening / idle / paused)
   - Manual toggle for pause/resume
   - Settings screen (wake-word sensitivity, etc.)

**Deliverable:** Custom Android app with optimized wake-word + audio streaming

---

## Technical Stack Summary

### Home Assistant
- **Wyoming openWakeWord**: Wake-word detection engine
- **Assist Pipeline**: Orchestration layer
- **Custom Intents**: Stop phrase recognition
- **WebSocket API**: Event streaming to session manager

### Session Manager (Python)
- **FastAPI**: Web framework + WebSocket server
- **websockets**: HA API client
- **webrtcvad**: Voice Activity Detection
- **OpenAI Python SDK**: Whisper API (STT) + TTS
- **Configuration**: YAML-based, environment variable substitution

### Android (MVP)
- **Home Assistant Companion App**: Existing app, no development

### Android (Custom, if needed)
- **Kotlin**: Modern Android development
- **Foreground Service**: Always-on listening
- **AudioRecord**: Low-latency audio capture
- **OkHttp**: WebSocket client
- **Picovoice Porcupine**: Wake-word SDK (optional)

---

## File Structure

```
/home/indigo/my-project3/Dappva/
├── session_manager/
│   ├── venv/                      # Python virtual environment
│   ├── logs/                      # Session logs
│   ├── config.yaml                # Configuration
│   ├── .env                       # Environment variables
│   ├── .env.example               # Environment template
│   ├── requirements.txt           # Python dependencies
│   ├── main.py                    # FastAPI entry point
│   ├── config.py                  # Config loader
│   ├── logger.py                  # Logging setup
│   ├── websocket_server.py        # WebSocket endpoint
│   ├── ha_client.py               # Home Assistant client
│   ├── api.py                     # REST API routes
│   ├── vad.py                     # Voice Activity Detection
│   ├── session.py                 # Session management
│   └── stt/
│       ├── base.py                # STTProvider abstract class
│       ├── router.py              # Model selection logic
│       └── providers/
│           ├── __init__.py
│           └── openai_whisper.py  # OpenAI Whisper provider
├── test_ha_websocket.py           # HA connectivity test
├── phase-1-implementation-plan.md # This file
└── voiceAssistantScripts/
    └── dad_profile_pre_filled_voice_assistant.md
```

---

## Testing Checkpoints

### Checkpoint 1: HA Assist Pipeline Configured
- [ ] Wyoming openWakeWord add-on installed and running
- [ ] "Dad VCA Pipeline" created in Home Assistant
- [ ] Wake-word "Hey Assistant" detectable
- [ ] Custom intents configured ("Stop for now", "Cancel that")
- [ ] WebSocket API accessible (test script passes)

### Checkpoint 2: Session Manager Running
- [ ] Python environment set up, dependencies installed
- [ ] FastAPI server starts without errors
- [ ] WebSocket endpoint accessible at ws://localhost:5000/ws/audio
- [ ] REST API endpoints responding (/health, /api/session/pause)
- [ ] STT provider initialized (OpenAI Whisper)
- [ ] Logging working (logs/session_manager.log created)

### Checkpoint 3: End-to-End Integration
- [ ] HA Companion App installed on Samsung A05
- [ ] App connected to Home Assistant
- [ ] Wake-word triggers listening mode
- [ ] Audio streams from phone to session manager
- [ ] Transcription returns from OpenAI Whisper
- [ ] Silence detection (2-3s) auto-stops recording
- [ ] Stop phrases terminate session immediately
- [ ] Bluetooth headset audio captured correctly

### Checkpoint 4: Testing with Dad
- [ ] Wake-word accuracy ≥90% with Dad's voice
- [ ] STT understands Dad's slurred speech reasonably well
- [ ] Latency <2 seconds (wake → listening)
- [ ] Stop controls feel responsive (not obtrusive)
- [ ] Dad comfortable with overall UX
- [ ] Battery usage acceptable (<10% per hour)

### Checkpoint 5: Phase 1 Complete
- [ ] All core objectives met (wake, stream, silence, stop)
- [ ] Event logging functional (session logs created)
- [ ] Documentation updated (completion report written)
- [ ] Decision made: Continue with Companion App or build custom
- [ ] Ready to proceed to Phase 2 (Session Manager & Baseline Chat)

---

## Success Criteria

**Phase 1 is complete when:**
1. ✅ Dad can trigger assistant with "Hey Assistant" (≥90% reliability)
2. ✅ 2-3 second silence stops recording automatically
3. ✅ "Cancel that" and "Stop for now" work immediately (<1 second)
4. ✅ Audio streams from phone to PC without dropouts
5. ✅ Works with Bluetooth headset hands-free
6. ✅ All wake events logged (session_id, timestamp, stop_reason)
7. ✅ Dad satisfied with stop controls ("doesn't feel obtrusive")
8. ✅ Transcription quality acceptable (ready for Phase 2 LLM integration)

---

## Risks & Mitigations

### Risk 1: Wake-word accuracy poor with NZ accent
**Probability:** Medium
**Impact:** High (blocks core functionality)

**Mitigation:**
- Test multiple wake-word models (openWakeWord, Porcupine, Vosk)
- Try different wake phrases ("OK Assistant", "Hey Computer")
- Adjust sensitivity threshold (balance false positives vs misses)
- Custom model training if needed (collect Dad's voice samples)

### Risk 2: STT doesn't understand Dad's slurred speech
**Probability:** Medium-High (known requirement)
**Impact:** High (affects usability)

**Mitigation:**
- Modular STT pipeline already designed for model swapping
- Test multiple providers in parallel (OpenAI, Deepgram, Google Cloud)
- Collect audio samples for A/B testing
- Plan to transition to fine-tuned local model if needed (Phase 3+)

### Risk 3: Latency too high (>2 seconds)
**Probability:** Low-Medium
**Impact:** Medium (affects conversation flow)

**Mitigation:**
- Optimize audio buffering (smaller chunks)
- Use streaming STT if available (incremental transcription)
- Consider local Whisper Small (Phase 3+) for lower latency
- Profile bottlenecks (network, API, processing)

### Risk 4: Battery drain excessive on Samsung A05
**Probability:** Medium (always-on listening)
**Impact:** Medium (usability concern)

**Mitigation:**
- HA Companion App is already optimized for battery
- If custom app needed: aggressive Doze mode handling
- Minimize wake locks, use job scheduling
- Offer configurable wake-word sensitivity (lower = less CPU)

### Risk 5: Bluetooth audio routing issues
**Probability:** Low-Medium (Android BT quirks)
**Impact:** High (Dad uses headset exclusively)

**Mitigation:**
- Test early with actual Promate Engage-Pro headset
- Use AudioManager API to force BT audio routing
- Implement fallback to phone mic if BT fails
- Document workarounds for common BT issues

---

## Next Immediate Steps (Post-Approval)

1. **Update CHANGELOG.md** with Phase 1 start date
2. **Create `.env` file** with HA token and OpenAI key
3. **Install HA add-ons** (openWakeWord, Whisper, Piper)
4. **Configure Assist pipeline** in Home Assistant
5. **Test wake-word detection** with sample audio
6. **Create `session_manager/` directory** with venv
7. **Implement core Python files** (main.py, config.py, logger.py)
8. **Build STT provider** (OpenAI Whisper)
9. **Test WebSocket connectivity** to HA
10. **Install HA Companion App** on Samsung A05
11. **End-to-end test** with Dad

---

## Time Estimate

**Quick MVP (Recommended):**
- Days 1-2: HA Assist Pipeline setup (6-8 hours)
- Days 3-4: Session Manager backend (12-16 hours)
- Days 5-6: Integration & testing (8-12 hours)
- Day 7: Bug fixes & documentation (4-6 hours)

**Total:** 30-42 hours (~1 week full-time, or 2 weeks part-time)

**With Custom Android App (If Needed):**
- Add 16-24 hours for custom app development
- **Total:** 46-66 hours (~2-3 weeks)

---

## References

- [vca1.0-implementation-plan.md](vca1.0-implementation-plan.md) - Full VCA roadmap
- [modular-stt-tts-pipeline-design.md](modular-stt-tts-pipeline-design.md) - STT/TTS architecture
- [stt-tts-hardware-analysis.md](stt-tts-hardware-analysis.md) - Hardware capabilities
- [phase-0-completion-status.md](phase-0-completion-status.md) - Phase 0 complete (100%)
- [voiceAssistantScripts/dad_profile_pre_filled_voice_assistant.md](voiceAssistantScripts/dad_profile_pre_filled_voice_assistant.md) - Dad's requirements
- [Home Assistant Assist](https://www.home-assistant.io/voice_control/) - HA voice control docs
- [Wyoming Protocol](https://github.com/rhasspy/wyoming) - HA voice integration protocol
- [openWakeWord](https://www.home-assistant.io/voice_assistant/open_wake_word/) - Wake-word detection
- [FastAPI](https://fastapi.tiangolo.com/) - Python web framework
- [WebRTC VAD](https://github.com/wiseman/py-webrtcvad) - Voice Activity Detection

---

**Status:** Ready to begin implementation
**Next Action:** Install Home Assistant add-ons and configure Assist pipeline
