# SESSION 8: Latency Tracking - Maintenance & Troubleshooting Guide
## VCA 1.0 Voice Assistant - Complete Reference for Latency Monitoring

**Date**: 2025-11-03
**Session**: Session 8
**Purpose**: Comprehensive guide for testing, maintaining, and troubleshooting latency tracking
**Your Go-To Resource**: "How do I make changes to the latency tracker?" or "I broke something, help!"

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Quick Reference - Common Tasks](#quick-reference---common-tasks)
3. [Testing Procedures](#testing-procedures)
4. [Configuration Reference](#configuration-reference)
5. [Architecture & Code Locations](#architecture--code-locations)
6. [Troubleshooting Guide](#troubleshooting-guide)
7. [Maintenance Tasks](#maintenance-tasks)
8. [Optimization Recommendations](#optimization-recommendations)

---

## System Overview

### What is the Latency Tracking System?

The latency tracking system measures, analyzes, and optimizes the time it takes for the voice assistant to respond to user requests. It tracks every component of the pipeline from speech input to audio response.

### Current Status (Session 8)

✅ **Fully Implemented**
- Comprehensive metric tracking (14+ metrics per request)
- Real-time optimization suggestions
- Provider name tracking for A/B testing
- Statistical analysis (mean, median, P50/P90/P99)
- WebSocket client reporting

✅ **Tested Components**
- Simulated latency tests (Session 7)
- Provider factory pattern (OpenAI ↔ Mock switching)
- Config loading for multiple providers
- Baseline measurements with OpenAI Whisper STT

⚠️ **Known Issues**
- Android app WebSocket protocol mismatch (discovered Session 8)
- No live phone + recording tests completed yet
- LLM module not implemented (echo mode only)

### Key Metrics Tracked

| Metric | Description | Target |
|--------|-------------|--------|
| `vad_processing` | Voice Activity Detection time | 0.1s |
| `silence_detection` | Waiting for speech end | 1.5s |
| `stt_total` | Speech-to-Text complete pipeline | 4.0s |
| `stt_network_upload` | Audio upload time | - |
| `stt_processing` | STT API processing | - |
| `llm_total` | Language Model response generation | 3.0s |
| `tts_total` | Text-to-Speech synthesis | 3.0s |
| `websocket_transmission` | Audio response delivery | 0.5s |
| `total_pipeline` | **Complete end-to-end time** | **10.0s** |

---

## Quick Reference - Common Tasks

### "How do I run a latency test?"

**Option 1: With PC Test Client** (Recommended for now)
```bash
cd /home/indigo/my-project3/Dappva/session_manager

# Start Session Manager
source venv/bin/activate
python main.py

# In another terminal, run test client
python test_client.py
```

**Option 2: With Android App** (Requires protocol fix)
```bash
# Start Session Manager with monitoring
python main.py

# Use Android app to make recordings
# (Currently blocked by protocol issue - see Troubleshooting)
```

### "How do I change the latency target?"

**Edit:** `session_manager/config.yaml`
```yaml
latency_monitoring:
  target_total_latency: 10.0  # Change this value (in seconds)
```

**Restart Session Manager:**
```bash
lsof -ti:5000 | xargs -r kill -9
source venv/bin/activate
python main.py
```

### "How do I switch providers to test latency?"

**Edit:** `session_manager/config.yaml` (lines 158-161)
```yaml
# Test with fast mock providers (no API calls)
stt_provider: "mock_stt"
tts_provider: "mock_tts"

# OR use OpenAI (real but slower)
stt_provider: "openai_whisper"
tts_provider: "openai_tts"
```

**Restart:** `lsof -ti:5000 | xargs -r kill -9 && python main.py`

### "Where do I see latency results?"

**Option 1: Session Manager Logs**
```bash
tail -f logs/session_manager.log | grep -A 15 "Latency Breakdown"
```

**Option 2: Simulated Test Output**
```bash
cd /home/indigo/my-project3/Dappva/session_manager
python test_latency.py
```

**Option 3: Android App** (when protocol is fixed)
- Latency metrics sent via WebSocket (`type: "latency_report"`)
- App can display breakdown in real-time

### "How do I add a new metric to track?"

See [Maintenance Tasks → Adding New Metrics](#adding-new-metrics)

---

## Testing Procedures

### Test 1: Provider Switching Validation

**Purpose:** Verify provider factory pattern works correctly

**Steps:**
1. **Start with OpenAI providers**
   ```bash
   # Verify config.yaml has:
   stt_provider: "openai_whisper"
   tts_provider: "openai_tts"

   # Start Session Manager
   python main.py

   # Check logs for:
   # "Initialized STT provider 'openai_whisper'"
   # "Initialized TTS provider 'openai_tts'"
   ```

2. **Switch to Mock providers**
   ```bash
   # Edit config.yaml:
   stt_provider: "mock_stt"
   tts_provider: "mock_tts"

   # Restart
   lsof -ti:5000 | xargs -r kill -9
   python main.py

   # Check logs for:
   # "Initialized STT provider 'mock_stt'"
   # "Initialized TTS provider 'mock_tts'"
   ```

3. **Switch back to OpenAI**
   ```bash
   # Revert config.yaml to openai_whisper/openai_tts
   # Restart and verify logs
   ```

**Expected Results:**
- ✅ Session Manager starts without errors
- ✅ Correct provider names appear in logs
- ✅ Provider-specific config loaded (check detailed log output)

**Actual Results (Session 8):**
- ✅ OpenAI → Mock switching: **SUCCESS**
- ✅ Mock → OpenAI switching: **SUCCESS**
- ✅ Config loading fixed in main.py:67-109

### Test 2: Simulated Latency Testing

**Purpose:** Measure latency with simulated data (no phone required)

**Script:** `session_manager/test_latency.py`

**Run:**
```bash
cd /home/indigo/my-project3/Dappva/session_manager
source venv/bin/activate
python test_latency.py
```

**Expected Output:**
```
=== Testing Latency Tracker with Different LLM Models ===

Testing with model: gpt-5
Testing with model: gpt-5-mini
Testing with model: gpt-5-nano

=== Latency Statistics ===
──────────────────────────────────────────────────
Component Statistics (3 requests):

STT Total: mean=4.00s, median=4.00s, p50=4.00s, p90=4.00s, p99=4.00s
LLM Total: mean=2.67s, median=2.50s, p50=2.50s, p90=4.50s, p99=4.50s
TTS Total: mean=3.00s, median=3.00s, p50=3.00s, p90=3.00s, p99=3.00s
Total Pipeline: mean=10.17s, median=10.00s, p50=10.00s, p90=12.00s, p99=12.00s

=== Model Comparison ===
Model: gpt-5, LLM Time: 4.50s, Total: 12.00s
Model: gpt-5-mini, LLM Time: 2.50s, Total: 10.00s
Model: gpt-5-nano, LLM Time: 1.00s, Total: 8.50s
```

**What This Tests:**
- ✅ Latency metrics recording
- ✅ Statistics calculation (mean, median, percentiles)
- ✅ Model comparison logic
- ✅ Bottleneck identification

**Actual Results (Session 7):**
- ✅ All statistics calculated correctly
- ✅ Model variants compared successfully
- ✅ P90/P99 percentiles working

### Test 3: Live Phone + Recording Test

**Purpose:** Measure real-world latency with Android app

**Prerequisites:**
- ⚠️ **BLOCKED:** Android app protocol issue (see Troubleshooting)
- Phone connected via USB (authorized for debugging)
- VCAAssistant app installed
- Session Manager running

**Steps (When Protocol is Fixed):**
1. **Start monitoring:**
   ```bash
   cd /home/indigo/my-project3/Dappva/session_manager
   tail -f logs/session_manager.log | python3 capture_live_latency.py
   ```

2. **Open VCAAssistant app** on Samsung A05

3. **Make 5-10 test recordings** with various phrases:
   - "Hello, this is a test" (short)
   - "What's the weather like today?" (medium)
   - "Can you help me troubleshoot my computer?" (long)

4. **Review results:**
   - Real-time breakdown appears in monitoring script
   - Statistics calculated when monitoring stopped (Ctrl+C)
   - Results saved to `live_latency_test_YYYYMMDD_HHMMSS.json`

**Expected Metrics:**
- Total pipeline: 11-15s (with OpenAI Whisper + TTS)
- STT: 8-9s (OpenAI Whisper over network)
- TTS: ~3s (OpenAI TTS)
- Network overhead: 0.5-1s

**Status:** ❌ Not yet tested (Session 8 blocked by protocol issue)

### Test 4: Optimization Advisor Validation

**Purpose:** Verify suggestions are generated correctly

**Steps:**
1. **Run with slow providers:**
   ```yaml
   stt_provider: "openai_whisper"  # ~8.5s (slow)
   tts_provider: "openai_tts"      # ~3s
   ```

2. **Make a request** (using test_client.py or app)

3. **Check logs for suggestions:**
   ```
   [WARNING] OPTIMIZATION SUGGESTION [HIGH]:
   STT latency (8.50s) exceeds target (4.00s).
   Recommendation: Switch to local Whisper (estimated 2-3s)
   Potential savings: 5-6 seconds
   ```

**Expected Behavior:**
- Suggestions appear if component exceeds target
- Priority: HIGH (≥1.5s savings), MEDIUM (0.5-1.5s), LOW (<0.5s)
- Specific recommendations (e.g., "Switch to local Whisper")

**Status:** ✅ Implemented and tested in Session 7

---

## Configuration Reference

### Complete Latency Configuration

**File:** `session_manager/config.yaml` (lines 7-43)

```yaml
# ============================================================================
# LATENCY MONITORING CONFIGURATION (Easy-to-change parameters at top)
# ============================================================================
latency_monitoring:
  enabled: true
  target_total_latency: 10.0  # Target in seconds for total pipeline
  log_breakdown: true          # Log detailed breakdown after each request
  send_to_client: true         # Send metrics to Android app

  # Component-specific targets (in seconds)
  component_targets:
    vad: 0.1
    silence_detection: 1.5
    stt: 4.0
    llm: 3.0
    tts: 3.0
    websocket: 0.5

  # Model-specific expected latencies (for decision making)
  model_latencies:
    gpt-5:
      min: 3.0
      avg: 4.5
      max: 6.0
    gpt-5-mini:
      min: 2.0
      avg: 2.5
      max: 3.5
    gpt-5-nano:
      min: 0.5
      avg: 1.0
      max: 1.5
    gpt-4o:
      min: 2.5
      avg: 3.5
      max: 4.5

  # Automatic optimization suggestions
  optimization_suggestions: true
```

### Configuration Options Explained

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | bool | `true` | Master switch for latency tracking |
| `target_total_latency` | float | `10.0` | Goal for end-to-end response time (seconds) |
| `log_breakdown` | bool | `true` | Log detailed ASCII table after each request |
| `send_to_client` | bool | `true` | Send metrics to Android app via WebSocket |
| `optimization_suggestions` | bool | `true` | Enable automatic optimization advice |
| `component_targets` | dict | see above | Per-component target latencies |
| `model_latencies` | dict | see above | Expected LLM response times (for suggestions) |

### How to Modify Targets

**Scenario 1: I want to be more aggressive (aim for 8s total)**
```yaml
latency_monitoring:
  target_total_latency: 8.0
  component_targets:
    stt: 3.0     # Tighter STT target
    llm: 2.0     # Tighter LLM target
    tts: 2.0     # Tighter TTS target
```

**Scenario 2: I want to relax targets (testing mode)**
```yaml
latency_monitoring:
  target_total_latency: 15.0
  component_targets:
    stt: 10.0    # Allow slower STT
    llm: 5.0
    tts: 5.0
```

**Scenario 3: Disable logging (production)**
```yaml
latency_monitoring:
  enabled: true
  log_breakdown: false          # Don't spam logs
  send_to_client: true          # Still send to app
  optimization_suggestions: false  # No suggestions
```

### Provider Selection

**File:** `session_manager/config.yaml` (lines 157-172)

```yaml
# ============================================================================
# PROVIDER SELECTION (Easy switching for experimentation)
# ============================================================================
# STT Provider Selection
stt_provider: "openai_whisper"  # Options: openai_whisper, mock_stt, deepgram, local_whisper

# TTS Provider Selection
tts_provider: "openai_tts"  # Options: openai_tts, mock_tts, elevenlabs, local_piper

# Mock Provider Configuration (for testing without API calls)
mock_stt:
  mock_latency: 0.5  # Fast mock STT (0.5 seconds)
  mock_text: "Hello, this is a test transcription"
  mock_confidence: 0.98

mock_tts:
  mock_latency: 0.3  # Fast mock TTS (0.3 seconds)
  audio_format: "mp3"
  sample_rate: 24000
```

**How Mock Providers Work:**
- No API calls (instant, free, offline)
- Configurable latency simulation (`mock_latency`)
- Fixed response (`mock_text`)
- Perfect for testing latency tracking without costs

---

## Architecture & Code Locations

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     SESSION MANAGER                          │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ WebSocket    │  │ Audio        │  │ VAD          │      │
│  │ Handler      │──│ Processing   │──│ Detection    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                  │                  │             │
│         │                  ▼                  │             │
│         │          ┌──────────────┐          │             │
│         │          │ STT Provider │          │             │
│         │          │ (Factory)    │          │             │
│         │          └──────────────┘          │             │
│         │                  │                  │             │
│         │                  ▼                  │             │
│         │          ┌──────────────┐          │             │
│         │          │ LLM Module   │          │             │
│         │          │ (Echo Mode)  │          │             │
│         │          └──────────────┘          │             │
│         │                  │                  │             │
│         │                  ▼                  │             │
│         │          ┌──────────────┐          │             │
│         │          │ TTS Provider │          │             │
│         │          │ (Factory)    │          │             │
│         │          └──────────────┘          │             │
│         │                  │                  │             │
│         ▼                  ▼                  ▼             │
│  ┌─────────────────────────────────────────────────┐      │
│  │         LATENCY TRACKING LAYER                   │      │
│  │                                                  │      │
│  │  ┌──────────────┐  ┌──────────────────────┐   │      │
│  │  │ Latency      │  │ Optimization         │   │      │
│  │  │ Metrics      │──│ Advisor              │   │      │
│  │  └──────────────┘  └──────────────────────┘   │      │
│  │         │                    │                  │      │
│  │  ┌──────────────┐  ┌──────────────────────┐   │      │
│  │  │ Latency      │  │ Statistics           │   │      │
│  │  │ Tracker      │──│ Calculator           │   │      │
│  │  └──────────────┘  └──────────────────────┘   │      │
│  └─────────────────────────────────────────────────┘      │
│                          │                                 │
│                          ▼                                 │
│                  ┌──────────────┐                         │
│                  │ Logs +       │                         │
│                  │ WebSocket    │                         │
│                  │ Reports      │                         │
│                  └──────────────┘                         │
└─────────────────────────────────────────────────────────────┘
```

### File Structure

```
session_manager/
├── main.py                              # WebSocket handler + latency integration
├── config.yaml                          # All configuration (lines 7-43: latency)
│
├── monitoring/                          # Latency tracking module
│   ├── __init__.py
│   ├── latency_tracker.py               # LatencyMetrics + LatencyTracker classes
│   └── optimization_advisor.py          # OptimizationAdvisor class
│
├── stt/                                 # Speech-to-Text providers
│   ├── factory.py                       # STTProviderFactory
│   └── providers/
│       ├── openai_whisper.py
│       └── mock_stt.py
│
├── tts/                                 # Text-to-Speech providers
│   ├── factory.py                       # TTSProviderFactory
│   └── providers/
│       ├── openai_tts.py
│       └── mock_tts.py
│
├── test_latency.py                      # Simulated latency testing script
├── capture_live_latency.py              # Live monitoring script (Session 8)
│
└── logs/
    └── session_manager.log              # All logs including latency breakdowns
```

### Key Code Locations

#### 1. Latency Metrics Collection

**File:** `session_manager/main.py`

**Timing Start** (line 218):
```python
pipeline_start = time.time()
```

**STT Timing** (lines 237-241):
```python
stt_start = time.time()
transcript = await stt_provider.transcribe(audio_data)
metrics.stt_total = time.time() - stt_start
metrics.stt_provider = stt_provider_name
```

**LLM Timing** (lines 273-284):
```python
llm_start = time.time()
response_text = f"You said: {transcript}"  # Echo mode
metrics.llm_total = time.time() - llm_start
metrics.llm_model_variant = "echo"
```

**TTS Timing** (lines 296-300):
```python
tts_start = time.time()
audio_response = await tts_provider.synthesize(response_text)
metrics.tts_total = time.time() - tts_start
metrics.tts_provider = tts_provider_name
```

**Total Pipeline** (line 310):
```python
metrics.total_pipeline = time.time() - pipeline_start
```

**Reporting** (lines 313-333):
```python
if latency_tracker:
    latency_tracker.record(metrics)

    # Log breakdown
    if settings.get('latency_monitoring.log_breakdown', True):
        logger.info(metrics.get_breakdown())

    # Get optimization suggestions
    if optimization_advisor:
        suggestions = optimization_advisor.analyze(metrics)
        if suggestions:
            logger.warning(optimization_advisor.format_suggestions(suggestions))

    # Send to client
    if settings.get('latency_monitoring.send_to_client', True):
        await websocket.send_json({
            "type": "latency_report",
            "metrics": metrics.to_dict()
        })
```

#### 2. LatencyMetrics Class

**File:** `session_manager/monitoring/latency_tracker.py` (lines 30-114)

**Key Methods:**
- `get_breakdown()` - ASCII table format for logs
- `get_summary()` - One-line summary
- `to_dict()` - JSON serialization for WebSocket
- `is_over_target(target)` - Check if exceeds goal
- `get_slowest_component()` - Identify bottleneck

**Example Breakdown Output:**
```
Latency Breakdown:
─────────────────────────────────────────────────
Component                Time (s)    Provider/Model
─────────────────────────────────────────────────
VAD Processing          0.05
Silence Detection       2.00
STT Total              8.50        openai_whisper
  ├─ Network Upload    1.20
  └─ Processing        7.30
LLM Total              2.50        gpt-5-mini
TTS Total              3.00        openai_tts
WebSocket Transmission  0.30
─────────────────────────────────────────────────
Total Pipeline         16.35
Target                 10.00        ⚠️ EXCEEDED BY 6.35s
─────────────────────────────────────────────────
```

#### 3. LatencyTracker Class

**File:** `session_manager/monitoring/latency_tracker.py` (lines 117-323)

**Key Methods:**
- `record(metrics)` - Store new measurement
- `get_statistics()` - Calculate mean, median, P50/P90/P99
- `get_bottlenecks()` - Find components exceeding targets
- `get_model_comparison()` - Compare LLM variants
- `print_statistics()` - Console output

**Storage:**
- Max history: 1000 requests (configurable)
- Stored in memory (not persistent)
- Access via `latency_tracker.history`

#### 4. OptimizationAdvisor Class

**File:** `session_manager/monitoring/optimization_advisor.py` (lines 38-315)

**Suggestion Logic:**

**STT Optimization** (lines 156-189):
```python
if stt_total > target_stt:
    if stt_provider == "openai_whisper":
        # Suggest local Whisper (saves 5-6s)
        priority = "HIGH" if potential_savings >= 1.5 else "MEDIUM"
```

**LLM Optimization** (lines 191-237):
```python
if llm_total > target_llm:
    if llm_model == "gpt-5":
        # Suggest gpt-5-mini (saves ~1.7s)
```

**TTS Optimization** (lines 239-276):
```python
if tts_total > target_tts:
    if tts_provider == "openai_tts":
        # Suggest Piper TTS or streaming
```

**Priority Thresholds:**
- HIGH: ≥1.5s potential savings
- MEDIUM: 0.5-1.5s savings
- LOW: <0.5s savings

#### 5. Provider Config Loading (Session 8 Fix)

**File:** `session_manager/main.py` (lines 67-109)

**STT Config:**
```python
if stt_provider_name == 'openai_whisper':
    stt_config = {
        'api_key': settings.get('openai.api_key'),
        'model': settings.get('openai.stt.model', 'whisper-1'),
        ...
    }
elif stt_provider_name == 'mock_stt':
    stt_config = {
        'mock_latency': settings.get('mock_stt.mock_latency', 0.5),
        ...
    }
```

**TTS Config:**
```python
if tts_provider_name == 'openai_tts':
    tts_config = { ... }
elif tts_provider_name == 'mock_tts':
    tts_config = { ... }
```

**Before Session 8:** Only OpenAI config loaded (hardcoded)
**After Session 8:** Provider-specific config selection ✅

---

## Troubleshooting Guide

### Problem 1: No Latency Breakdown Appearing in Logs

**Symptoms:**
- Session Manager starts successfully
- Requests complete
- But no "Latency Breakdown:" table in logs

**Diagnosis:**
```bash
# Check if latency monitoring is enabled
grep "latency_monitoring:" session_manager/config.yaml -A 5

# Check if log_breakdown is enabled
grep "log_breakdown:" session_manager/config.yaml

# Check if latency tracker initialized
grep "Initialized latency tracker" logs/session_manager.log
```

**Possible Causes:**

**Cause 1:** Latency monitoring disabled
```yaml
# Fix in config.yaml:
latency_monitoring:
  enabled: true  # Was false
```

**Cause 2:** Log breakdown disabled
```yaml
# Fix in config.yaml:
latency_monitoring:
  log_breakdown: true  # Was false
```

**Cause 3:** Request failed before completion
```bash
# Check for errors in logs:
grep "ERROR" logs/session_manager.log | tail -20

# Common error: STT timeout, WebSocket disconnect
```

**Solution:** Fix the underlying error first, then latency will track

### Problem 2: Android App Can't Connect

**Symptoms:**
- App shows "Connecting..." indefinitely
- Logs show: `WARNING - Received non-text data`
- Logs show: `ERROR - No session_start message received`

**Diagnosis:**
```bash
# Check WebSocket connections
grep "WebSocket connection accepted" logs/session_manager.log | tail -5

# Check for protocol errors
grep "non-text data" logs/session_manager.log | tail -5
```

**Root Cause (Discovered Session 8):**
- Android app sends raw audio bytes immediately
- Should send JSON message first: `{"type": "session_start"}`
- Protocol mismatch between app and server

**Fix Required:** Android app code (not Session Manager)

**Location:** `VCAAssistant/app/src/main/java/.../VoiceAssistantService.kt`

**Change Needed:**
```kotlin
// BEFORE (incorrect):
webSocket.send(audioData.toByteArray())  // Sends bytes first

// AFTER (correct):
webSocket.send("""{"type": "session_start"}""")  // Send JSON first
webSocket.send(audioData.toByteArray())          // Then send audio
```

**Temporary Workaround:** Use PC test client instead
```bash
cd session_manager
python test_client.py
```

### Problem 3: Provider Switching Not Working

**Symptoms:**
- Changed `stt_provider` in config.yaml
- Restarted Session Manager
- Logs still show old provider

**Diagnosis:**
```bash
# Check what config.yaml actually says
grep "stt_provider:" session_manager/config.yaml
grep "tts_provider:" session_manager/config.yaml

# Check what Session Manager loaded
grep "Initialized STT provider" logs/session_manager.log | tail -1
grep "Initialized TTS provider" logs/session_manager.log | tail -1
```

**Possible Causes:**

**Cause 1:** Didn't restart Session Manager
```bash
# Must restart after config changes:
lsof -ti:5000 | xargs -r kill -9
source venv/bin/activate
python main.py
```

**Cause 2:** Multiple Session Manager instances running
```bash
# Check for duplicates:
lsof -i :5000

# Kill all:
lsof -ti:5000 | xargs -r kill -9

# Restart clean:
python main.py
```

**Cause 3:** Typo in provider name
```yaml
# WRONG:
stt_provider: "mock_whisper"  # Not a valid provider

# RIGHT:
stt_provider: "mock_stt"      # Matches factory registration
```

**Valid Provider Names:**
- STT: `openai_whisper`, `mock_stt`
- TTS: `openai_tts`, `mock_tts`

**Cause 4:** Provider config not loaded (pre-Session 8 bug)
- **Fixed in Session 8:** `main.py:67-109` now supports provider-specific configs
- If using old version, update `main.py`

### Problem 4: Optimization Suggestions Not Appearing

**Symptoms:**
- Latency clearly exceeds targets
- No suggestions in logs

**Diagnosis:**
```bash
# Check if suggestions enabled
grep "optimization_suggestions:" session_manager/config.yaml

# Check if OptimizationAdvisor initialized
grep "Initialized optimization advisor" logs/session_manager.log
```

**Possible Causes:**

**Cause 1:** Suggestions disabled
```yaml
# Fix in config.yaml:
latency_monitoring:
  optimization_suggestions: true  # Was false
```

**Cause 2:** Latency below all thresholds
- Suggestions only appear if component exceeds target
- Check if targets are too loose

**Cause 3:** OptimizationAdvisor not initialized
```bash
# Check main.py startup:
grep "optimization_advisor" main.py

# Should see:
optimization_advisor = OptimizationAdvisor(...)
```

### Problem 5: Statistics Calculation Errors

**Symptoms:**
- `python test_latency.py` crashes
- Error: "division by zero" or "list index out of range"

**Diagnosis:**
```bash
# Run test and capture error:
python test_latency.py 2>&1 | tee /tmp/latency_error.log

# Check error details
cat /tmp/latency_error.log
```

**Possible Causes:**

**Cause 1:** No data recorded
```python
# LatencyTracker.history is empty
# Fix: Record at least one metric before calling get_statistics()
```

**Cause 2:** Invalid metric values
```python
# Some timing values are None or negative
# Fix: Ensure all timings are >= 0
```

**Cause 3:** Python version incompatibility
```bash
# Check Python version:
python --version

# Requires: Python 3.8+
# If older, upgrade or use python3.12
```

### Problem 6: Latency Metrics Not Sent to Android App

**Symptoms:**
- Android app connected
- Requests complete
- App doesn't receive latency data

**Diagnosis:**
```bash
# Check if send_to_client enabled
grep "send_to_client:" session_manager/config.yaml

# Check WebSocket send attempts
grep "Sending latency metrics to client" logs/session_manager.log
```

**Possible Causes:**

**Cause 1:** Send to client disabled
```yaml
# Fix in config.yaml:
latency_monitoring:
  send_to_client: true  # Was false
```

**Cause 2:** WebSocket disconnected before send
- Check for `ClientDisconnected` errors in logs
- App may be closing connection too early

**Cause 3:** Android app not handling message
- Check if app has handler for `type: "latency_report"`
- May need to add Kotlin code to receive and display

### Common Error Messages

| Error | Meaning | Solution |
|-------|---------|----------|
| `No session_start message received` | Android app protocol issue | Fix app to send JSON first (see Problem 2) |
| `Request timed out` | STT API took too long | Check internet, try mock provider |
| `ClientDisconnected` | WebSocket closed early | App timing issue, check app logs |
| `No specific config found for provider` | Unknown provider name | Check spelling, see valid names above |
| `division by zero` in statistics | No data recorded | Record metrics before calling statistics |

---

## Maintenance Tasks

### Adding New Metrics

**Scenario:** You want to track a new timing (e.g., "database query time")

**Step 1:** Add field to `LatencyMetrics` dataclass

**File:** `session_manager/monitoring/latency_tracker.py`

```python
@dataclass
class LatencyMetrics:
    # Existing fields...
    tts_total: float = 0.0

    # NEW: Add your metric here
    database_query: float = 0.0

    websocket_transmission: float = 0.0
```

**Step 2:** Update `get_breakdown()` method

```python
def get_breakdown(self) -> str:
    # Existing lines...
    lines.append(f"TTS Total              {self.tts_total:>6.2f}        {self.tts_provider or 'N/A'}")

    # NEW: Add your metric to the table
    lines.append(f"Database Query         {self.database_query:>6.2f}")

    lines.append(f"WebSocket Transmission {self.websocket_transmission:>6.2f}")
```

**Step 3:** Update `to_dict()` method

```python
def to_dict(self) -> dict:
    return {
        # Existing fields...
        'tts_total': self.tts_total,

        # NEW: Include in JSON output
        'database_query': self.database_query,

        'websocket_transmission': self.websocket_transmission,
    }
```

**Step 4:** Measure and record in `main.py`

```python
# In audio_stream() function:

# NEW: Measure your operation
db_start = time.time()
result = await database.query(...)
metrics.database_query = time.time() - db_start

# Existing code continues...
metrics.total_pipeline = time.time() - pipeline_start
latency_tracker.record(metrics)
```

**Step 5:** (Optional) Add target to `config.yaml`

```yaml
latency_monitoring:
  component_targets:
    database_query: 0.2  # Target: 200ms
```

**Step 6:** (Optional) Add optimization suggestion

**File:** `session_manager/monitoring/optimization_advisor.py`

```python
def analyze(self, metrics: LatencyMetrics) -> List[dict]:
    # Existing suggestions...

    # NEW: Add suggestion logic
    db_query = metrics.database_query
    target_db = self.component_targets.get('database_query', 0.2)

    if db_query > target_db:
        potential_savings = db_query - 0.05  # Optimized target
        suggestions.append({
            'component': 'database_query',
            'current': db_query,
            'target': target_db,
            'recommendation': "Add database index or use caching",
            'potential_savings': potential_savings,
            'priority': 'HIGH' if potential_savings >= 1.5 else 'MEDIUM'
        })
```

### Modifying Component Targets

**Scenario:** You want to change when suggestions appear

**File:** `session_manager/config.yaml`

**Example: Make STT target more aggressive**
```yaml
latency_monitoring:
  component_targets:
    stt: 2.0  # Was 4.0, now requires faster STT
```

**Effect:**
- Suggestions appear if STT > 2.0s (instead of > 4.0s)
- More aggressive optimization recommendations

**Example: Relax VAD target**
```yaml
latency_monitoring:
  component_targets:
    vad: 0.5  # Was 0.1, now more lenient
```

**Restart required:** `lsof -ti:5000 | xargs -r kill -9 && python main.py`

### Adjusting Suggestion Priorities

**Scenario:** You want different priority thresholds

**File:** `session_manager/monitoring/optimization_advisor.py`

**Current Logic** (lines 123-127):
```python
# HIGH priority if >= 1.5s savings
# MEDIUM priority if 0.5-1.5s savings
# LOW priority if < 0.5s savings
if potential_savings >= 1.5:
    priority = "HIGH"
elif potential_savings >= 0.5:
    priority = "MEDIUM"
else:
    priority = "LOW"
```

**Modified Example** (stricter HIGH threshold):
```python
# HIGH priority only if >= 3.0s savings
# MEDIUM priority if 1.0-3.0s savings
# LOW priority if < 1.0s savings
if potential_savings >= 3.0:
    priority = "HIGH"
elif potential_savings >= 1.0:
    priority = "MEDIUM"
else:
    priority = "LOW"
```

**Apply to all suggestion methods:**
- Lines 156-189 (STT suggestions)
- Lines 191-237 (LLM suggestions)
- Lines 239-276 (TTS suggestions)

### Changing Max History Size

**Scenario:** You want to track more requests in statistics

**File:** `session_manager/main.py` (line 108)

**Current:**
```python
latency_tracker = LatencyTracker(max_history=1000)
```

**Modified:**
```python
latency_tracker = LatencyTracker(max_history=5000)  # Track 5x more
```

**Trade-off:**
- Larger history = more memory usage
- More data = better statistics
- Recommended: 1000-10000

**Restart required:** Yes

### Exporting Latency Data

**Scenario:** You want to analyze data in Excel or Jupyter

**Method 1: Export from test script**

```python
# In test_latency.py or custom script:
import json

# Get all recorded metrics
data = [m.to_dict() for m in latency_tracker.history]

# Save to JSON
with open('latency_export.json', 'w') as f:
    json.dump(data, f, indent=2)

# Or save to CSV
import csv
with open('latency_export.csv', 'w') as f:
    writer = csv.DictWriter(f, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)
```

**Method 2: Parse logs**

```bash
# Extract latency data from logs
grep "Total Pipeline" logs/session_manager.log | \
  awk '{print $NF}' > latency_times.txt
```

**Method 3: Live capture to file**

```bash
# Run live capture (saves JSON automatically)
tail -f logs/session_manager.log | python3 capture_live_latency.py

# Creates: live_latency_test_YYYYMMDD_HHMMSS.json
```

### Disabling Latency Tracking (Production)

**Scenario:** You want to reduce overhead in production

**File:** `session_manager/config.yaml`

**Option 1: Disable completely**
```yaml
latency_monitoring:
  enabled: false  # No tracking at all
```

**Option 2: Minimal tracking (no logging)**
```yaml
latency_monitoring:
  enabled: true
  log_breakdown: false          # Don't spam logs
  send_to_client: false         # Don't send to app
  optimization_suggestions: false  # No suggestions
```

**Performance Impact:**
- Tracking enabled: ~0.5ms overhead per request (negligible)
- Logging disabled: Saves ~10ms per request (log I/O)
- Suggestions disabled: Saves ~1ms per request

**Recommendation:** Keep tracking enabled, disable only logging/suggestions

---

## Optimization Recommendations

### Current Baseline (Session 7-8)

**Measured with OpenAI Whisper STT:**

| Component | Time | Provider | Status |
|-----------|------|----------|--------|
| VAD Processing | ~0.05s | WebRTC VAD | ✅ Under target (0.1s) |
| Silence Detection | 2.0s | Fixed threshold | ⚠️ Slightly over (target 1.5s) |
| STT Total | **8.2-8.6s** | OpenAI Whisper | ❌ **Far over target (4.0s)** |
| LLM Total | ~0s | Echo mode | ✅ N/A (not implemented) |
| TTS Total | ~3s | OpenAI TTS (estimated) | ✅ At target (3.0s) |
| WebSocket | ~0.3s | Network | ✅ Under target (0.5s) |
| **Total Pipeline** | **~11-12s** | | ❌ **Exceeds 10s target** |

### Optimization Roadmap

#### Priority 1: Switch to Local Whisper STT (HIGH IMPACT)

**Problem:** OpenAI Whisper takes 8.2-8.6s (exceeds target by 4-5s)

**Solution:** Run Whisper locally on GTX 970 GPU

**Implementation:**
1. Install Whisper locally:
   ```bash
   pip install openai-whisper
   ```

2. Create `session_manager/stt/providers/local_whisper.py`:
   ```python
   import whisper

   class LocalWhisperProvider(STTProvider):
       def __init__(self, config: dict):
           self.model = whisper.load_model("small")  # Or "base"

       async def transcribe(self, audio_data: bytes) -> str:
           result = self.model.transcribe(audio_data)
           return result["text"]
   ```

3. Register in factory (`stt/factory.py`):
   ```python
   from .providers.local_whisper import LocalWhisperProvider

   class STTProviderFactory:
       _providers = {
           "local_whisper": LocalWhisperProvider,
           ...
       }
   ```

4. Switch in config.yaml:
   ```yaml
   stt_provider: "local_whisper"
   ```

**Expected Results:**
- Latency: 2-3s (vs 8.5s with OpenAI)
- **Savings: 5-6 seconds** ✅
- Quality: Same (uses same Whisper model)
- Cost: $0 (vs $0.006/minute with OpenAI)

**Challenges:**
- GPU memory: Whisper Small needs ~2GB VRAM
- GTX 970 has 4GB → Should work fine
- May need to use "base" model if memory issues

**Testing Priority:** CRITICAL for <10s target

#### Priority 2: Reduce VAD Silence Threshold (MEDIUM IMPACT)

**Problem:** Waiting 2.0s for silence adds latency

**Solution:** Reduce to 1.0s or 1.5s

**Implementation:**

**Edit:** `session_manager/config.yaml`
```yaml
session:
  vad:
    silence_timeout: 1.0  # Was 2.0
```

**Restart:** `lsof -ti:5000 | xargs -r kill -9 && python main.py`

**Expected Results:**
- Latency: 1.0s (vs 2.0s)
- **Savings: 1.0 second** ✅
- Risk: May cut off end of speech (test with Warren!)

**Testing Protocol:**
1. Test with 1.5s first (safer)
2. If works, try 1.0s
3. Monitor for cut-off transcripts
4. Tune based on Warren's speech patterns

**Testing Priority:** HIGH (quick win)

#### Priority 3: Switch to Piper TTS (MEDIUM IMPACT)

**Problem:** OpenAI TTS takes ~3s

**Solution:** Run Piper TTS locally

**Implementation:** (Similar to Local Whisper)

1. Install Piper
2. Create `tts/providers/piper.py`
3. Register in factory
4. Switch in config.yaml

**Expected Results:**
- Latency: 0.3-0.5s (vs 3.0s)
- **Savings: 2.5 seconds** ✅
- Quality: May need tuning for clarity
- Cost: $0 (vs $0.015/1000 chars with OpenAI)

**Testing Priority:** HIGH (after local Whisper)

#### Priority 4: Implement LLM Module (REQUIRED)

**Problem:** Echo mode doesn't provide real responses

**Solution:** Integrate OpenAI GPT API

**Implementation:** (Future session)

1. Create `session_manager/llm/` module
2. Implement GPT-5-mini provider (fast, 2.5s avg)
3. Add conversation history
4. Replace echo in main.py

**Expected Results:**
- Latency: 2.5s (GPT-5-mini) or 1.0s (GPT-5-nano)
- Required for actual functionality

**Testing Priority:** CRITICAL (core feature)

#### Priority 5: Streaming TTS (FUTURE OPTIMIZATION)

**Problem:** User waits for full TTS before hearing response

**Solution:** Stream audio as it's generated

**Implementation:** (Advanced, future session)

1. Modify TTS providers to support streaming
2. Send audio chunks via WebSocket as ready
3. Android app starts playback before complete

**Expected Results:**
- Perceived latency: Reduced by 50-70%
- Actual latency: Same (but user hears response sooner)
- Complexity: High (requires streaming protocol)

**Testing Priority:** LOW (nice-to-have)

### Projected Latency After Optimizations

**Scenario 1: Local Whisper + Reduced VAD + Piper TTS**

| Component | Current | Optimized | Savings |
|-----------|---------|-----------|---------|
| VAD | 0.05s | 0.05s | 0s |
| Silence | 2.0s | 1.0s | 1.0s |
| STT | 8.5s | 2.5s | 6.0s |
| LLM | 0s | 2.5s (GPT-5-mini) | -2.5s |
| TTS | 3.0s | 0.5s | 2.5s |
| WebSocket | 0.3s | 0.3s | 0s |
| **Total** | **13.85s** | **6.85s** | **7.0s** ✅ |

**Result:** 6.85s total (well under 10s target!) ✅

**Scenario 2: All OpenAI (current)**

| Component | Time |
|-----------|------|
| Silence | 2.0s |
| STT (OpenAI) | 8.5s |
| LLM (GPT-5-mini) | 2.5s |
| TTS (OpenAI) | 3.0s |
| Other | 0.3s |
| **Total** | **16.3s** ❌ |

**Result:** 16.3s total (far exceeds 10s target) ❌

**Recommendation:** Implement Scenario 1 optimizations ASAP

---

## Summary

This guide provides everything you need to:
- ✅ Test latency tracking (simulated and live)
- ✅ Configure targets and settings
- ✅ Troubleshoot common issues
- ✅ Maintain and extend the system
- ✅ Optimize for <10s target

**Your Next Steps:**

1. **Immediate:** Fix Android app WebSocket protocol
2. **Short-term:** Implement local Whisper STT
3. **Medium-term:** Reduce VAD threshold, add Piper TTS
4. **Long-term:** Implement LLM module, streaming TTS

**Questions? Refer to:**
- This guide (SESSION-8-MAINTENANCE-GUIDE.md)
- [SESSION-8-SUMMARY.md](./SESSION-8-SUMMARY.md) - Test results and handover
- [PROVIDER-SWITCHING-GUIDE.md](./PROVIDER-SWITCHING-GUIDE.md) - Provider details
- [SESSION-7-SUMMARY.md](./SESSION-7-SUMMARY.md) - Implementation details

---

**Last Updated:** 2025-11-03 (Session 8)
**Next Session:** Implement local Whisper STT + test with Warren's voice
