# Phase 1: UI Configuration Steps for Home Assistant (REVISED)
**Date:** 2025-11-01
**Status:** Ready to configure

## IMPORTANT ARCHITECTURE CLARIFICATION

**What this guide covers:**
- ✅ Adding Wyoming Protocol integration for **wake-word detection ONLY**
- ✅ Creating a minimal Assist Pipeline that triggers on "OK Nabu"

**What this guide does NOT cover:**
- ❌ OpenAI Conversation integration (NOT needed - only provides gpt-4o-mini LLM)
- ❌ Configuring STT/TTS in Home Assistant (Home Assistant has NO native OpenAI Whisper/TTS integrations)

## The Correct Architecture

```
┌─────────────────────────────────────────────┐
│  Samsung A05 Phone (HA Companion App)      │
│  - Captures audio                           │
│  - Sends to Session Manager                 │
└─────────────────────────────────────────────┘
                    ↓ audio stream
┌─────────────────────────────────────────────┐
│  Home Assistant                             │
│  - Wyoming openWakeWord (port 10400)        │
│  - Detects "OK Nabu" wake-word              │
│  - Triggers Session Manager                 │
└─────────────────────────────────────────────┘
                    ↓ wake event
┌─────────────────────────────────────────────┐
│  Session Manager (Python/FastAPI)          │
│  - Receives audio from phone                │
│  - Calls OpenAI Whisper API (STT)          │ ← Direct API call
│  - Processes with custom LLM (later)        │
│  - Calls OpenAI TTS API (TTS)              │ ← Direct API call
│  - Sends audio back to phone                │
└─────────────────────────────────────────────┘
```

