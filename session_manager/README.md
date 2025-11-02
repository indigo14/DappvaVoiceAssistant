# VCA Session Manager

Voice Conversational Assistant - Session Manager FastAPI Server
**Status**: Phase 1 Complete ✅

## Overview

The Session Manager is the core backend server for the VCA system. It provides:
- WebSocket-based audio streaming
- Voice Activity Detection (VAD) using webrtcvad
- Speech-to-Text via OpenAI Whisper API
- Text-to-Speech via OpenAI TTS API
- Session state management
- Stop phrase detection
- Modular STT/TTS provider architecture

## Features Implemented

✅ **Audio Streaming**: WebSocket endpoint for bidirectional audio streaming
✅ **Voice Activity Detection**: Automatic detection of speech/silence boundaries
✅ **STT Integration**: OpenAI Whisper API for speech recognition
✅ **TTS Integration**: OpenAI TTS API for speech synthesis (Nova voice)
✅ **Session Management**: Track multiple concurrent sessions with timeouts
✅ **Stop Phrases**: Natural language session ending ("that's all", "goodbye", etc.)
✅ **Modular Architecture**: Easy to swap STT/TTS providers
✅ **Configuration System**: YAML config + environment variables
✅ **Logging**: Colored console logging with file output

## Quick Start

### 1. Setup Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure

Create `.env` file with your OpenAI API key:

```bash
OPENAI_API_KEY=sk-proj-...
HA_ACCESS_TOKEN=your_ha_token_here
```

Edit `config.yaml` to customize settings (optional):
- Server host/port
- VAD parameters (silence threshold, aggressiveness)
- Stop phrases
- Session timeouts
- STT/TTS models

### 3. Run Server

```bash
source venv/bin/activate
python main.py
```

Server will start on `http://0.0.0.0:5000`

### 4. Test

```bash
# Test connection
python test_client.py test

# Test with audio file (must be 16kHz, mono, PCM16 WAV)
python test_client.py test_audio_16k.wav

# Generate test audio
python generate_test_audio.py "Your test phrase here"
```

## API Endpoints

### HTTP Endpoints

- `GET /` - Health check (simple)
- `GET /health` - Detailed health check with component status

### WebSocket Endpoint

- `WS /audio-stream` - Audio streaming endpoint

#### WebSocket Protocol

**Client → Server (JSON):**
```json
{"type": "session_start", "device_id": "device_123"}
```

**Client → Server (Binary):**
- Audio chunks: PCM16, 16kHz, mono, 30ms frames (960 bytes)

**Server → Client (JSON):**
```json
{"type": "session_started", "session_id": "uuid"}
{"type": "status", "state": "processing"}
{"type": "transcript", "text": "User's speech"}
{"type": "response_text", "text": "Assistant response"}
{"type": "session_ending", "reason": "stop_phrase", "matched_phrase": "goodbye"}
{"type": "error", "message": "Error description"}
```

**Server → Client (Binary):**
- Audio response: MP3 format, 24kHz

**Client → Server (JSON):**
```json
{"type": "session_end", "reason": "user_request"}
```

## Architecture

```
┌─────────────┐
│   Client    │ (Android App / Test Client)
│  (WebSocket)│
└──────┬──────┘
       │ Audio PCM16 16kHz
       │
┌──────▼───────────────────────────────────┐
│      Session Manager (FastAPI)           │
│                                           │
│  ┌────────────┐  ┌────────────────────┐  │
│  │ WebSocket  │  │  Session Manager   │  │
│  │  Handler   │──┤  (State tracking)  │  │
│  └────────────┘  └────────────────────┘  │
│         │                                 │
│  ┌──────▼──────┐                          │
│  │     VAD     │ (Voice Activity Detect)  │
│  └──────┬──────┘                          │
│         │ End of speech                   │
│  ┌──────▼──────┐                          │
│  │ STT Provider│ (OpenAI Whisper)         │
│  └──────┬──────┘                          │
│         │ Transcript                      │
│  ┌──────▼────────┐                        │
│  │ Stop Phrase   │                        │
│  │   Detector    │                        │
│  └──────┬────────┘                        │
│         │ (if not stop phrase)            │
│  ┌──────▼──────┐                          │
│  │LLM Provider │ (Phase 2: Not yet impl.) │
│  └──────┬──────┘                          │
│         │ Response text                   │
│  ┌──────▼──────┐                          │
│  │ TTS Provider│ (OpenAI TTS)             │
│  └──────┬──────┘                          │
│         │ Audio MP3                       │
└─────────┼────────────────────────────────┘
          │
     ┌────▼────┐
     │  Client │ (Plays audio)
     └─────────┘
```

## Configuration

### VAD Settings (config.yaml)

```yaml
session:
  vad:
    enabled: true
    silence_timeout: 2.0        # Seconds of silence before processing
    min_speech_duration: 0.5    # Minimum speech duration (seconds)
    sample_rate: 16000          # Audio sample rate (Hz)
    frame_duration: 30          # VAD frame duration (10, 20, or 30 ms)
    aggressiveness: 3           # VAD aggressiveness (0-3)
```

