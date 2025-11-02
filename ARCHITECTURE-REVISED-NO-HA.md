# VCA 1.0 Architecture - Revised (No Home Assistant)
**Date:** 2025-11-02
**Decision:** Remove Home Assistant, Build Custom Android App

## Architecture Decision Rationale

### Why We Removed Home Assistant

**Critical Discovery:**
- HA Companion App CANNOT stream audio to custom endpoints
- HA Companion App REQUIRES Home Assistant's Assist pipeline
- Home Assistant has NO OpenAI Whisper or OpenAI TTS integrations
- Would force us to use Wyoming Whisper (local) instead of OpenAI APIs
- Contradicts the modular STT/TTS provider design

**Dad's Actual Needs (from profile):**
- ✅ Communication (WhatsApp, calls, SMS)
- ✅ Reminders and check-ins
- ✅ Tech help (Bluetooth, Wi-Fi troubleshooting)
- ✅ Note-taking and retrieval
- ❌ NO smart home devices mentioned
- ❌ NO need for device control (lights, scenes, etc.)

**Conclusion:** Home Assistant adds complexity without providing value for Dad's use case.

---

## New Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────┐
│         Samsung A05 Phone                    │
│                                               │
│  ┌────────────────────────────────────────┐ │
│  │  VCA Custom Android App (Kotlin)       │ │
│  │                                         │ │
│  │  • Vosk wake-word detection (local)    │ │
│  │  • AudioRecord API (microphone)        │ │
│  │  • OkHttp WebSocket client             │ │
│  │  • MediaPlayer (audio playback)        │ │
│  │  • Foreground Service (background)     │ │
│  └────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
                    ↓ ↑
            WebSocket (bidirectional)
                    ↓ ↑
┌─────────────────────────────────────────────┐
│         PC (WSL2 Ubuntu)                     │
│                                               │
│  ┌────────────────────────────────────────┐ │
│  │  Session Manager (Python/FastAPI)      │ │
│  │                                         │ │
│  │  • FastAPI WebSocket server            │ │
│  │  • Receives audio stream from phone    │ │
│  │  • Voice Activity Detection (VAD)      │ │
│  │  • OpenAI Whisper API (STT)           │ │
│  │  • Custom LLM (Phase 2)                │ │
│  │  • OpenAI TTS API (TTS)                │ │
│  │  • Session state management            │ │
│  │  • Stop phrase detection               │ │
│  └────────────────────────────────────────┘ │
│                    ↓                          │
│  ┌────────────────────────────────────────┐ │
│  │  n8n (Standalone - Phase 5)            │ │
│  │                                         │ │
│  │  • Reminders and check-ins             │ │
│  │  • SMS/WhatsApp routing                │ │
│  │  • Workflow orchestration              │ │
│  └────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

---

## Component Details

### 1. Custom Android App

**Purpose:** Audio capture, wake-word detection, streaming to Session Manager

**Tech Stack:**
- **Language:** Kotlin
- **Framework:** Android SDK
- **WebSocket:** OkHttp 4.x
- **Wake-word:** Vosk Android SDK (free, open source)
- **Audio:** AudioRecord API (16kHz, PCM16)
- **Service:** Foreground Service (always-on listening)

**Key Features:**
- Wake-word detection ("OK Nabu" or custom phrase via Vosk)
- Audio streaming to Session Manager via WebSocket
- Audio playback from Session Manager
- Battery optimization (Doze mode handling)
- Background listening with notification

**Development Time:** 16-24 hours

---

### 2. Session Manager (Python/FastAPI)

**Purpose:** Core voice processing pipeline

**Tech Stack:**
- **Framework:** FastAPI 0.109+
- **WebSocket:** Native FastAPI WebSocket
- **STT:** OpenAI Whisper API
- **TTS:** OpenAI TTS API
- **VAD:** webrtcvad 2.0.10
- **Audio:** numpy, scipy

**Key Features:**
- WebSocket server for audio streaming
- Voice Activity Detection (silence timeout)
- STT via OpenAI Whisper API (modular, swappable)
- TTS via OpenAI TTS API (modular, swappable)
- Session state management
- Stop phrase detection ("that's all", "goodbye")

**Development Time:** 12-16 hours

---

### 3. n8n Automation Platform (Phase 5)

**Purpose:** Reminders, notifications, workflow automation

**Tech Stack:**
- **Platform:** n8n (Docker)
- **Integrations:** Twilio (SMS), WhatsApp, Email
- **Triggers:** Webhooks from Session Manager