**Key Points:**
1. Home Assistant is ONLY used for wake-word detection (Wyoming openWakeWord)
2. STT/TTS are handled by your Session Manager via direct OpenAI API calls
3. You do NOT need OpenAI Conversation integration (that's for gpt-4o-mini LLM only)

---

## Prerequisites Completed

- ✅ Wyoming openWakeWord container running (port 10400)
- ✅ OpenAI API key added to secrets.yaml (for Session Manager use)
- ✅ Home Assistant restarted and running
- ✅ Configuration.yaml cleaned up (no YAML integration configs)

---

## Step 1: Add Wyoming Protocol Integration

### 1.1 Open Home Assistant Web UI
- Navigate to: `http://localhost:8123`
- Log in as **Mike VCA** (admin account)

### 1.2 Go to Integrations
1. Click **Settings** (gear icon in left sidebar)
2. Click **Devices & Services**
3. Click **+ Add Integration** (bottom right, blue button)

### 1.3 Add Wyoming Integration
1. In the search box, type: **`wyoming`**
2. Click on **Wyoming Protocol** from the results
3. Configure the integration:
   - **Host:** `localhost` or `127.0.0.1`
   - **Port:** `10400`
4. Click **Submit**

### 1.4 Verify Wyoming Integration
- You should see a new integration card for **Wyoming Protocol**
- It should show **1 device** (the openWakeWord service)
- Status should be **Connected** or similar

**Expected Result:**
```
Wyoming Protocol
✓ Connected
1 device - openWakeWord
```

---

## Step 2: Create Minimal Assist Pipeline

### 2.1 Navigate to Voice Assistants
1. Click **Settings** (left sidebar)
2. Scroll down to **Voice Assistants**
3. Click **Voice Assistants**

### 2.2 Add New Assistant
1. Click **+ Add Assistant** (bottom right)

### 2.3 Configure "Dad VCA Pipeline"

**Basic Settings:**
- **Name:** `Dad VCA Pipeline`
- **Language:** Select **English** (try `en-NZ` if available, otherwise `en-US`)

**Conversation Agent:**
- Select **Home Assistant** (default)
- **DO NOT** add or select OpenAI Conversation
- This is just a placeholder - your Session Manager will handle actual conversation

**Wake Word:**
- Select **Wyoming** from the dropdown
- Should auto-detect the service at `localhost:10400`
- Wake word should show: **ok_nabu**
- If Wyoming doesn't appear, go back to Step 1 and verify integration is added

**Speech-to-Text:**
- Select **Home Assistant** (default placeholder)
- **Note:** This will NOT actually be used - your Session Manager calls OpenAI Whisper API directly
- We're setting it to satisfy the UI requirement, but audio processing bypasses this

**Text-to-Speech:**
- Select **Home Assistant** (default placeholder)
- **Note:** This will NOT actually be used - your Session Manager calls OpenAI TTS API directly
- Same as above - just a placeholder

**Why use placeholders?**
- Home Assistant Assist Pipeline requires these fields to be set
- But your Session Manager intercepts the audio stream after wake-word detection
- The actual STT/TTS happens in your Python code via OpenAI APIs

### 2.4 Save Pipeline
- Click **Create** or **Save**

### 2.5 Verify Pipeline
- You should see **Dad VCA Pipeline** in the list of assistants
- It should show:
  - Wake word: Wyoming (ok_nabu)
  - STT: Home Assistant (placeholder)
  - TTS: Home Assistant (placeholder)
  - Conversation: Home Assistant (placeholder)

---

## Step 3: Verify Wyoming Wake-Word Detection

### 3.1 Check Wyoming Container Logs
```bash
docker logs wyoming-openwakeword -f
```

**Expected output:**
```
INFO:root:Ready
INFO:wyoming_openwakeword:Server started on tcp://0.0.0.0:10400
```

### 3.2 Check Home Assistant Logs
```bash
docker logs homeassistant --tail 50 | grep -i wyoming
```

**Look for:**
```
INFO (MainThread) [homeassistant.components.wyoming] Connected to Wyoming service
```

---

## Step 4: Prepare for Phone Testing (Optional for now)

### 4.1 Install Home Assistant Companion App
On Samsung A05:
1. Open **Google Play Store**
2. Search: **`home assistant`**
3. Install: **Home Assistant Companion** (official app by Nabu Casa)

### 4.2 Configure Companion App
1. Open app
2. **Connect to Home Assistant:**
   - From Phase 0, you know your Windows IP
   - Enter URL: `http://<WINDOWS_IP>:8123`
   - Or scan QR code from HA Settings → Companion App
3. **Log in as Dad VCA** (limited user account)

### 4.3 Configure Assist in App
1. In app, go to **Settings** (⋮ menu)
2. Tap **Assist**
3. Select **Dad VCA Pipeline**

### 4.4 Test Wake Word (Basic Test Only)
1. Say: **"OK Nabu"**
2. Check if HA detects the wake-word

**At this stage:**
- Wake-word detection should work
- But full conversation won't work yet (Session Manager not built)

**Check Home Assistant logs for wake-word detection:**
```bash
docker logs homeassistant -f | grep wake
```

**Expected when wake-word detected:**
```
INFO (MainThread) [homeassistant.components.wake_word] Wake word detected: ok_nabu
INFO (MainThread) [homeassistant.components.assist_pipeline] Pipeline started
```

---

## What Happens Next: Building the Session Manager

After you've confirmed Wyoming wake-word detection is working, we'll build the Session Manager (Phase 1 Days 3-4):

### Session Manager Components

**1. Core Server (`session_manager/main.py`)**
- FastAPI WebSocket server
- Listens for audio streams from HA Companion App
- Connects to Home Assistant WebSocket API to receive wake-word events

**2. STT Provider (`session_manager/stt/providers/openai_whisper.py`)**
```python
from openai import OpenAI

class OpenAIWhisperProvider:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    async def transcribe(self, audio_bytes: bytes) -> str:
        # Direct API call to OpenAI Whisper
        response = self.client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="en"
        )
        return response.text
```

**3. TTS Provider (`session_manager/tts/providers/openai_tts.py`)**
```python
from openai import OpenAI

class OpenAITTSProvider:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    async def synthesize(self, text: str, voice: str = "nova") -> bytes:
        # Direct API call to OpenAI TTS
        response = self.client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text
        )
        return response.content
```

**4. Session Management (`session_manager/session.py`)**
- Voice Activity Detection (VAD) for silence timeout
- Stop phrase detection ("that's all", "stop listening")
- Session state management

**5. Home Assistant WebSocket Integration (`session_manager/ha_websocket.py`)**
- Connect to HA WebSocket API
- Subscribe to wake-word detection events
- Coordinate with audio stream processing

---

## Architecture Flow

**1. Wake-Word Detection (Now):**
```
User says "OK Nabu"
    ↓
Wyoming openWakeWord detects it (port 10400)
    ↓
Home Assistant triggers Assist Pipeline
    ↓
Wake-word event sent to Session Manager (via WebSocket)
```

**2. Audio Processing (After Session Manager is built):**
```
Session Manager receives wake-word event
    ↓
HA Companion App streams audio to Session Manager
    ↓
Session Manager calls OpenAI Whisper API (STT)
    ↓
Transcribed text: "What time is it?"
    ↓
Session Manager processes with custom LLM (Phase 2)
    ↓
Response text: "It's 3:45 PM"
    ↓
Session Manager calls OpenAI TTS API (TTS)
    ↓
Audio bytes sent back to phone
    ↓
Phone plays response
```

---

## Common Questions

### Q: Why not use OpenAI Conversation integration?
**A:** That integration only provides gpt-4o-mini as an LLM conversation agent. It does NOT provide STT or TTS. You want to use OpenAI's Whisper and TTS APIs, which are not available as Home Assistant integrations.

### Q: How does Session Manager get the audio?
**A:** The HA Companion App can stream audio to a custom WebSocket endpoint. Your Session Manager will provide this endpoint and receive the audio stream directly.

### Q: Why set placeholder STT/TTS in the Assist Pipeline?
**A:** Home Assistant requires these fields to be set when creating a pipeline. However, when your Session Manager intercepts the audio stream after wake-word detection, these placeholder values are never actually used.

### Q: Can I test STT/TTS now?
**A:** Not yet - you can only test wake-word detection. Full STT/TTS testing requires the Session Manager to be built (Phase 1 Days 3-4).

### Q: What if wake-word detection doesn't work?
**A:** Troubleshooting:
1. Check Wyoming container is running: `docker ps | grep wyoming`
2. Check container logs: `docker logs wyoming-openwakeword`
3. Verify port 10400 is listening: `ss -tuln | grep 10400`
4. Try restarting HA: `docker restart homeassistant`
5. Try different wake-word model (see troubleshooting section below)

---

## Troubleshooting

### Issue: Wyoming integration not found in HA

**Solution:**
1. Restart Home Assistant: `docker restart homeassistant`
2. Wait 30 seconds for full startup
3. Verify Wyoming container is running: `docker ps | grep wyoming`
4. Try using IP address instead of hostname: `127.0.0.1:10400`

### Issue: Wake-word not detecting

**Test wake-word container directly:**
```bash
# Check logs
docker logs wyoming-openwakeword -f

# Restart container
docker restart wyoming-openwakeword

# Wait for "Ready" message
```

**Try different wake-word model:**
```bash
# Stop and remove current container
docker stop wyoming-openwakeword
docker rm wyoming-openwakeword

# Try "hey_jarvis" model instead
docker run -d \
  --name wyoming-openwakeword \
  --restart unless-stopped \
  -p 10400:10400 \
  -v /home/indigo/my-project3/Dappva/wyoming-data/openwakeword:/data \
  rhasspy/wyoming-openwakeword:latest \
  --uri tcp://0.0.0.0:10400 \
  --preload-model 'hey_jarvis'

# Restart Home Assistant
docker restart homeassistant
```

**Available wake-word models:**
- `ok_nabu` - "OK Nabu" (default)
- `hey_jarvis` - "Hey Jarvis"
- `alexa` - "Alexa"
- See: https://github.com/dscripka/openWakeWord#pre-trained-models

### Issue: HA Companion App can't connect

**Check network connectivity:**
```bash
# From Phase 0, verify Windows IP and port forwarding
# Windows PowerShell (Administrator):
netsh interface portproxy show all

# Should show:
# Listen on 0.0.0.0:8123 → Connect to <WSL2_IP>:8123
```

**Verify from phone browser:**
- Open browser on Samsung A05
- Go to: `http://<WINDOWS_IP>:8123`
- Should see Home Assistant login page

---

## Success Criteria

Phase 1 wake-word setup is complete when:
- ✅ Wyoming Protocol integration added to Home Assistant
- ✅ Wyoming openWakeWord device shows as connected
- ✅ "Dad VCA Pipeline" created with Wyoming wake-word
- ✅ Wake-word "OK Nabu" triggers pipeline (visible in HA logs)
- ✅ HA Companion App installed and connected (optional for now)
- ✅ Ready to build Session Manager (Phase 1 Days 3-4)

---

## Next Steps

After confirming wake-word detection works:

**1. Build Session Manager Backend (12-16 hours)**
- Create directory structure
- Implement core modules (main.py, config.py, logger.py)
- Implement OpenAI Whisper STT provider
- Implement OpenAI TTS provider
- Implement HA WebSocket integration
- Add VAD and stop phrase detection

**2. End-to-End Testing (4-6 hours)**
- Test with Dad's voice
- Tune wake-word sensitivity
- Measure latency
- Document results

**Total remaining Phase 1 time:** ~16-22 hours

---

## Files Modified

- ✅ `/home/indigo/homeassistant/config/secrets.yaml` - OpenAI API key added
- ✅ `/home/indigo/homeassistant/config/configuration.yaml` - Cleaned up
- ✅ Home Assistant restarted

## Files to Create (Next)

- ⏳ `session_manager/` - Directory structure
- ⏳ `session_manager/main.py` - FastAPI server
- ⏳ `session_manager/stt/providers/openai_whisper.py` - STT provider
- ⏳ `session_manager/tts/providers/openai_tts.py` - TTS provider
- ⏳ `session_manager/ha_websocket.py` - HA integration
- ⏳ `session_manager/requirements.txt` - Dependencies

---

**Current Status:** Ready to configure Wyoming integration via Home Assistant UI

**Next:** Follow Steps 1-3 above to add Wyoming integration and create Assist Pipeline
