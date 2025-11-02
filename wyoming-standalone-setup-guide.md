# Wyoming Standalone Container Setup Guide
**VCA 1.0 - Phase 1 (Revised)**
**Date:** 2025-11-01

## Background

Home Assistant Container (which we installed in Phase 0) does NOT support add-ons. Add-ons require Home Assistant OS or Supervised installation.

**Solution:** Run Wyoming services as standalone Docker containers alongside Home Assistant. They communicate via Wyoming Protocol (WebSocket-based), providing the same functionality as add-ons.

## Wyoming Protocol Overview

Wyoming is an open protocol for voice pipelines. It uses WebSocket connections for:
- Wake-word detection
- Speech-to-text (STT)
- Text-to-speech (TTS)
- Audio streaming

**Official Wyoming containers:**
- `rhasspy/wyoming-openwakeword` - Wake-word detection
- `rhasspy/wyoming-whisper` - Local Whisper STT
- `rhasspy/wyoming-piper` - Local Piper TTS

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                Samsung A05 Phone                        │
│                                                          │
│  HA Companion App → Audio Stream                       │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              WSL2 Docker Containers                     │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │  Wyoming openWakeWord Container                │    │
│  │  Port: 10400                                    │    │
│  │  Model: "ok_nabu" or "hey_jarvis"              │    │
│  └────────────────────────────────────────────────┘    │
│                          │ Wyoming Protocol             │
│                          ▼                               │
│  ┌────────────────────────────────────────────────┐    │
│  │  Home Assistant Container                       │    │
│  │  Port: 8123                                     │    │
│  │  Assist Pipeline connects to Wyoming           │    │
│  └────────────────────────────────────────────────┘    │
│                          │                               │
│                          ▼                               │
│  ┌────────────────────────────────────────────────┐    │
│  │  Session Manager (Python FastAPI)              │    │
│  │  Port: 5000                                     │    │
│  │  Receives transcripts from HA WebSocket        │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  Optional (Phase 3+):                                   │
│  ┌─────────────────┐  ┌──────────────────┐            │
│  │ Wyoming Whisper │  │  Wyoming Piper   │            │
│  │ Port: 10300     │  │  Port: 10200     │            │
│  │ Local STT       │  │  Local TTS       │            │
│  └─────────────────┘  └──────────────────┘            │
└─────────────────────────────────────────────────────────┘
```

## Installation Steps

### Prerequisites

- ✅ Docker installed and running (from Phase 0)
- ✅ Home Assistant Container running (from Phase 0)
- ✅ Network connectivity verified (from Phase 0)

### Step 1: Create Wyoming Data Directory

Wyoming containers need persistent storage for downloaded models.

```bash
cd /home/indigo/my-project3/Dappva
mkdir -p wyoming-data/openwakeword
mkdir -p wyoming-data/whisper
mkdir -p wyoming-data/piper
```

**Verify:**
```bash
ls -la wyoming-data/
# Should show: openwakeword, whisper, piper directories
```

### Step 2: Pull Wyoming openWakeWord Image

```bash
docker pull rhasspy/wyoming-openwakeword:latest
```

**Expected output:**
```
latest: Pulling from rhasspy/wyoming-openwakeword
...
Status: Downloaded newer image for rhasspy/wyoming-openwakeword:latest
```

### Step 3: Run Wyoming openWakeWord Container

```bash
docker run -d \
  --name wyoming-openwakeword \
  --restart unless-stopped \
  -p 10400:10400 \
  -v /home/indigo/my-project3/Dappva/wyoming-data/openwakeword:/data \
  rhasspy/wyoming-openwakeword:latest \
  --uri tcp://0.0.0.0:10400 \
  --preload-model 'ok_nabu'
```

**Command breakdown:**
- `--name wyoming-openwakeword` - Container name for easy reference
- `--restart unless-stopped` - Auto-restart on PC boot
- `-p 10400:10400` - Expose port 10400 (Wyoming Protocol)
- `-v ...:/data` - Mount data directory for model storage
- `--uri tcp://0.0.0.0:10400` - Listen on all interfaces
- `--preload-model 'ok_nabu'` - Load "OK Nabu" wake-word model

**Alternative wake-word models:**
```bash
# To use "Hey Jarvis" instead:
docker run -d \
  --name wyoming-openwakeword \
  --restart unless-stopped \
  -p 10400:10400 \
  -v /home/indigo/my-project3/Dappva/wyoming-data/openwakeword:/data \
  rhasspy/wyoming-openwakeword:latest \
  --uri tcp://0.0.0.0:10400 \
  --preload-model 'hey_jarvis'

# Available models: ok_nabu, hey_jarvis, alexa, and more
# See: https://github.com/dscripka/openWakeWord#pre-trained-models
```

