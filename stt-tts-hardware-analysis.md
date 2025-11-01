# STT/TTS Hardware Analysis & Recommendation
**VCA 1.0 - Session 3**
**Date:** 2025-11-01

## Your PC Specifications

### Hardware Summary
| Component | Specification | Assessment |
|-----------|---------------|------------|
| **CPU** | Intel Core i7-4770 (4th gen, 2013) | Moderate - 8 threads @ 3.40GHz |
| **RAM** | 7.7 GB in WSL2 (16 GB system total) | ✅ Good for local models |
| **GPU** | NVIDIA GeForce GTX 970 | **✅ EXCELLENT for local AI!** |
| **VRAM** | 4 GB GDDR5 | Good for Whisper medium/small |
| **CUDA** | Version 12.6 support | ✅ Enabled and ready |
| **Disk** | 902 GB free | ✅ Plenty of space |

### GPU Performance Details
- **Model**: GeForce GTX 970 (Maxwell architecture)
- **CUDA Cores**: 1664
- **Memory**: 4096 MB (1542 MB currently used by display)
- **Power Draw**: 29W idle / 250W max
- **Temperature**: 38°C (healthy)
- **Driver**: 560.94 (current, supports CUDA 12.6)
- **Status**: ✅ GPU detected and functional in WSL2

## STT/TTS Performance Assessment

### 🎯 RECOMMENDATION: **Hybrid Approach - Local Primary with Cloud Fallback**

Your GTX 970 is **MORE than capable** of running local STT/TTS efficiently. Here's why:

### Local STT: Whisper (OpenAI model, run locally)

#### Performance Estimate on GTX 970

| Whisper Model | VRAM Usage | Speed (RTX) | Your GTX 970 (estimated) | Quality | Recommendation |
|---------------|------------|-------------|-------------------------|---------|----------------|
| **tiny** | ~1 GB | ~32x realtime | ~15-20x realtime | Basic (acceptable) | ❌ Too inaccurate for NZ accent |
| **base** | ~1 GB | ~16x realtime | ~8-12x realtime | Fair | ⚠️ May struggle with accent |
| **small** | ~2 GB | ~6x realtime | **~3-5x realtime** | **Good** | **✅ RECOMMENDED** |
| **medium** | ~5 GB | ~2x realtime | ~1-1.5x realtime | Very Good | ⚠️ Tight VRAM (4GB total) |
| **large-v3** | ~10 GB | ~1x realtime | ❌ Won't fit | Best | ❌ Insufficient VRAM |

**Best choice: Whisper Small**
- **Speed**: 3-5x realtime = ~0.2-0.3 seconds per second of audio (fast enough for conversation)
- **Accuracy**: Good, especially with fine-tuning for NZ accent
- **VRAM**: ~2GB (comfortable fit with 4GB total)
- **Latency**: Acceptable for hands-free assistant (<1 second for 3-second utterance)

### Local TTS: Piper

#### Performance Estimate on GTX 970

| Aspect | Performance | Notes |
|--------|-------------|-------|
| **Speed** | ~0.15-0.25s per sentence | Very fast, even on CPU |
| **Quality** | Natural, comparable to cloud | Multiple voice options |
| **VRAM Usage** | <500 MB (can run on CPU too) | Minimal resources |
| **Voices** | 50+ languages, accents | NZ English available |
| **Latency** | Near-instant | No network delay |

**Verdict: ✅ Excellent choice for local TTS**

### Cloud Alternative: OpenAI (Your existing API key)

#### OpenAI Whisper API (STT)
- **Cost**: $0.006 per minute (~$0.36/hour of audio)
- **Latency**: 1-3 seconds (network + processing)
- **Accuracy**: Excellent for NZ accent (same Whisper large-v3 model)
- **Pros**: No local compute, always latest model
- **Cons**: Requires internet, privacy concerns (audio sent to cloud), ongoing cost