- **aggressiveness**: Higher = more aggressive in filtering out non-speech
  - 0 = Least aggressive (detects more as speech)
  - 3 = Most aggressive (only detects clear speech)
- **silence_timeout**: How long to wait for silence before processing transcript

### Stop Phrases

```yaml
session:
  stop_phrases:
    - "that's all"
    - "stop listening"
    - "thank you goodbye"
    - "goodbye"
```

Add any natural phrases that should end the session.

### Provider Selection

```yaml
stt_provider: "openai_whisper"  # Options: openai_whisper, deepgram, local_whisper
tts_provider: "openai_tts"      # Options: openai_tts, elevenlabs, local_piper
```

## Project Structure

```
session_manager/
├── main.py                     # FastAPI server entry point
├── config.yaml                 # Main configuration
├── .env                        # Environment variables (API keys)
├── requirements.txt            # Python dependencies
│
├── config/
│   └── settings.py             # Configuration loader
│
├── utils/
│   └── logger.py               # Logging utility
│
├── stt/
│   ├── base.py                 # STT provider base class
│   └── providers/
│       └── openai_whisper.py   # OpenAI Whisper implementation
│
├── tts/
│   ├── base.py                 # TTS provider base class
│   └── providers/
│       └── openai_tts.py       # OpenAI TTS implementation
│
├── session/
│   ├── manager.py              # Session state management
│   ├── vad.py                  # Voice Activity Detection
│   └── stop_phrases.py         # Stop phrase detection
│
├── test_client.py              # WebSocket test client
├── generate_test_audio.py      # Test audio generator
└── README.md                   # This file
```

## Audio Format Requirements

### Input (Client → Server)
- **Format**: Raw PCM16 (signed 16-bit)
- **Sample Rate**: 16000 Hz (16kHz)
- **Channels**: Mono (1 channel)
- **Frame Size**: 960 bytes (30ms @ 16kHz PCM16)
- **Byte Order**: Little-endian

### Output (Server → Client)
- **Format**: MP3
- **Sample Rate**: 24000 Hz (24kHz)
- **Channels**: Mono
- **Bitrate**: 160 kbps

## Testing

### Test Connection

```bash
python test_client.py test
```

### Generate Test Audio

```bash
# Default test phrase
python generate_test_audio.py

# Custom phrase
python generate_test_audio.py "Hello, how are you?"

# Stop phrase test
python generate_test_audio.py "That's all, goodbye"
```

### Test Full Pipeline

```bash
python test_client.py test_audio_16k.wav
```

Expected output:
```
Connecting to ws://localhost:5000/audio-stream...
Connected!
Sent: {'type': 'session_start', 'device_id': 'test_client'}
Received: {"type":"session_started","session_id":"..."}

Reading audio file: test_audio_16k.wav
Audio format: 1 channel(s), 2 bytes/sample, 16000 Hz
Sending audio in 960-byte chunks (30ms frames)...
Sent 102 audio chunks (3060ms total)
Sending 2.5 seconds of silence to trigger VAD...

[STATUS] processing
[TRANSCRIPT] Hello, how are you?
[RESPONSE] You said: Hello, how are you?
[AUDIO RESPONSE] Received 88800 bytes
Saved to: test_response.mp3
[STATUS] listening
```

## Next Steps (Phase 2)

- [ ] **LLM Integration**: Add conversation intelligence (Anthropic Claude API)
- [ ] **Conversation History**: Track multi-turn conversations
- [ ] **Context Management**: Pass conversation context to LLM
- [ ] **Home Assistant Integration**: Optional smart home control
- [ ] **Android App**: Custom app with Vosk wake-word detection
- [ ] **Wake-word Integration**: Trigger sessions automatically

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 5000
lsof -i :5000

# Kill process
kill -9 <PID>
```

### OpenAI API Key Issues

```bash
# Verify .env file exists
cat .env

# Check API key is loaded
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('OPENAI_API_KEY')[:20])"
```

### VAD Not Detecting End of Speech

- Ensure audio file has 2+ seconds of silence at the end
- Try reducing `silence_timeout` in config.yaml (default: 2.0s)
- Try reducing `aggressiveness` (default: 3, try 2 or 1)

### WebSocket Connection Refused

- Check server is running: `curl http://localhost:5000/health`
- Check firewall settings
- Verify port 5000 is accessible

## Development

### Add New STT Provider

1. Create `stt/providers/your_provider.py`
2. Inherit from `STTProvider` base class
3. Implement `transcribe()` method
4. Return `TranscriptionResult` object
5. Update `config.yaml`: `stt_provider: "your_provider"`

### Add New TTS Provider

1. Create `tts/providers/your_provider.py`
2. Inherit from `TTSProvider` base class
3. Implement `synthesize()` method
4. Return `TTSResult` object
5. Update `config.yaml`: `tts_provider: "your_provider"`

## License

MIT

## Support

For issues, questions, or contributions, contact the project maintainer.

---

**VCA 1.0 - Phase 1 Complete** ✅
Session Manager operational and tested.
Ready for Phase 2: LLM integration and Android app development.