### Step 4: Verify Container is Running

```bash
# Check container status
docker ps | grep openwakeword
```

**Expected output:**
```
CONTAINER ID   IMAGE                                  STATUS         PORTS                     NAMES
abc123...      rhasspy/wyoming-openwakeword:latest   Up 10 seconds  0.0.0.0:10400->10400/tcp  wyoming-openwakeword
```

**Check logs:**
```bash
docker logs wyoming-openwakeword
```

**Expected log output:**
```
INFO:wyoming_openwakeword:Loading model: ok_nabu
INFO:wyoming_openwakeword:Model loaded successfully
INFO:wyoming_openwakeword:Server started on tcp://0.0.0.0:10400
INFO:wyoming_openwakeword:Ready
```

**If you see "Ready"**: ✅ Wake-word detection is running!

### Step 5: Test Wyoming Protocol Connection

```bash
# Test if Wyoming service is responding
curl -v http://localhost:10400
```

**Expected:** Connection successful (may show Wyoming protocol headers)

### Step 6: Configure Home Assistant

Edit Home Assistant configuration file:

```bash
# Open configuration.yaml
nano /home/indigo/homeassistant/config/configuration.yaml
```

**Add Wyoming wake-word configuration:**

```yaml
# Wyoming Wake Word Integration
wake_word:
  - platform: wyoming
    host: localhost
    port: 10400
```

**Save and exit** (Ctrl+X, Y, Enter)

### Step 7: Restart Home Assistant

```bash
# Restart HA to load new configuration
docker restart homeassistant

# Wait for HA to start (~30 seconds)
sleep 30

# Check HA logs
docker logs homeassistant --tail 50
```

**Look for in logs:**
```
INFO (MainThread) [homeassistant.setup] Setting up wake_word
INFO (MainThread) [homeassistant.components.wyoming] Connected to Wyoming service at localhost:10400
```

**If you see "Connected to Wyoming service"**: ✅ Home Assistant can communicate with wake-word service!

### Step 8: Create Assist Pipeline in Home Assistant UI

1. **Open Home Assistant:** `http://localhost:8123`

2. **Navigate to Settings → Voice Assistants**

3. **Click "Add Assistant"**