#### OpenAI TTS API
- **Cost**: $15 per 1M characters (~$0.015 per 1000 words)
- **Latency**: 1-2 seconds (network + processing)
- **Voices**: 6 voices (alloy, echo, fable, onyx, nova, shimmer)
- **Quality**: Very natural, high quality
- **Pros**: Excellent quality, no local compute
- **Cons**: Requires internet, privacy concerns, ongoing cost

## Usage Cost Comparison

### Scenario: Dad uses VCA for 2 hours/day (moderate usage)

#### Option 1: Local Only (Whisper Small + Piper)
- **Initial Setup**: 1-2 hours (install, configure)
- **Ongoing Cost**: $0/month
- **Privacy**: ✅ All audio stays local
- **Internet Required**: No (works offline)
- **GPU Load**: Moderate (GTX 970 handles easily)
- **Latency**: Low (~0.3-0.5s total)

#### Option 2: Cloud Only (OpenAI Whisper + TTS)
- **Initial Setup**: 15 minutes (API key only)
- **Ongoing Cost**: ~$20-40/month
  - STT: 60 hours/month × $0.006/min = ~$21.60/month
  - TTS: ~5000 words/day × 30 days × $0.015/1000 = ~$2.25/month
- **Privacy**: ⚠️ Audio sent to OpenAI (encrypted)
- **Internet Required**: Yes (fails when offline)
- **GPU Load**: None
- **Latency**: Medium (~1.5-3s total)

#### Option 3: Hybrid (Local primary, Cloud fallback) **✅ RECOMMENDED**
- **Initial Setup**: 2-3 hours
- **Ongoing Cost**: ~$2-5/month (fallback usage only)
- **Privacy**: ✅ Mostly local, cloud only when needed
- **Internet Required**: 95% works offline
- **GPU Load**: Moderate when home, none when away
- **Latency**: Low at home, medium when away

## Detailed Recommendation

### Phase 1-2: Start with Cloud (Quick MVP)
**Why**: Get the assistant working quickly while building local pipeline

```yaml
Configuration:
  STT: OpenAI Whisper API
  TTS: OpenAI TTS API (voice: "onyx" or "nova")
  Cost: ~$20-40/month
  Setup Time: 15 minutes

Benefits:
  - Immediate functionality
  - Test conversation flow and persona
  - Validate Dad's usage patterns
  - Focus on session manager logic
```

### Phase 3-4: Add Local Pipeline (Cost Optimization)
**Why**: Your GTX 970 can handle it, reduce costs to near-zero

```yaml
Configuration:
  STT Primary: Whisper Small (local, GPU-accelerated)
  STT Fallback: OpenAI Whisper API (when PC offline or high load)
  TTS Primary: Piper (local, fast)
  TTS Fallback: OpenAI TTS API (when PC offline)
  Cost: ~$2-5/month (fallback only)
  Setup Time: 2-3 hours

Benefits:
  - Near-zero ongoing cost (95% local)
  - Privacy-first (audio stays home)
  - Low latency at home
  - Graceful degradation when PC offline
  - Full control over models and voices
```

## GPU Workload Analysis

### GTX 970 Capacity Check

**Current State:**
- Display usage: 1542 MB VRAM
- Available for AI: ~2500 MB VRAM
- GPU Utilization: 27% (Windows display)

**Expected Load with Whisper Small + Piper:**
- Whisper Small: ~2000 MB VRAM (during transcription)
- Piper TTS: ~300 MB VRAM or CPU fallback
- **Total**: ~2300 MB (fits comfortably)

**Realistic Usage Pattern:**
- STT active: 2-5 seconds per utterance (not continuous)
- GPU idle: 95% of the time (waiting for Dad to speak)
- Thermal impact: Minimal (38°C idle → ~55-60°C during processing)
- Power: +20-50W during processing bursts

**Verdict: ✅ GTX 970 can easily handle this workload**

### Will Your PC "Struggle"?

**Short answer: NO - Your PC is well-suited for local STT/TTS**

**Detailed analysis:**

