# Home Assistant Add-on Installation Guide
**VCA 1.0 - Phase 1, Days 1-2**
**Date:** 2025-11-01

## Overview

Install Wyoming protocol add-ons for Home Assistant voice pipeline:
- **Wyoming openWakeWord** - Wake-word detection ("Hey Assistant")
- **Wyoming Whisper** - Local STT (optional for Phase 1, required Phase 3+)
- **Wyoming Piper** - Local TTS (optional for Phase 1, required Phase 3+)

## Prerequisites

- ✅ Home Assistant 2025.10.4 running
- ✅ Accessible at `http://localhost:8123` (from PC) and `http://<WINDOWS_IP>:8123` (from phone)
- ✅ Logged in as Mike VCA (admin account)

## Installation Steps

### Step 1: Access Add-on Store

1. **Open Home Assistant** in your web browser:
   - From PC: `http://localhost:8123`
   - From phone: `http://<WINDOWS_IP>:8123`

2. **Navigate to Add-ons:**
   - Click **Settings** (gear icon in sidebar)
   - Click **Add-ons**
   - Click **Add-on Store** (bottom right, blue button)

### Step 2: Install Wyoming openWakeWord

**What it does:** Detects wake words like "Hey Assistant" to trigger listening mode

1. In the Add-on Store search box, type: **`wyoming openwakeword`**

2. Click on **Wyoming openWakeWord** card

3. Click **Install** button

4. Wait for installation to complete (may take 2-5 minutes)

5. **Configure the add-on:**
   - Once installed, you'll see the add-on page
   - Click **Configuration** tab
   - Default settings are fine for now, but note these options:
     ```yaml
     # Default configuration (don't change yet)
     models:
       - ok_nabu  # Default wake word model
     ```
   - Available models to test later:
     - `ok_nabu` - "OK Nabu"
     - `hey_jarvis` - "Hey Jarvis"
     - `alexa` - "Alexa"
     - We'll test which works best with Dad's NZ accent

6. **Start the add-on:**
   - Click **Info** tab
   - Toggle **Start on boot** to ON
   - Click **Start** button
   - Wait for status to show **Running** (green)

7. **Check logs:**
   - Click **Log** tab
   - Verify no error messages
   - Should see: `INFO:wyoming_openwakeword:Ready`

8. **Note the port:**
   - Default port: **10400**
   - We'll use this when configuring Assist pipeline

### Step 3: Install Wyoming Whisper (Optional for Phase 1)

**What it does:** Local speech-to-text (alternative to OpenAI Whisper API)

**Note:** This is OPTIONAL for Phase 1. We're starting with OpenAI Whisper API (cloud). Install this now for Phase 3+ when we transition to local processing.

1. In Add-on Store search box, type: **`wyoming whisper`**

2. Click on **Whisper** card (look for Wyoming icon)

3. Click **Install**

4. Wait for installation (~5-10 minutes, downloads model files)

5. **Configure the add-on:**
   - Click **Configuration** tab
   - Recommended settings for GTX 970 GPU:
     ```yaml
     model: small  # Good balance of speed/accuracy on GTX 970
     language: en  # English
     beam_size: 5  # Higher for better accuracy with slurred speech
     ```

6. **Don't start it yet** (not needed for Phase 1)
   - We'll enable this in Phase 3 when transitioning to local STT
   - For now, we're using OpenAI Whisper API

7. **Note the port:**
   - Default port: **10300**

### Step 4: Install Wyoming Piper (Optional for Phase 1)

**What it does:** Local text-to-speech (alternative to OpenAI TTS)

**Note:** This is OPTIONAL for Phase 1. We're starting with OpenAI TTS API. Install now for Phase 3+ local processing.

1. In Add-on Store search box, type: **`wyoming piper`**

2. Click on **Piper** card (Wyoming icon)

3. Click **Install**

4. Wait for installation (~3-5 minutes)

5. **Configure the add-on:**
   - Click **Configuration** tab
   - Recommended settings:
     ```yaml
     voice: en_US-lessac-medium  # Clear American English
     # Note: NZ English voice may be available, check voice list
     ```
   - To see available voices, click **Documentation** tab

6. **Don't start it yet** (not needed for Phase 1)
   - We'll use this in Phase 3 for privacy + cost savings
   - For now, using OpenAI TTS API

7. **Note the port:**
   - Default port: **10200**

### Step 5: Verify Installations

1. **Go back to Add-ons main page:**
   - Click **Settings** → **Add-ons**

2. **Check installed add-ons:**
   - You should see:
     - ✅ **Wyoming openWakeWord** (Running)
     - ⏸️ **Whisper** (Installed, not started - OK for Phase 1)
     - ⏸️ **Piper** (Installed, not started - OK for Phase 1)

3. **Verify openWakeWord is running:**
   - Click **Wyoming openWakeWord**
   - Status should be **Running** (green indicator)
   - Click **Log** tab
   - Should see `Ready` message

## Configuration Summary

| Add-on | Status | Port | Purpose | Phase 1 Usage |
|--------|--------|------|---------|---------------|
| **Wyoming openWakeWord** | ✅ Running | 10400 | Wake-word detection | **Required** |
| **Whisper** | ⏸️ Installed | 10300 | Local STT | Optional (using OpenAI API) |
| **Piper** | ⏸️ Installed | 10200 | Local TTS | Optional (using OpenAI API) |

## Next Steps

### Create Assist Pipeline

Now that openWakeWord is running, we can create the "Dad VCA Pipeline":

1. **Go to Settings → Voice Assistants**

2. **Click "Add Assistant"**

