# Android App Development - Handover Brief
**VCA 1.0 Project - New Session Quick Start**
**Date**: 2025-11-02
**Session**: 5 → 6 Handover

---

## 🎯 Your Mission

Build the Android app that connects to the **already-completed Session Manager backend**. The backend is 100% operational and tested. You just need to build the mobile client.

**Estimated Time**: 16-24 hours
**Target Device**: Samsung Galaxy A05 (Dad's phone, same as yours)
**Status**: Ready to begin immediately

---

## ✅ What's Already Complete (Don't rebuild this!)

### Session Manager Backend (100% Done)
- **Location**: `/home/indigo/my-project3/Dappva/session_manager/`
- **Status**: 🟢 Running on port 5000 (Process ID: 203813)
- **Tested**: End-to-end with audio files ✅
- **Components Working**:
  - WebSocket server (FastAPI)
  - Voice Activity Detection (VAD)
  - OpenAI Whisper STT
  - OpenAI TTS (Nova voice)
  - Stop phrase detection
  - Session state management

**You can test it right now**:
```bash
cd /home/indigo/my-project3/Dappva/session_manager
python test_client.py test  # Test connection
```

**Health check**:
```bash
curl http://localhost:5000/health
```

---

## 🔨 What You Need to Build

### Android App (0% Done - Your Task)
**All code is provided** in [android-app-development-guide.md](android-app-development-guide.md)

**6 Modules to Implement**:
1. ✏️ **WebSocketClient.kt** - Connect to Session Manager
2. ✏️ **AudioRecorder.kt** - Record 16kHz PCM16 audio
3. ✏️ **WakeWordDetector.kt** - Vosk integration ("OK Nabu")
4. ✏️ **AudioPlayer.kt** - Play MP3 responses
5. ✏️ **VoiceAssistantService.kt** - Foreground service (always-on)
6. ✏️ **MainActivity.kt** - UI and permissions

**What's provided for you**:
- Complete Kotlin code for all 6 modules
- Full Gradle configuration
- AndroidManifest.xml template
- Dependencies list (OkHttp, Vosk, Coroutines)
- Configuration examples

---

## 📋 Quick Start Checklist

### Step 1: Read Documentation (65 minutes)
Read these files **in order**:

1. **[ARCHITECTURE-REVISED-NO-HA.md](ARCHITECTURE-REVISED-NO-HA.md)** (15 min)
   - System overview
   - Why Home Assistant was removed
   - Complete data flow walkthrough

2. **[android-app-development-guide.md](android-app-development-guide.md)** (30 min)
   - **THIS IS YOUR MAIN GUIDE**
   - Step-by-step implementation
   - All code provided

3. **[phase-1-completion-status.md](phase-1-completion-status.md)** (10 min)
   - Current project status
   - What's tested and working
   - Server configuration

4. **[session_manager/README.md](session_manager/README.md)** (10 min)
   - WebSocket protocol details
   - Audio format specifications
   - API endpoints

### Step 2: Verify Backend is Running (5 minutes)
```bash
# Check Session Manager health
curl http://localhost:5000/health

# Should return:
# {"status":"healthy","components":{"stt":true,"tts":true,"vad":true,"session_manager":true},"active_sessions":0}
```

If not running:
```bash
cd /home/indigo/my-project3/Dappva/session_manager
source venv/bin/activate
python main.py
```

### Step 3: Setup Android Studio (30 minutes)
- Install Android Studio (or verify installed)
- Install required SDKs (API 24-35)
- Setup JDK 17+
- Create new Kotlin project: "DappVA" or "VoiceAssistant"

### Step 4: Follow Implementation Guide (14-20 hours)
Open [android-app-development-guide.md](android-app-development-guide.md) and implement:
1. Gradle dependencies (5 min)
2. AndroidManifest permissions (5 min)
3. WebSocketClient module (1-2 hours)
4. AudioRecorder module (2-3 hours)
5. WakeWordDetector module (3-4 hours - includes Vosk model download)
6. AudioPlayer module (1-2 hours)
7. VoiceAssistantService module (3-4 hours)
8. MainActivity module (2-3 hours)

### Step 5: Configure Network (10 minutes)
1. Find your PC's IP address:
   ```bash
   # On Windows (PowerShell)
   ipconfig | findstr IPv4
   ```

2. Update Android app config (in `MainActivity.kt`):
   ```kotlin
   private val SERVER_URL = "ws://[YOUR_PC_IP]:5000/audio-stream"
   ```

3. Ensure WSL2 port forwarding is active (should already be configured):
   ```powershell
   # On Windows (Administrator PowerShell)
   netsh interface portproxy show v4tov4
   # Should show: 5000 → 172.20.177.188:5000
   ```

### Step 6: Test on Samsung A05 (1-2 hours)
1. Enable Developer Mode on phone
2. Enable USB Debugging
3. Connect phone via USB
4. Build and deploy app
5. Grant permissions (microphone, notifications)
6. Test wake-word: "OK Nabu, what time is it?"
7. Verify audio response plays

---

## 🔑 Critical Technical Details

### Network Configuration
- **Session Manager**: Running at `ws://[PC_IP]:5000/audio-stream`
- **WSL2 IP**: 172.20.177.188 (internal)
- **Port Forwarding**: Windows port 5000 → WSL2:5000 (already configured)
- **From Phone**: Use PC's LAN IP address (find with `ipconfig` on Windows)

### Audio Format Specifications
**Android App → Session Manager (Upstream)**:
- Format: Raw PCM16 (signed 16-bit, little-endian)
- Sample Rate: 16000 Hz (16kHz)
- Channels: Mono (1 channel)
- Frame Size: 960 bytes (30ms chunks)
- Use: `AudioRecord` with `AudioFormat.ENCODING_PCM_16BIT`

**Session Manager → Android App (Downstream)**:
- Format: MP3
- Sample Rate: 24000 Hz (24kHz)
- Channels: Mono
- Bitrate: 160 kbps
- Use: `MediaPlayer` to play MP3 bytes

### WebSocket Protocol

**1. Client Initiates Session:**
```json
→ {"type": "session_start", "device_id": "samsung_a05"}
← {"type": "session_started", "session_id": "uuid"}
```

**2. Client Streams Audio:**
```
→ [Binary: PCM16 chunks, 960 bytes each, 30ms intervals]
```

**3. Server Detects End of Speech (VAD):**
```json
← {"type": "status", "state": "processing"}
```

**4. Server Transcribes (STT):**
```json
← {"type": "transcript", "text": "What time is it?"}
```

**5. Server Generates Response (LLM - Phase 2):**
```json
← {"type": "response_text", "text": "It's 3:45 PM"}
```

**6. Server Synthesizes Speech (TTS):**
```
← [Binary: MP3 audio data]
```

**7. Server Ready for Next Input:**
```json
← {"type": "status", "state": "listening"}
```

**8. Client Ends Session:**
```json
→ {"type": "session_end", "reason": "user_request"}
```

### Vosk Wake-Word Model
- **Model**: vosk-model-small-en-us-0.15
- **Size**: ~40 MB
- **Download**: https://alphacephei.com/vosk/models
- **Location**: Put in `app/src/main/assets/vosk-model-small-en-us-0.15/`
- **Wake Phrases**: "ok nabu", "hey jarvis" (configurable in code)

---

## 🚨 Known Issues & Limitations

### Current Limitations (Phase 1)
1. **No LLM Yet**: Server currently echoes "You said: [transcript]"
   - Phase 2 will add Anthropic Claude API for intelligent responses
   - This doesn't affect Android app development

2. **Dad's Slurred Speech**: STT accuracy unknown with Dad's speech patterns
   - Architecture is modular - can swap STT providers easily
   - Will need testing with Dad to tune

3. **Network Dependency**: Requires PC and phone on same LAN
   - 95% uptime requirement (PC must be on)
   - Future: Could add fallback to cloud server

### Troubleshooting Resources
- Backend issues: [session_manager/README.md](session_manager/README.md#troubleshooting)
- Android issues: [android-app-development-guide.md](android-app-development-guide.md) (bottom section)
- Architecture questions: [ARCHITECTURE-REVISED-NO-HA.md](ARCHITECTURE-REVISED-NO-HA.md)

---

## 📊 Project Context

### Why Home Assistant Was Removed
- **Original Plan**: Use HA Companion App for voice input
- **Discovery**: HA Companion App cannot stream audio to custom endpoints
- **Impact**: Would only send transcript, losing OpenAI Whisper API benefit
- **Decision**: Build custom Android app with full audio streaming control
- **Result**: Same development time, more flexibility, simpler architecture

### Architecture Summary
```
┌─────────────────────────────────────────────────────────┐
│                     Android App                          │
│  (Vosk Wake-Word → Audio Recording → WebSocket)         │
└───────────────────────┬─────────────────────────────────┘
                        │ PCM16 16kHz Audio
                        ↓
┌─────────────────────────────────────────────────────────┐
│              Session Manager (PC - FastAPI)              │
│  VAD → OpenAI Whisper → LLM (Phase 2) → OpenAI TTS      │
└───────────────────────┬─────────────────────────────────┘
                        │ MP3 Audio
                        ↓
┌─────────────────────────────────────────────────────────┐
│                     Android App                          │
│              (Audio Playback → UI Update)                │
└─────────────────────────────────────────────────────────┘
```

### Development Phases
- ✅ **Phase 0**: Environment setup (Docker, Python, Node, API keys) - 100%
- ✅ **Phase 1**: Session Manager backend - 100%
- 🔄 **Phase 2a**: Android app - **YOUR TASK** (0%)
- ⏳ **Phase 2b**: LLM integration (Anthropic Claude) - 0%
- ⏳ **Phase 3**: Memory/context system - 0%
- ⏳ **Phase 4**: Advanced features - 0%

---

## 🎯 Success Criteria for Your Work

### Minimum Viable Product (MVP)
- [ ] Android app connects to Session Manager via WebSocket
- [ ] Wake-word "OK Nabu" triggers session start
- [ ] Audio recording streams to server (PCM16 16kHz)
- [ ] Transcript displays in app UI
- [ ] TTS response plays through phone speaker
- [ ] Stop phrase "goodbye" ends session
- [ ] App runs as Foreground Service (always-on)

### Testing Checklist
- [ ] Wake-word detection works (multiple attempts)
- [ ] Full conversation flow works (speak → response → speak)
- [ ] Audio quality is clear (no distortion)
- [ ] Network reconnection works (if WiFi drops)
- [ ] Battery usage is acceptable (monitor over 1 hour)
- [ ] Phone remains responsive (no UI freezing)

---

## 📚 Essential File Reference

### Must-Read Files (In Order)
1. [ARCHITECTURE-REVISED-NO-HA.md](ARCHITECTURE-REVISED-NO-HA.md) - System architecture
2. [android-app-development-guide.md](android-app-development-guide.md) - **YOUR MAIN GUIDE**
3. [phase-1-completion-status.md](phase-1-completion-status.md) - Current status
4. [session_manager/README.md](session_manager/README.md) - Backend API docs

### Reference Files (As Needed)
- [CHANGELOG.md](CHANGELOG.md) - Full project history
- [SESSION-5-SUMMARY.md](SESSION-5-SUMMARY.md) - Latest session recap
- [phase-0-completion-status.md](phase-0-completion-status.md) - Infrastructure setup
- [dad_profile_pre_filled_voice_assistant.md](dad_profile_pre_filled_voice_assistant.md) - User requirements

### Test & Debug Files
- [session_manager/test_client.py](session_manager/test_client.py) - Backend test tool
- [session_manager/generate_test_audio.py](session_manager/generate_test_audio.py) - Audio generator

---

## 🚀 Ready to Start?

### Your First Actions (Next 5 Minutes)
1. Read [ARCHITECTURE-REVISED-NO-HA.md](ARCHITECTURE-REVISED-NO-HA.md) (15 min)
2. Verify backend health: `curl http://localhost:5000/health`
3. Open [android-app-development-guide.md](android-app-development-guide.md)
4. Start with "Step 1: Project Setup"

### If You Get Stuck
1. Check troubleshooting section in android-app-development-guide.md
2. Verify Session Manager is running (curl health endpoint)
3. Check network connectivity (ping PC from phone)
4. Review WebSocket protocol in session_manager/README.md
5. Check CHANGELOG.md for decisions and rationale

### Key Contacts / Resources
- **OpenAI API Key**: In `/home/indigo/my-project3/Dappva/session_manager/.env`
- **Server Config**: `/home/indigo/my-project3/Dappva/session_manager/config.yaml`
- **Vosk Models**: https://alphacephei.com/vosk/models
- **OkHttp Docs**: https://square.github.io/okhttp/
- **Android AudioRecord**: https://developer.android.com/reference/android/media/AudioRecord

---

## 📞 Handover Notes

### What the Previous Session Accomplished
- Implemented complete Session Manager backend (9 hours)
- Tested end-to-end with audio files (all tests passed)
- Created comprehensive documentation
- Verified OpenAI Whisper STT working (~4s latency)
- Verified OpenAI TTS working (~3s latency)
- Confirmed VAD detecting speech boundaries correctly

### What Was Deliberately Deferred
- LLM integration (Phase 2b) - Will add Anthropic Claude API after Android app works
- Home Assistant cleanup - Containers still running, can stop anytime
- Advanced features (memory, context, smart home) - Phase 3+

### Critical Decisions Made
1. **Removed Home Assistant** - HA Companion App cannot stream raw audio
2. **Chose Vosk for wake-word** - Local processing, free, works offline
3. **OpenAI APIs for STT/TTS** - Quick MVP, will optimize to local models later
4. **Modular provider architecture** - Easy to swap STT models for Dad's speech

### Current System State
- ✅ Session Manager running on port 5000
- ✅ All dependencies installed (venv at session_manager/venv/)
- ✅ Configuration files ready (.env, config.yaml)
- ✅ Test tools available and working
- ✅ WSL2 port forwarding configured
- ✅ Network tested from Samsung A05

---

**🎉 Everything is ready for you to start building the Android app! 🎉**

Follow [android-app-development-guide.md](android-app-development-guide.md) and you'll have a working voice assistant in 16-24 hours.

**Good luck!** 🚀