#### ✅ GPU: GTX 970 (Excellent)
- Maxwell architecture still very capable for inference
- 4GB VRAM sufficient for Whisper Small/Base
- CUDA support means massive speedup vs. CPU-only
- Not continuous load (only processes when Dad speaks)

#### ⚠️ CPU: i7-4770 (Moderate)
- 4th gen (2013) but still 8 threads @ 3.4GHz
- Adequate for session manager logic
- NOT recommended for CPU-only Whisper (too slow)
- Perfect for everything except heavy AI inference

#### ✅ RAM: 16 GB System (7.7 GB allocated to WSL2)
- **System total**: 16 GB (good headroom)
- **WSL2 allocation**: 7.7 GB (can be increased via .wslconfig if needed)
- **Currently available**: 3.5 GB (healthy)
- Whisper models loaded into VRAM, not RAM
- Sufficient for session manager + Home Assistant + AnythingLLM
- **Note**: WSL2 memory can be increased by editing `C:\Users\<username>\.wslconfig` if needed

#### ✅ Storage: 902 GB free (Plenty)
- Whisper models: ~1-3 GB per model
- Piper voices: ~50-100 MB each
- No concerns here

**Bottleneck assessment:**
- **CPU-only Whisper**: Would struggle (0.3-0.5x realtime = unacceptable lag)
- **GPU-accelerated Whisper**: Runs great (3-5x realtime = very responsive)
- **Piper TTS**: Lightning fast even on CPU

**The GTX 970 GPU transforms your "moderate" PC into an "excellent" local AI platform.**

## Implementation Roadmap

### Phase 1-2: Cloud STT/TTS (Quick Start)
```bash
# No installation needed, just use OpenAI API
# Configure in session manager:
STT_PROVIDER=openai
STT_API_KEY=sk-proj-...
TTS_PROVIDER=openai
TTS_VOICE=nova
```

**Timeline**: Already done (you have API key)

### Phase 3: Add Local Whisper (GPU)
```bash
# Install faster-whisper with GPU support
pip install faster-whisper

# Install CUDA toolkit (if not present)
# Already have CUDA 12.6 support via nvidia-smi

# Download Whisper Small model
python3 -c "from faster_whisper import WhisperModel; model = WhisperModel('small', device='cuda', compute_type='float16')"

# Test performance
# Expected: 3-5x realtime on GTX 970
```

**Timeline**: Phase 3 (after memory foundation), ~2 hours

### Phase 4: Add Local Piper TTS
```bash
# Install via Home Assistant Supervisor add-on
# or standalone via Docker:
docker pull rhasspy/wyoming-piper

docker run -d \
  --name piper \
  -p 10200:10200 \
  -v ~/piper-data:/data \
  rhasspy/wyoming-piper \
  --voice en_NZ-aotearoa-medium
```

**Timeline**: Phase 4 (alongside RAG), ~1 hour

### Phase 5: Implement Hybrid Fallback Logic
```python
# Pseudocode for session manager
def transcribe_audio(audio_data):
    try:
        # Try local Whisper first
        if is_home_network() and gpu_available():
            return whisper_local.transcribe(audio_data)
    except Exception as e:
        log_warning(f"Local STT failed: {e}")

    # Fallback to cloud
    return openai.audio.transcriptions.create(
        model="whisper-1",
        file=audio_data
    )
```

**Timeline**: Phase 5 (automations), ~1-2 hours

## Privacy Considerations

### Local STT/TTS (Recommended for Privacy)
✅ Audio never leaves your PC
✅ No third-party access to Dad's conversations
✅ Full control over data retention
✅ Complies with "Privacy Pack" requirements in VCA plan
✅ No upload bandwidth used

### Cloud STT/TTS (Convenience Trade-off)
⚠️ Audio sent to OpenAI servers (encrypted in transit)
⚠️ Subject to OpenAI's data policies (30-day retention, then deleted)
⚠️ Potential privacy concern for sensitive conversations
⚠️ Requires trust in third-party provider
✅ Can opt out of training data usage (OpenAI API default)