**Key Features:**
- Scheduled reminders (medication, check-ins)
- SMS/WhatsApp routing
- Safety escalations (if Dad doesn't respond)
- Task orchestration

**Development Time:** 8-12 hours

---

## Data Flow

### Wake-Word Triggered Conversation

```
1. User says "OK Nabu"
    ↓
2. Vosk (on phone) detects wake-word locally
    ↓
3. Android app opens WebSocket to Session Manager
    ↓
4. Android app starts streaming audio (AudioRecord)
    ↓
5. Session Manager receives audio stream
    ↓
6. VAD detects speech activity
    ↓
7. User says: "What time is it?"
    ↓
8. VAD detects 2 seconds of silence
    ↓
9. Session Manager sends audio to OpenAI Whisper API
    ↓
10. Whisper returns transcript: "What time is it?"
    ↓
11. Session Manager processes with LLM (Phase 2)
    ↓
12. LLM returns: "It's 3:45 PM"
    ↓
13. Session Manager sends text to OpenAI TTS API
    ↓
14. TTS returns audio bytes (MP3)
    ↓
15. Session Manager streams audio to Android app
    ↓
16. Android app plays audio via MediaPlayer
    ↓
17. User hears: "It's 3:45 PM"
    ↓
18. Session Manager waits for stop phrase or timeout
    ↓
19. User says: "That's all"
    ↓
20. Session Manager closes session
```

---

## Audio Format Specifications

### Phone → Session Manager (Upstream)

**Format:**
- Encoding: PCM16 (Linear PCM, 16-bit signed integer)
- Sample Rate: 16000 Hz (16 kHz)
- Channels: Mono (1 channel)
- Bitrate: 256 kbps
- Container: Raw PCM bytes (no container)

**Why 16kHz?**
- OpenAI Whisper API optimal input
- Vosk wake-word models trained on 16kHz
- Lower bandwidth than 48kHz (smaller data transfer)
- Sufficient for speech recognition

**Frame Size:**
- 30ms frames (480 samples @ 16kHz)
- 960 bytes per frame (480 samples × 2 bytes/sample)

### Session Manager → Phone (Downstream)

**Format:**
- Encoding: MP3 (from OpenAI TTS API)
- Sample Rate: 24000 Hz (24 kHz, OpenAI default)
- Channels: Mono (1 channel)
- Bitrate: 64 kbps (OpenAI TTS output)

**Android playback:**
- MediaPlayer supports MP3 natively
- No transcoding needed

---

## Network Communication

### WebSocket Protocol

**Connection:**
```
ws://<PC_IP>:5000/audio-stream
```

**Message Types (JSON):**

**1. Client → Server (Android → Session Manager)**
```json
// Session start
{
  "type": "session_start",
  "timestamp": "2025-11-02T12:34:56Z",
  "device_id": "samsung_a05_001"
}

// Audio chunk (binary message)
// Raw PCM16 bytes (960 bytes per 30ms frame)

// Session end
{
  "type": "session_end",
  "reason": "stop_phrase",
  "timestamp": "2025-11-02T12:35:30Z"
}
```

**2. Server → Client (Session Manager → Android)**
```json
// Transcript (for display)
{
  "type": "transcript",
  "text": "What time is it?",
  "confidence": 0.95,
  "timestamp": "2025-11-02T12:35:10Z"
}

// Response text (for display)
{
  "type": "response_text",
  "text": "It's 3:45 PM",
  "timestamp": "2025-11-02T12:35:12Z"
}

// Audio response (binary message)
// MP3 bytes from OpenAI TTS

// Session status
{
  "type": "status",
  "state": "listening" | "processing" | "responding" | "idle",
  "timestamp": "2025-11-02T12:35:15Z"
}
```

---

## Wake-Word Detection

### Vosk Android SDK

**Why Vosk:**
- ✅ Free and open source
- ✅ Runs locally on phone (no network required)
- ✅ Supports custom wake words
- ✅ Small model size (~50MB)
- ✅ Low latency (<100ms detection time)
- ✅ Works offline

**Model:**
- `vosk-model-small-en-us-0.15` (39MB)
- English language
- Phoneme-based recognition
- Can detect custom phrases

**Wake-word options:**
1. "OK Nabu" (from original plan)
2. "Hey Assistant"
3. "OK Computer"
4. Custom phrase (train Vosk on specific phrase)

**Implementation:**
```kotlin
val recognizer = KaldiRecognizer(model, 16000.0f)
recognizer.setWords(true)

// Feed audio from microphone
val audioData = ByteArray(960) // 30ms frame
microphone.read(audioData)

if (recognizer.acceptWaveform(audioData)) {
    val result = recognizer.result
    // Check if wake-word detected
    if (result.contains("nabu") || result.contains("assistant")) {
        // Trigger Session Manager connection
        connectToSessionManager()
    }
}
```

---

## Voice Activity Detection (VAD)

### webrtcvad Implementation

**Purpose:** Detect when user stops speaking to trigger STT processing

**Parameters:**
```python
import webrtcvad

vad = webrtcvad.Vad(3)  # Aggressiveness 0-3 (3 = most aggressive)

# Process 30ms frames
frame_duration = 30  # ms
sample_rate = 16000  # Hz
frame_size = int(sample_rate * frame_duration / 1000) * 2  # 960 bytes

# Check if frame contains speech
is_speech = vad.is_speech(audio_frame, sample_rate)
```

**Silence Detection Algorithm:**
```python
silence_threshold = 2.0  # seconds
consecutive_silent_frames = 0
frames_per_second = 1000 / frame_duration  # ~33 frames/sec

for frame in audio_stream:
    if vad.is_speech(frame, 16000):
        consecutive_silent_frames = 0
    else:
        consecutive_silent_frames += 1

    if consecutive_silent_frames > (silence_threshold * frames_per_second):
        # 2 seconds of silence detected
        # Process accumulated audio with Whisper
        process_stt(accumulated_audio)
        break
```

---

## Security Considerations

### WebSocket Security

**Phase 1 (Development):**
- `ws://` (unencrypted WebSocket)
- localhost only (phone → PC on same network)
- No authentication

**Phase 3+ (Production):**
- `wss://` (WebSocket Secure with TLS)
- Certificate-based authentication
- Token-based session auth

### API Key Storage

**OpenAI API Key:**
- Stored in `.env` file on PC (Session Manager)
- NOT stored on phone
- Phone never sees API key

**Network Security:**
- Phone and PC on same local network (192.168.x.x or 172.x.x.x)
- No public internet exposure
- WSL2 port forwarding required (same as HA Phase 0 setup)

---

## Battery Optimization (Android)

### Foreground Service

**Why:**
- Android kills background services after ~10 minutes
- Foreground Service keeps app alive with notification
- User can control via notification actions

**Implementation:**
```kotlin
class VoiceAssistantService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val notification = createNotification()
        startForeground(NOTIFICATION_ID, notification)

        // Start wake-word listening
        startWakeWordDetection()

        return START_STICKY
    }
}
```

### Doze Mode Handling

**Android Doze mode:**
- Restricts app activity when screen off
- Use `PowerManager.WakeLock` for critical listening periods
- Release wake lock when idle

**Battery-friendly approach:**
```kotlin
// Only hold wake lock during active session
fun startSession() {
    wakeLock.acquire(10 * 60 * 1000L) // 10 minutes max
    // ... session logic
}

fun endSession() {
    if (wakeLock.isHeld) {
        wakeLock.release()
    }
}
```

---

## Modular Provider Architecture

### STT Provider Interface

```python
# stt/base.py
from abc import ABC, abstractmethod
from typing import AsyncIterator

class STTProvider(ABC):
    @abstractmethod
    async def transcribe(self, audio_stream: AsyncIterator[bytes]) -> str:
        """Transcribe audio stream to text"""
        pass
```

### Available STT Providers

**1. OpenAI Whisper API (Phase 1)**
```python
# stt/providers/openai_whisper.py
from openai import AsyncOpenAI

class OpenAIWhisperProvider(STTProvider):
    async def transcribe(self, audio_stream: AsyncIterator[bytes]) -> str:
        audio_bytes = b"".join([chunk async for chunk in audio_stream])

        response = await self.client.audio.transcriptions.create(
            model="whisper-1",
            file=("audio.wav", audio_bytes),
            language="en"
        )
        return response.text
```

**2. Deepgram (Alternative - faster, real-time)**
```python
# stt/providers/deepgram.py
class DeepgramProvider(STTProvider):
    # Real-time streaming STT
    # Lower latency than OpenAI Whisper
    # Cost: ~$0.0043/min
    pass
```

**3. Local Whisper (Phase 3+ - privacy)**
```python
# stt/providers/local_whisper.py
class LocalWhisperProvider(STTProvider):
    # Uses faster-whisper library
    # Runs on GTX 970 GPU
    # Free, local, private
    pass
```

**Swapping providers:**
```yaml
# config.yaml
stt_provider: "openai_whisper"  # Change to "deepgram" or "local_whisper"
```

---

## Development Phases

### Phase 1: Core Voice Pipeline (28-40 hours)

**Week 1: Android App (16-24 hours)**
- Days 1-3: Basic app structure
  - Kotlin project setup (Android Studio)
  - WebSocket client (OkHttp)
  - Audio recording (AudioRecord)
  - Audio playback (MediaPlayer)

- Days 4-5: Wake-word integration
  - Vosk SDK integration
  - Wake-word detection loop
  - Foreground Service setup

- Day 6: Polish & testing
  - Battery optimization
  - Error handling
  - UI (simple status indicator)

**Week 2: Session Manager (12-16 hours)**
- Days 1-2: Core server
  - FastAPI WebSocket server
  - Audio stream handling
  - VAD integration

- Days 3-4: STT/TTS integration
  - OpenAI Whisper provider
  - OpenAI TTS provider
  - Audio format conversion

- Day 5: Session management
  - Stop phrase detection
  - Session timeouts
  - State management

**Week 3: Integration & Testing (4-6 hours)**
- End-to-end testing
- Latency optimization
- Bug fixes

### Phase 2: LLM Integration (12-16 hours)

- Custom LLM provider interface
- OpenAI GPT-4 integration
- Context management
- Conversation history

### Phase 3: Memory & RAG (20-30 hours)

- AnythingLLM integration
- RAG pipeline
- Memory persistence
- Dad's note-taking feature

### Phase 4: Retrieval Augmentation (15-20 hours)

- Advanced RAG features
- Multi-source retrieval
- Context ranking

### Phase 5: n8n Automation (8-12 hours)

- n8n standalone setup
- Reminder workflows
- SMS/WhatsApp integration
- Safety escalations

### Phase 6: Hardening & Deployment (15-20 hours)

- Security hardening
- Error recovery
- Dad testing & tuning
- Documentation

**Total: 97-144 hours (~3-4.5 weeks full-time)**

---

## Success Criteria

### Phase 1 Complete When:

- ✅ Android app detects wake-word ("OK Nabu" via Vosk)
- ✅ Audio streams from phone → Session Manager
- ✅ OpenAI Whisper transcribes speech accurately
- ✅ OpenAI TTS responds with clear audio
- ✅ Audio plays back on phone
- ✅ VAD detects silence correctly (2 sec timeout)
- ✅ Stop phrases end session ("that's all")
- ✅ Battery usage acceptable (<10% per hour)
- ✅ Works reliably with Dad's slurred speech

### Overall Project Complete When:

- ✅ Dad can reliably use voice assistant (≥90% success rate)
- ✅ System handles Dad's common tasks (reminders, notes, calls)
- ✅ Battery lasts full day (8-12 hours)
- ✅ Latency acceptable (<3 seconds end-to-end)
- ✅ Privacy maintained (local processing where possible)
- ✅ Dad reports improved quality of life

---

## Comparison to Original HA Plan

| Aspect | With HA | Without HA (New) |
|--------|---------|------------------|
| **Development Time** | 112-162 hours | 97-144 hours |
| **STT Options** | Wyoming Whisper only | OpenAI/Deepgram/Local |
| **TTS Options** | Wyoming Piper/Google | OpenAI/ElevenLabs/Local |
| **Modular Providers** | ❌ Difficult | ✅ Easy to swap |
| **Smart Home Control** | ✅ Yes | ❌ No (not needed) |
| **Architecture Complexity** | High | Medium |
| **Maintenance Burden** | High (HA + custom) | Medium (custom only) |
| **Aligns with Dad's Needs** | Partial | ✅ Fully |

**Time Saved:** 15-18 hours
**Complexity Reduced:** Significantly simpler
**Flexibility Gained:** Full control over STT/TTS

---

## Next Steps

1. ✅ Architecture decision made (remove HA)
2. ⏳ Create Android app project (Kotlin + Android Studio)
3. ⏳ Implement WebSocket client
4. ⏳ Integrate Vosk wake-word detection
5. ⏳ Complete Session Manager implementation
6. ⏳ End-to-end testing

---

**Document Status:** Active
**Last Updated:** 2025-11-02
**Next Review:** After Phase 1 completion