4. **Configure "Dad VCA Pipeline":**
   - **Name:** `Dad VCA Pipeline`
   - **Language:** English (en-US or en-NZ if available)
   - **Conversation agent:** Home Assistant (default)
   - **Wake word:**
     - Select **"Wyoming"** from dropdown
     - It should auto-detect `localhost:10400`
     - Wake word: `ok_nabu` (or whatever model you loaded)
   - **Speech-to-text:**
     - For Phase 1: Select "Home Assistant Cloud" or "OpenAI Whisper"
     - (We'll add OpenAI API key if using OpenAI)
   - **Text-to-speech:**
     - For Phase 1: Select "Home Assistant Cloud" or "OpenAI TTS"

5. **Click "Save"**

### Step 9: Configure OpenAI API for STT/TTS (If Using OpenAI)

**Edit secrets.yaml:**
```bash
nano /home/indigo/homeassistant/config/secrets.yaml
```

**Add OpenAI API key:**
```yaml
openai_api_key: "sk-proj-YOUR_OPENAI_API_KEY_HERE"
```

**Edit configuration.yaml:**
```bash
nano /home/indigo/homeassistant/config/configuration.yaml
```

**Add OpenAI integrations:**
```yaml
# OpenAI Speech-to-Text
stt:
  - platform: openai
    api_key: !secret openai_api_key
    model: whisper-1

# OpenAI Text-to-Speech
tts:
  - platform: openai_tts
    api_key: !secret openai_api_key
    model: tts-1
    voice: nova
```

**Restart HA:**
```bash
docker restart homeassistant
```

### Step 10: Test Wake-Word Detection

**From HA Companion App (Samsung A05):**

1. Open HA Companion App
2. Go to Settings → Assist
3. Select "Dad VCA Pipeline"
4. **Say the wake word:** "OK Nabu" (or "Hey Jarvis")
5. Watch for "Listening..." indicator

**Check Home Assistant logs:**
```bash
docker logs homeassistant -f | grep wake
```

**Expected log when wake-word detected:**
```
INFO (MainThread) [homeassistant.components.wake_word] Wake word detected: ok_nabu
INFO (MainThread) [homeassistant.components.assist_pipeline] Pipeline started
```

**If wake-word detected**: ✅ Phase 1 wake-word setup complete!

## Optional: Install Wyoming Whisper and Piper (Phase 3 Prep)

These are optional for Phase 1 (using OpenAI API). Install now for Phase 3+ local processing.

### Wyoming Whisper (Local STT)

```bash
# Pull image
docker pull rhasspy/wyoming-whisper:latest

# Run container (will download ~1GB model on first start)
docker run -d \
  --name wyoming-whisper \
  --restart unless-stopped \
  --gpus all \
  -p 10300:10300 \
  -v /home/indigo/my-project3/Dappva/wyoming-data/whisper:/data \
  rhasspy/wyoming-whisper:latest \
  --model small \
  --language en \
  --uri tcp://0.0.0.0:10300

# Check logs
docker logs wyoming-whisper
```

**Note:** `--gpus all` enables GTX 970 GPU acceleration for faster transcription.

### Wyoming Piper (Local TTS)

```bash
# Pull image
docker pull rhasspy/wyoming-piper:latest

# Run container
docker run -d \
  --name wyoming-piper \
  --restart unless-stopped \
  -p 10200:10200 \
  -v /home/indigo/my-project3/Dappva/wyoming-data/piper:/data \
  rhasspy/wyoming-piper:latest \
  --voice en_US-lessac-medium \
  --uri tcp://0.0.0.0:10200

# Check logs
docker logs wyoming-piper
```

**When to enable (Phase 3+):**

Update Assist pipeline in HA UI:
- **STT:** Change to "Wyoming" (localhost:10300)
- **TTS:** Change to "Wyoming" (localhost:10200)

This switches from cloud (OpenAI) to local processing on your GTX 970.

## Container Management

### View Running Containers

```bash
docker ps | grep wyoming
```

**Expected output:**
```
wyoming-openwakeword   Running   0.0.0.0:10400->10400/tcp
wyoming-whisper        Running   0.0.0.0:10300->10300/tcp  (if installed)
wyoming-piper          Running   0.0.0.0:10200->10200/tcp  (if installed)
```

### View Container Logs

```bash
# openWakeWord logs
docker logs wyoming-openwakeword -f

# Whisper logs
docker logs wyoming-whisper -f

# Piper logs
docker logs wyoming-piper -f
```

### Stop/Start/Restart Containers

```bash
# Stop
docker stop wyoming-openwakeword

# Start
docker start wyoming-openwakeword

# Restart
docker restart wyoming-openwakeword

# Remove (keeps data in volumes)
docker rm wyoming-openwakeword
```

### Update Containers

```bash
# Pull latest image
docker pull rhasspy/wyoming-openwakeword:latest

# Stop and remove old container
docker stop wyoming-openwakeword
docker rm wyoming-openwakeword

# Run new container (same command as Step 3)
docker run -d \
  --name wyoming-openwakeword \
  --restart unless-stopped \
  -p 10400:10400 \
  -v /home/indigo/my-project3/Dappva/wyoming-data/openwakeword:/data \
  rhasspy/wyoming-openwakeword:latest \
  --uri tcp://0.0.0.0:10400 \
  --preload-model 'ok_nabu'
```

## Troubleshooting

### Issue: Container won't start

**Check logs:**
```bash
docker logs wyoming-openwakeword
```

**Common causes:**
- Port 10400 already in use: `lsof -i :10400`
- Insufficient permissions: Check data directory ownership
- Out of memory: `docker stats wyoming-openwakeword`

**Solution:**
```bash
# Kill process using port
sudo kill $(sudo lsof -t -i:10400)

# Or use different port
docker run ... -p 10401:10400 ...
# Then update HA config to use port 10401
```

### Issue: Wake-word not detected

**Test wake-word container directly:**
```bash
# Check if service is responding
curl http://localhost:10400
```

**Try different wake-word model:**
```bash
# Stop current container
docker stop wyoming-openwakeword
docker rm wyoming-openwakeword

# Try hey_jarvis model
docker run -d \
  --name wyoming-openwakeword \
  --restart unless-stopped \
  -p 10400:10400 \
  -v /home/indigo/my-project3/Dappva/wyoming-data/openwakeword:/data \
  rhasspy/wyoming-openwakeword:latest \
  --uri tcp://0.0.0.0:10400 \
  --preload-model 'hey_jarvis'
```

**Adjust sensitivity:**

Edit container command to add `--threshold`:
```bash
docker run -d \
  --name wyoming-openwakeword \
  --restart unless-stopped \
  -p 10400:10400 \
  -v /home/indigo/my-project3/Dappva/wyoming-data/openwakeword:/data \
  rhasspy/wyoming-openwakeword:latest \
  --uri tcp://0.0.0.0:10400 \
  --preload-model 'ok_nabu' \
  --threshold 0.5  # Lower = more sensitive (0.0-1.0)
```

### Issue: HA can't connect to Wyoming service

**Check HA configuration:**
```yaml
wake_word:
  - platform: wyoming
    host: localhost  # Try 127.0.0.1 if localhost doesn't work
    port: 10400
```

**Restart Home Assistant:**
```bash
docker restart homeassistant
```

**Check both containers are on same network:**
```bash
docker network inspect bridge
```

### Issue: GPU not available for Whisper

**Verify NVIDIA Docker runtime:**
```bash
# Check if nvidia-docker is installed
nvidia-smi

# Install nvidia-container-toolkit if needed
# (Already have nvidia-smi working from Phase 0)
```

**Run Whisper without GPU (slower, CPU-only):**
```bash
docker run -d \
  --name wyoming-whisper \
  --restart unless-stopped \
  -p 10300:10300 \
  -v /home/indigo/my-project3/Dappva/wyoming-data/whisper:/data \
  rhasspy/wyoming-whisper:latest \
  --model small \
  --language en \
  --uri tcp://0.0.0.0:10300
  # No --gpus flag
```

## Testing with Dad's Voice

### Phase 1 Testing Checklist

- [ ] openWakeWord container running
- [ ] HA connected to Wyoming service
- [ ] Assist pipeline created
- [ ] HA Companion App configured
- [ ] Wake-word triggers from phone
- [ ] Dad can say wake-word successfully
- [ ] Wake-word works with Dad's NZ accent
- [ ] Latency acceptable (<2 seconds)

### Collect Test Data

```bash
# Monitor wake-word detections in real-time
docker logs wyoming-openwakeword -f

# Note successful detections vs misses
# Test different:
# - Voice volumes
# - Background noise levels
# - Speaking speeds
# - NZ accent variations
```

### Wake-Word Model Comparison

Test different models with Dad's voice:

| Model | Wake Phrase | Test Result | Notes |
|-------|-------------|-------------|-------|
| ok_nabu | "OK Nabu" | ⬜ Pass / ⬜ Fail | |
| hey_jarvis | "Hey Jarvis" | ⬜ Pass / ⬜ Fail | |
| alexa | "Alexa" | ⬜ Pass / ⬜ Fail | |

**Choose model with best accuracy for Dad's NZ accent.**

## Port Summary

| Service | Port | Protocol | Purpose |
|---------|------|----------|---------|
| Wyoming openWakeWord | 10400 | Wyoming (WebSocket) | Wake-word detection |
| Wyoming Whisper | 10300 | Wyoming (WebSocket) | Local STT (Phase 3+) |
| Wyoming Piper | 10200 | Wyoming (WebSocket) | Local TTS (Phase 3+) |
| Home Assistant | 8123 | HTTP/WebSocket | UI + Assist Pipeline |
| Session Manager | 5000 | HTTP/WebSocket | Audio processing (Phase 1 Days 3-4) |

**All Wyoming ports (10200, 10300, 10400) are localhost-only** - no external access needed.

## Success Criteria

Phase 1 wake-word setup complete when:
- ✅ Wyoming openWakeWord container running and healthy
- ✅ Home Assistant configured to use Wyoming Protocol
- ✅ "Dad VCA Pipeline" created in HA UI
- ✅ Wake-word detection working from HA Companion App
- ✅ Dad can trigger wake-word reliably (≥90% accuracy)
- ✅ Logs show wake-word detection events
- ✅ Ready to proceed with session manager (Days 3-4)

## Time Estimate

- **Container setup:** 15-20 minutes
- **HA configuration:** 10-15 minutes
- **Assist pipeline creation:** 10 minutes
- **Testing:** 15-20 minutes

**Total:** 50-65 minutes (~1 hour)

## Next Steps

After wake-word setup is working:
1. ✅ Continue Phase 1 Days 3-4: Build session manager (Python/FastAPI)
2. ✅ Integrate session manager with HA WebSocket API
3. ✅ Add Voice Activity Detection (silence timeout)
4. ✅ Implement stop phrase detection
5. ✅ Test end-to-end with Dad

## References

- [Wyoming Protocol](https://github.com/rhasspy/wyoming)
- [Wyoming openWakeWord](https://github.com/rhasspy/wyoming-openwakeword)
- [Wyoming Whisper](https://github.com/rhasspy/wyoming-faster-whisper)
- [Wyoming Piper](https://github.com/rhasspy/wyoming-piper)
- [HA Wyoming Integration](https://www.home-assistant.io/integrations/wyoming/)
- [openWakeWord Models](https://github.com/dscripka/openWakeWord)

---

**Status:** Ready to begin implementation
**Next:** Run Wyoming openWakeWord container and configure Home Assistant