**For Dad's use case (personal assistant with safety/health info):**
- **Recommendation**: Prioritize local processing
- **Justification**: VCA will handle personal info (contacts, health, safety protocols)
- **Implementation**: Hybrid approach gives both privacy AND reliability

## Final Recommendation Summary

### ✅ Recommended Approach: **Hybrid Local-Primary**

**Phase 1-2 (Now - Next 2 weeks):**
- Use OpenAI API for both STT and TTS
- Get the assistant working quickly
- Measure actual usage patterns
- **Cost**: ~$20-40/month
- **Setup**: Already complete (have API key)

**Phase 3-4 (Weeks 3-6):**
- Deploy Whisper Small on GTX 970 GPU
- Deploy Piper TTS (local)
- Keep OpenAI as automatic fallback
- **Cost**: ~$2-5/month (5% cloud fallback)
- **Setup**: 3-4 hours total

**Long-term (Production):**
- 95% local processing (privacy + cost)
- 5% cloud fallback (reliability when PC offline)
- Best of both worlds

### Why This Works for Your PC

1. **GTX 970 GPU is perfect for Whisper Small**
   - 3-5x realtime = responsive conversation
   - Low latency (<1 second typical)
   - Only active during speech (not constant load)

2. **RAM and CPU are adequate**
   - Session manager is lightweight
   - GPU handles heavy lifting (not CPU)

3. **Cost optimization**
   - $0/month after initial setup
   - Cloud fallback only when needed

4. **Privacy-first**
   - Aligns with VCA design goals
   - Dad's health/safety data stays home

5. **Offline capable**
   - Works during internet outages
   - Supports 95% uptime requirement

## Next Steps

1. **Phase 1-2**: Continue with OpenAI API (already configured)
2. **Monitor usage**: Track API costs for 1-2 weeks
3. **Phase 3 decision point**: If monthly cost >$15, prioritize local deployment
4. **GPU setup**: Install faster-whisper with CUDA support
5. **Benchmark**: Test Whisper Small performance on GTX 970
6. **Gradual transition**: Switch to hybrid once local pipeline tested

## Technical Notes

### Whisper Small Model Details
- **Parameters**: 244 million
- **Languages**: 99 (including English)
- **Disk Size**: ~967 MB
- **VRAM**: ~2 GB (float16 precision)
- **Accuracy**: WER ~4-5% on clean English (acceptable for NZ accent)

### Piper TTS Model Details
- **NZ English Voice**: `en_NZ-aotearoa-medium`
- **Quality**: 22kHz, natural prosody
- **Speed**: ~150ms per sentence (very fast)
- **Size**: ~80 MB per voice
- **Voices Available**: Multiple NZ accents and genders

### Performance Testing Commands

```bash
# Test Whisper GPU performance
time python3 -c "
from faster_whisper import WhisperModel
model = WhisperModel('small', device='cuda')
segments, info = model.transcribe('test_audio.wav')
for segment in segments:
    print(segment.text)
"

# Expected output: <1 second for 3-second audio clip

# Monitor GPU during processing
watch -n 1 nvidia-smi
```

## References
- [faster-whisper GitHub](https://github.com/guillaumekln/faster-whisper) - GPU-accelerated Whisper
- [Piper TTS](https://github.com/rhasspy/piper) - Local neural TTS
- [OpenAI Whisper Pricing](https://openai.com/pricing) - Cloud alternative costs
- [GTX 970 Specs](https://www.techpowerup.com/gpu-specs/geforce-gtx-970.c2620) - GPU capabilities
- [vca1.0-implementation-plan.md](vca1.0-implementation-plan.md) - VCA architecture decisions

---

**Bottom Line: Your GTX 970 makes local STT/TTS very viable. Start with cloud for quick MVP, then transition to local for privacy and cost savings. Your PC will NOT struggle with this workload.**
