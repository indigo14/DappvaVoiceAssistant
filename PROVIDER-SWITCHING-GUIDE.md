# Provider Switching Guide
## VCA Voice Assistant - STT/TTS Provider Experimentation

**Purpose**: This guide explains how to switch between different Speech-to-Text (STT) and Text-to-Speech (TTS) providers to find the best combination for Warren's slurred speech.

**Last Updated**: 2025-11-03 (Session 7)

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Available Providers](#available-providers)
3. [Configuration Guide](#configuration-guide)
4. [Adding New Providers](#adding-new-providers)
5. [Testing & Comparison](#testing--comparison)
6. [Troubleshooting](#troubleshooting)

---

## Quick Start

### How to Switch Providers

**Step 1**: Edit `session_manager/config.yaml`

**Step 2**: Change provider names:
```yaml
# Find these lines (around line 158-161)
stt_provider: "openai_whisper"  # Change to: mock_stt, local_whisper, etc.
tts_provider: "openai_tts"      # Change to: mock_tts, piper, etc.
```

**Step 3**: Restart Session Manager:
```bash
cd /home/indigo/my-project3/Dappva/session_manager

# Kill existing process
lsof -ti:5000 | xargs -r kill -9

# Restart
source venv/bin/activate
python main.py
```

**Step 4**: Verify in logs:
```
[INFO] Initialized STT provider 'mock_stt': MockSTTProvider(latency=0.5s, ...)
[INFO] Initialized TTS provider 'mock_tts': MockTTSProvider(latency=0.3s, ...)
```

**That's it!** No code changes needed.

---

## Available Providers

### STT (Speech-to-Text) Providers

#### 1. `openai_whisper` ✅ Currently Active

**Status**: Implemented and tested
**Latency**: 8.2-8.6 seconds
**Cost**: ~$0.006 per minute of audio
**Accuracy**: Excellent for clear speech

**Configuration**:
```yaml
stt_provider: "openai_whisper"

# Config is under openai.stt section
openai:
  stt:
    model: "whisper-1"
    language: "en"
    temperature: 0.0
```

**Pros**:
- High accuracy
- Handles multiple languages
- Good with accents

**Cons**:
- Slow (8+ seconds)
- API costs
- Network dependency
- May struggle with slurred speech (untested with Warren)

#### 2. `mock_stt` ✅ Implemented

**Status**: Implemented for testing
**Latency**: 0.5 seconds (configurable)
**Cost**: Free (no API calls)
**Accuracy**: Returns fixed text (not real transcription)

**Configuration**:
```yaml
stt_provider: "mock_stt"

mock_stt:
  mock_latency: 0.5  # Simulate 0.5s processing
  mock_text: "Hello, this is a test transcription"
  mock_confidence: 0.98
```

**Use Cases**:
- Testing latency tracking
- Development without API costs
- UI/UX testing
- Performance benchmarking

#### 3. `local_whisper` ⏳ Future

**Status**: Planned for implementation
**Latency**: 2-4 seconds (GPU accelerated)
**Cost**: Free (local processing)
**Accuracy**: Same as OpenAI Whisper

**Expected Configuration**:
```yaml
stt_provider: "local_whisper"

local_whisper:
  model_size: "small"  # tiny, base, small, medium, large
  device: "cuda"       # cuda or cpu
  language: "en"
```

**Benefits**:
- 4-6s faster than OpenAI API
- No API costs
- No network dependency
- Privacy (audio stays local)

**Requirements**:
- GPU with CUDA support (GTX 970 is sufficient)
- ~1-2 GB disk space for model
- ~2 GB GPU RAM

#### 4. `deepgram` ⏳ Future

**Status**: Planned
**Latency**: 1-2 seconds (streaming)
**Cost**: ~$0.0043 per minute
**Accuracy**: Excellent, tuned for real-time

**Expected Configuration**:
```yaml
stt_provider: "deepgram"

deepgram:
  api_key: ${DEEPGRAM_API_KEY}
  model: "nova-2"
  language: "en-US"
```

**Benefits**:
- Fastest API option
- Streaming support
- Good with difficult audio

#### 5. `vosk` ⏳ Future

**Status**: Planned
**Latency**: 0.5-1 second (local)
**Cost**: Free
**Accuracy**: Good for simple use cases

**Expected Configuration**:
```yaml
stt_provider: "vosk"

vosk:
  model_path: "/path/to/vosk-model-en-us-0.22"
```

**Benefits**:
- Very fast
- Completely offline
- Lightweight

**Cons**:
- Lower accuracy than Whisper
- Limited language support

---

### TTS (Text-to-Speech) Providers

#### 1. `openai_tts` ✅ Currently Active

**Status**: Implemented and tested
**Latency**: ~3 seconds (estimated)
**Cost**: ~$0.015 per 1K characters
**Quality**: Excellent, natural voices

**Configuration**:
```yaml
tts_provider: "openai_tts"

openai:
  tts:
    model: "tts-1"
    voice: "nova"  # alloy, echo, fable, onyx, nova, shimmer
    speed: 1.0
```

**Voices**:
- `alloy`: Neutral, balanced
- `echo`: Male, clear
- `fable`: Warm, expressive
- `onyx`: Deep, authoritative
- `nova`: Female, friendly (current)
- `shimmer`: Bright, upbeat

#### 2. `mock_tts` ✅ Implemented

**Status**: Implemented for testing
**Latency**: 0.3 seconds (configurable)
**Cost**: Free
**Quality**: Silent audio (testing only)

**Configuration**:
```yaml
tts_provider: "mock_tts"

mock_tts:
  mock_latency: 0.3
  audio_format: "mp3"
  sample_rate: 24000
```

**Use Cases**:
- Testing without API costs
- Performance benchmarking
- Development workflow

#### 3. `piper` ⏳ High Priority for Next Session

**Status**: Planned
**Latency**: 0.2-0.5 seconds (local, GPU)
**Cost**: Free
**Quality**: Very good, natural

**Expected Configuration**:
```yaml
tts_provider: "piper"

piper:
  model_path: "/path/to/piper/models"
  speaker: "en_US-lessac-medium"  # or other voices
  use_gpu: true
```

**Benefits**:
- 2.5s faster than OpenAI
- No API costs
- Offline operation
- Multiple voices available

**Voices Available**:
- `en_US-lessac-medium`: Male, clear, recommended
- `en_US-amy-medium`: Female, natural
- `en_US-libritts-high`: High quality, slower

**Why This Matters**:
- **Piper could reduce total latency by 2.5 seconds**
- Gets us from ~10s total to ~7.5s total
- Makes conversation more natural

---

## Configuration Guide

### Config File Structure

**Location**: `session_manager/config.yaml`

**Provider Selection** (lines 154-172):
```yaml
# ============================================================================
# PROVIDER SELECTION (Easy switching for experimentation)
# ============================================================================
# STT Provider Selection
stt_provider: "openai_whisper"  # Change this

# TTS Provider Selection
tts_provider: "openai_tts"  # Change this

# Provider-specific configs below...
```

### Provider-Specific Configurations

Each provider has its own configuration section:

```yaml
# OpenAI STT configuration
openai:
  stt:
    model: "whisper-1"
    language: "en"
    temperature: 0.0

# Mock STT configuration
mock_stt:
  mock_latency: 0.5
  mock_text: "Test transcription"
  mock_confidence: 0.98

# OpenAI TTS configuration
openai:
  tts:
    model: "tts-1"
    voice: "nova"
    speed: 1.0

# Mock TTS configuration
mock_tts:
  mock_latency: 0.3
  audio_format: "mp3"
  sample_rate: 24000
```

### Environment Variables

**OpenAI API Key**:
```bash
# In session_manager/.env
OPENAI_API_KEY=sk-proj-...
```

**Future Providers**:
```bash
# Add as needed
DEEPGRAM_API_KEY=...
ELEVENLABS_API_KEY=...
```

---

## Adding New Providers

### Step-by-Step Guide

Let's add **Piper TTS** as an example:

#### Step 1: Create Provider Class

**File**: `session_manager/tts/providers/piper.py`

```python
"""
Piper TTS Provider - Local, fast, high-quality TTS
"""

import asyncio
import subprocess
from pathlib import Path
from ..base import TTSProvider, TTSResult

class PiperTTSProvider(TTSProvider):
    def __init__(self, config: dict):
        super().__init__(config)
        self.model_path = config.get('model_path')
        self.speaker = config.get('speaker', 'en_US-lessac-medium')
        self.use_gpu = config.get('use_gpu', True)
        self.sample_rate = config.get('sample_rate', 22050)

    async def synthesize(self, text: str) -> TTSResult:
        """Synthesize speech using Piper."""
        # Call Piper command-line tool
        cmd = [
            'piper',
            '--model', f'{self.model_path}/{self.speaker}.onnx',
            '--output_file', '-'  # Output to stdout
        ]

        # Run Piper
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        audio_bytes, _ = await proc.communicate(input=text.encode())

        # Calculate duration
        duration = len(audio_bytes) / (self.sample_rate * 2)  # 16-bit PCM

        return TTSResult(
            audio_bytes=audio_bytes,
            sample_rate=self.sample_rate,
            format='wav',
            duration=duration
        )

    def __repr__(self) -> str:
        return f"PiperTTSProvider(speaker='{self.speaker}', gpu={self.use_gpu})"
```

#### Step 2: Register in Factory

**File**: `session_manager/tts/factory.py`

```python
# Add import
from .providers.piper import PiperTTSProvider

class TTSProviderFactory:
    _providers = {
        'openai_tts': OpenAITTSProvider,
        'mock_tts': MockTTSProvider,
        'piper': PiperTTSProvider,  # Add this line
    }
```

#### Step 3: Add Configuration

**File**: `session_manager/config.yaml`

```yaml
# TTS Provider Selection
tts_provider: "piper"  # Change this

# Piper TTS configuration
piper:
  model_path: "/home/indigo/piper/models"
  speaker: "en_US-lessac-medium"
  use_gpu: true
  sample_rate: 22050
```

#### Step 4: Test

```bash
# Restart session manager
cd session_manager
lsof -ti:5000 | xargs -r kill -9
source venv/bin/activate
python main.py

# Check logs
tail -f /tmp/session_manager_new.log
# Should see: "Initialized TTS provider 'piper': PiperTTSProvider(...)"
```

### Template for STT Providers

Same process for STT providers - just use `STTProvider` base class and `STTProviderFactory`.

---

## Testing & Comparison

### Testing Checklist

When testing a new provider:

- [ ] Provider initializes without errors
- [ ] Logs show correct provider name
- [ ] Audio processing completes successfully
- [ ] Latency metrics include provider name
- [ ] Latency is reasonable for use case
- [ ] Quality is acceptable (for STT: accuracy, for TTS: naturalness)
- [ ] No crashes or errors during extended use

### A/B Comparison Workflow

**Goal**: Compare providers side-by-side with identical audio

**Steps**:

1. **Record Test Audio**:
   ```bash
   # Record Warren's voice saying a test phrase
   # Save as test_warren_sample1.wav
   ```

2. **Test Provider A**:
   ```yaml
   # config.yaml
   stt_provider: "openai_whisper"
   ```
   - Run test client with audio
   - Note latency: 8.5s
   - Note transcription: "Hello, this is a test"
   - Note accuracy: 100%

3. **Test Provider B**:
   ```yaml
   # config.yaml
   stt_provider: "local_whisper"
   ```
   - Run test client with same audio
   - Note latency: 3.2s
   - Note transcription: "Hello, this is a test"
   - Note accuracy: 100%

4. **Compare**:
   - Latency: local_whisper is 5.3s faster
   - Accuracy: Both 100% for this sample
   - Decision: Use local_whisper for speed

5. **Test with Slurred Speech**:
   - Repeat with Warren's actual speech
   - May find one provider handles slurred speech better
   - Choose based on accuracy, not speed

### Latency Comparison Table

Use latency tracker output to compare:

```
Provider        | STT Time | TTS Time | Total Pipeline
----------------|----------|----------|---------------
openai_whisper  | 8.5s     | 3.0s     | 12.5s
+ openai_tts    |          |          |
----------------|----------|----------|---------------
local_whisper   | 3.0s     | 3.0s     | 7.0s
+ openai_tts    |          |          |
----------------|----------|----------|---------------
local_whisper   | 3.0s     | 0.4s     | 4.4s (BEST)
+ piper         |          |          |
----------------|----------|----------|---------------
mock_stt        | 0.5s     | 0.3s     | 1.8s (testing)
+ mock_tts      |          |          |
```

### Metrics to Track

For each provider combination:

1. **Latency**:
   - STT time
   - TTS time
   - Total pipeline time

2. **Accuracy** (for STT):
   - Word Error Rate (WER)
   - Understanding of slurred speech
   - Handling of background noise

3. **Quality** (for TTS):
   - Naturalness
   - Clarity
   - Warren's preference

4. **Cost**:
   - Per request
   - Monthly estimate
   - vs. local (free)

5. **Reliability**:
   - Success rate
   - Error frequency
   - Network dependency

---

## Troubleshooting

### Common Issues

#### Issue: Provider Not Found

**Error**:
```
ValueError: Unknown STT provider: 'piper'
```

**Cause**: Provider not registered in factory

**Fix**:
```python
# In stt/factory.py or tts/factory.py
from .providers.piper import PiperTTSProvider  # Add import

class TTSProviderFactory:
    _providers = {
        'openai_tts': OpenAITTSProvider,
        'piper': PiperTTSProvider,  # Add registration
    }
```

#### Issue: Config Not Loading

**Error**:
```
KeyError: 'model_path'
```

**Cause**: Config loading in main.py not updated for new provider

**Fix** (`main.py` lines 73-82):
```python
# Load provider-specific config
if tts_provider_name == 'piper':
    tts_config = settings.get('piper', {})
elif tts_provider_name == 'openai_tts':
    tts_config = {
        'api_key': settings.get('openai.api_key'),
        ...
    }
```

#### Issue: Provider Shows as "unknown" in Metrics

**Error**: Latency breakdown shows:
```
║ STT Provider: unknown
```

**Cause**: Provider name not set in metrics

**Fix** (`main.py` line 239):
```python
metrics.stt_provider = stt_provider_name  # Add this line
```

#### Issue: Mock Provider Not Working

**Error**: Still calling OpenAI API

**Cause**: Config loading defaults to OpenAI config

**Fix**: Complete provider-specific config loading (see TODO in SESSION-7-SUMMARY.md)

---

## Best Practices

### For Warren's Use Case

1. **Accuracy > Speed**: Warren's slurred speech requires best STT accuracy
2. **Test with Real Samples**: Use Warren's actual voice for testing
3. **Compare Multiple Providers**: Don't assume first provider is best
4. **Document Results**: Keep notes on what works/doesn't work
5. **Start Local**: Prefer local providers (free, private, fast)

### Development Workflow

1. **Use Mock Providers** for:
   - Testing latency tracking
   - UI development
   - Debugging without API costs

2. **Use OpenAI Providers** for:
   - Establishing baseline
   - High-quality reference
   - When accuracy is critical

3. **Use Local Providers** for:
   - Production deployment
   - Cost savings
   - Speed optimization
   - Privacy

### Configuration Management

1. **Keep Comments**: Document why you chose each provider
2. **Version Control**: Commit config changes with explanations
3. **Environment-Specific**: Use different configs for dev/prod
4. **Backup Working Configs**: Save configurations that work well

---

## Next Steps

### Recommended Implementation Order

1. **Complete Config Loading** (~10 minutes)
   - Fix main.py to load provider-specific configs
   - Test with mock providers

2. **Implement Piper TTS** (~2 hours)
   - Create PiperTTSProvider class
   - Register in factory
   - Test latency improvement (expect ~2.5s faster)

3. **Implement Local Whisper** (~2-3 hours)
   - Create LocalWhisperProvider class
   - Install model on GPU
   - Test latency improvement (expect ~5s faster)

4. **Test with Warren's Voice** (~1 hour)
   - Record samples of slurred speech
   - Test all STT providers
   - Choose best for accuracy

5. **Production Configuration** (~30 minutes)
   - Set optimal provider combination
   - Document decision rationale
   - Configure for deployment

---

## Quick Reference

### Switch to Mock Providers (Fast Testing)

```yaml
stt_provider: "mock_stt"
tts_provider: "mock_tts"
```

**Expected**: <1s total latency, no API costs

### Switch to Local Providers (Production)

```yaml
stt_provider: "local_whisper"
tts_provider: "piper"
```

**Expected**: ~4s total latency, no costs, private

### Switch to OpenAI (Baseline)

```yaml
stt_provider: "openai_whisper"
tts_provider: "openai_tts"
```

**Expected**: ~12s total latency, highest quality

---

## Additional Resources

- **Piper TTS**: https://github.com/rhasspy/piper
- **Whisper (Local)**: https://github.com/openai/whisper
- **Deepgram**: https://deepgram.com/
- **Vosk**: https://alphacephei.com/vosk/

---

**Last Updated**: 2025-11-03
**Session**: 7 (Provider Switching Implementation)
**Status**: Ready for experimentation