3. **Configure the pipeline:**
   - **Name:** `Dad VCA Pipeline`
   - **Language:** English (en-US or en-NZ if available)
   - **Conversation agent:** Home Assistant (default for now)
   - **Wake word engine:**
     - Select **Wyoming Protocol**
     - Host: `localhost` or `127.0.0.1`
     - Port: `10400`
   - **Speech-to-text:**
     - For Phase 1: Select **Home Assistant Cloud** or configure OpenAI API
     - For Phase 3+: Wyoming Protocol (localhost:10300)
   - **Text-to-speech:**
     - For Phase 1: Home Assistant Cloud or OpenAI API
     - For Phase 3+: Wyoming Protocol (localhost:10200)

4. **Test the pipeline:**
   - Click **Test** button
   - Say a wake word (if available on PC mic)
   - Or proceed to phone testing

**Detailed Assist pipeline configuration in next guide.**

## Troubleshooting

### Issue: Add-on won't start

**Check logs:**
1. Click on the add-on
2. Click **Log** tab
3. Look for error messages

**Common causes:**
- Port already in use (check other services)
- Insufficient permissions
- Out of memory (close other apps)

**Solution:**
```bash
# Restart Home Assistant container
docker restart homeassistant

# Wait 60 seconds, then try starting add-on again
```

### Issue: Can't find add-on in store

**Check Home Assistant version:**
- Wyoming add-ons require Home Assistant 2023.9+
- We have 2025.10.4 ✅

**Refresh add-on store:**
- Close browser tab
- Open `http://localhost:8123` again
- Navigate to Add-on Store

### Issue: Installation takes very long

**Expected times:**
- openWakeWord: 2-5 minutes
- Whisper: 5-10 minutes (downloads models)
- Piper: 3-5 minutes

**If >15 minutes:**
- Check internet connection
- Check Docker logs: `docker logs homeassistant --tail 100`
- Restart installation if stuck

### Issue: openWakeWord not detecting wake word

**Troubleshooting steps:**

1. **Check microphone input:**
   - Ensure PC microphone is working
   - Or test from phone with Companion App

2. **Try different wake word model:**
   - Stop openWakeWord add-on
   - Edit configuration, change model:
     ```yaml
     models:
       - hey_jarvis  # Try this instead of ok_nabu
     ```
   - Save and restart add-on

3. **Adjust sensitivity:**
   - Will be tunable in Assist pipeline settings
   - Lower threshold = more sensitive (more false positives)
   - Higher threshold = less sensitive (might miss wake words)

## Testing Wake-Word Detection

### Quick Test (If you have PC microphone)

1. **Open openWakeWord logs:**
   - Settings → Add-ons → Wyoming openWakeWord
   - Click **Log** tab
   - Keep this open

2. **Say the wake word:**
   - Say "OK Nabu" clearly (or "Hey Jarvis" if you changed model)
   - Watch logs for detection message

3. **Expected log output:**
   ```
   INFO:wyoming_openwakeword:Detection: ok_nabu (score: 0.95)
   ```

### Full Test (With Phone - After Companion App Setup)

This will be tested in Days 5-6 when we integrate the phone.

## Phase 3+ Configuration Notes

When transitioning to local STT/TTS in Phase 3:

### Enable Whisper
1. Start Whisper add-on
2. Update Assist pipeline STT to Wyoming Protocol (localhost:10300)
3. Test transcription accuracy
4. Compare with OpenAI API performance

### Enable Piper
1. Start Piper add-on
2. Update Assist pipeline TTS to Wyoming Protocol (localhost:10200)
3. Test voice quality
4. Adjust speed if needed (Dad may prefer slower)

### Test NZ English Voices
```yaml
# Check if NZ English voice available for Piper
# In Piper configuration, try:
voice: en_NZ-aotearoa-medium  # If available
```

## Security Notes

### Ports Summary
- **10400** (openWakeWord): Only accessible from localhost (Docker internal)
- **10300** (Whisper): Only accessible from localhost
- **10200** (Piper): Only accessible from localhost

**These ports are NOT exposed to the network** - they communicate with Home Assistant via Docker internal networking. No additional firewall rules needed.

### API Keys (Phase 1 - Cloud Services)

For OpenAI integration, we'll configure via Home Assistant secrets:

**File:** `/home/indigo/homeassistant/config/secrets.yaml`
```yaml
openai_api_key: "your_openai_api_key_here"
```

**Reference in configuration.yaml:**
```yaml
stt:
  - platform: openai
    api_key: !secret openai_api_key
    model: whisper-1

tts:
  - platform: openai_tts
    api_key: !secret openai_api_key
    voice: nova
```

## Success Criteria

Phase 1 add-on installation is complete when:
- ✅ Wyoming openWakeWord installed and running
- ✅ Whisper installed (not started - for Phase 3+)
- ✅ Piper installed (not started - for Phase 3+)
- ✅ openWakeWord logs show "Ready" status
- ✅ Ports 10400, 10300, 10200 allocated
- ✅ Ready to create Assist pipeline

## Time Estimate

- **Installation:** 15-20 minutes
- **Configuration:** 5-10 minutes
- **Testing:** 5 minutes

**Total:** ~30-35 minutes

## References

- [Wyoming Protocol Documentation](https://github.com/rhasspy/wyoming)
- [Home Assistant Voice Control](https://www.home-assistant.io/voice_control/)
- [openWakeWord Models](https://github.com/dscripka/openWakeWord)
- [Whisper Models](https://github.com/openai/whisper)
- [Piper Voices](https://github.com/rhasspy/piper)

---

**Next Guide:** Assist Pipeline Configuration & Testing
