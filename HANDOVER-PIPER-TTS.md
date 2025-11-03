# HANDOVER: Piper TTS Implementation for VCA Session Manager

**Date**: 2025-11-03
**From**: Session 10 (PyTorch Whisper implementation)
**For**: Next session - Piper TTS implementation
**Status**: PyTorch Whisper STT ✅ operational, Piper TTS ⏳ pending

---

## Current State

### What's Working ✅

1. **PyTorch Whisper STT**:
   - 3.13s latency on GTX 970 (Maxwell) GPU
   - FP32 mode operational
   - 63% faster than OpenAI API baseline
   - Under 4s target
   - Configuration: [config.yaml:184-196](session_manager/config.yaml#L184-196)
   - Provider: [pytorch_whisper.py](session_manager/stt/providers/pytorch_whisper.py)

2. **Provider Factory Pattern**:
   - STT factory: [stt/factory.py](session_manager/stt/factory.py)
   - TTS factory: [tts/factory.py](session_manager/tts/factory.py)
   - Config-driven provider switching functional

3. **Latency Tracking**:
   - Automatic provider name + P50/P90/P99 metrics
   - Database: [monitoring/metrics.db](session_manager/monitoring/metrics.db)
   - Working for STT, ready for TTS integration

4. **Session Manager**:
   - WebSocket server operational
   - Android client compatible
   - Echo response for testing
   - Main entry point: [main.py](session_manager/main.py)

### Current TTS Provider

**OpenAI TTS** (to be replaced):
- Provider: [tts/providers/openai_tts.py](session_manager/tts/providers/openai_tts.py)
- Latency: Not yet measured (estimated 1-2s)
- Model: tts-1
- Voice: alloy
- API-based (requires network)

---

## Mission: Implement Piper TTS

### Objectives

1. **Primary**: Reduce TTS latency to ~0.5s (target)
2. **Secondary**: Eliminate OpenAI API dependency for TTS
3. **Tertiary**: Explore GPU acceleration on GTX 970 (if supported)

### Success Criteria

- [ ] Piper TTS provider created and registered in factory
- [ ] Configuration added to config.yaml
- [ ] Test script validates functionality and latency
- [ ] Latency ≤1s (stretch goal: ≤0.5s)
- [ ] Audio quality acceptable for conversational assistant
- [ ] Live testing with session manager + Android phone successful
- [ ] Latency tracking integration verified

---

## Piper TTS Overview

### What is Piper?

**Piper** is a fast, local neural TTS system designed for real-time applications like voice assistants.

- **GitHub**: https://github.com/rhasspy/piper
- **Models**: https://huggingface.co/rhasspy/piper-voices
- **License**: MIT
- **Language**: C++ with Python bindings
- **Dependencies**: ONNX Runtime

### Key Features

- **Fast**: Optimized for low-latency inference (100-500ms typical)
- **Local**: Runs entirely offline, no API calls
- **High Quality**: Neural TTS with natural-sounding voices
- **Lightweight**: Models range from 10-60MB
- **Multi-voice**: Many English voices available (male/female, accents)
- **ONNX Runtime**: CPU acceleration standard, GPU possible

### Piper Architecture

```
Text Input
    ↓
Phonemization (text → phonemes)
    ↓
ONNX Model (phonemes → mel spectrogram)
    ↓
Vocoder (mel → audio waveform)
    ↓
PCM16 Audio Output (16kHz or 22kHz)
```

---

## GTX 970 Considerations

### GPU Acceleration for Piper

**Status**: ⚠️ **UNCERTAIN** - Requires investigation

#### Factors to Consider:

1. **ONNX Runtime GPU Support**:
   - ONNX Runtime supports CUDA acceleration
   - Requires CUDA Execution Provider
   - May require additional CUDA libraries

2. **Maxwell Architecture Limitations**:
   - Piper models may be FP16-optimized (like CTranslate2)
   - GTX 970 is 64x slower at FP16 than FP32
   - Need to verify if ONNX Runtime enforces FP32 on Maxwell

3. **Performance Expectations**:
   - **CPU inference**: 100-500ms (likely sufficient)
   - **GPU inference**: 50-200ms (if supported)
   - **Risk**: GPU may not improve latency if models are FP16-only

### Recommendation

**Start with CPU inference**:
- Piper is already optimized for low latency on CPU
- 100-500ms latency meets ≤1s target
- Avoid Maxwell FP16 complications (learned from Whisper)
- GPU acceleration can be explored later if CPU insufficient

**If pursuing GPU**:
1. Check if Piper/ONNX Runtime supports FP32 mode on CUDA
2. Verify GTX 970 compatibility before installation
3. Have CPU fallback ready

---

## Implementation Plan

### Phase 1: Research and Validation (30-60 min)

#### Tasks:
1. **Read Piper documentation**:
   - Installation requirements
   - Python API usage
   - Model selection guide
   - Audio format requirements

2. **Check ONNX Runtime compatibility**:
   - CPU inference requirements
   - CUDA support (optional)
   - GTX 970 compatibility (if pursuing GPU)

3. **Select voice model**:
   - Browse: https://huggingface.co/rhasspy/piper-voices
   - Recommended: `en_US-lessac-medium` (good quality, ~30MB)
   - Alternative: `en_US-amy-medium` (female voice)
   - Download model + config files

4. **Verify audio format compatibility**:
   - VCA expects: PCM16, 16kHz mono
   - Piper outputs: PCM16, 16kHz or 22kHz
   - Resampling needed if 22kHz model chosen

#### Research Questions:
- Does Piper Python package exist, or need to call CLI?
- What's the cleanest integration: library vs subprocess?
- Are there hidden dependencies or system libraries?

### Phase 2: Installation (15-30 min)

#### Expected Steps:

```bash
cd /home/indigo/my-project3/Dappva/session_manager
source venv/bin/activate

# Install Piper Python package (if available)
pip install piper-tts
# OR
pip install piper-phonemize onnxruntime

# Download voice model
mkdir -p models/piper
cd models/piper
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json
cd ../..

# Test Piper CLI (if using CLI approach)
echo "Hello, this is a test." | piper --model models/piper/en_US-lessac-medium.onnx --output_file test.wav
```

#### Potential Issues:
- **Missing phonemization library**: May need `espeak-ng` system package
  ```bash
  sudo apt-get update
  sudo apt-get install espeak-ng
  ```
- **ONNX Runtime conflicts**: May need specific onnxruntime version
- **Path issues**: Ensure model paths are absolute or relative to working directory

### Phase 3: PiperTTSProvider Implementation (45-90 min)

#### File to Create:
**`session_manager/tts/providers/piper_tts.py`**

#### Provider Structure:

```python
"""
Piper TTS Provider
Local neural TTS with low latency for VCA.
VCA 1.0 - Session 11
"""

import asyncio
import io
import logging
import wave
import numpy as np
from pathlib import Path
from typing import Optional

# Import will depend on Piper Python API
# Option 1: Direct library import
# from piper import PiperVoice
# Option 2: Subprocess to CLI
# import subprocess

from ..base import TTSProvider, AudioResult

logger = logging.getLogger(__name__)


class PiperTTSProvider(TTSProvider):
    """Piper TTS provider with CPU/GPU acceleration"""

    def __init__(self, config: dict):
        super().__init__(config)

        # Extract config
        self.model_path = config.get('model_path')
        self.speaker_id = config.get('speaker_id', None)
        self.length_scale = config.get('length_scale', 1.0)
        self.noise_scale = config.get('noise_scale', 0.667)
        self.noise_w = config.get('noise_w', 0.8)
        self.use_cuda = config.get('use_cuda', False)

        logger.info(
            f"Initializing PiperTTSProvider: model={self.model_path}, "
            f"use_cuda={self.use_cuda}"
        )

        # Load Piper model
        # TODO: Implement based on Piper Python API
        # self.voice = PiperVoice.load(self.model_path, use_cuda=self.use_cuda)

    async def synthesize(self, text: str) -> AudioResult:
        """
        Synthesize text to speech using Piper.

        Args:
            text: Text to synthesize

        Returns:
            AudioResult with PCM16 audio bytes

        Raises:
            Exception: If synthesis fails
        """
        # Run in thread pool (TTS is CPU/GPU intensive)
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            self._synthesize_sync,
            text
        )

        return result

    def _synthesize_sync(self, text: str) -> AudioResult:
        """
        Synchronous synthesis (runs in thread pool).

        Args:
            text: Text to synthesize

        Returns:
            AudioResult with audio bytes and metadata
        """
        try:
            # TODO: Implement based on Piper Python API
            # Option 1: Library API
            # audio_np = self.voice.synthesize(text, ...)

            # Option 2: CLI subprocess
            # result = subprocess.run([
            #     'piper',
            #     '--model', self.model_path,
            #     '--output_raw'  # Get raw PCM instead of WAV
            # ], input=text.encode(), capture_output=True, check=True)
            # audio_bytes = result.stdout

            # Convert to WAV format (VCA expects WAV container)
            # sample_rate = 16000  # or 22050 if using 22kHz model
            # audio_wav = self._to_wav(audio_bytes, sample_rate)

            # Calculate duration
            # duration = len(audio_np) / sample_rate

            logger.debug(f"Synthesized {len(text)} chars → {duration:.2f}s audio")

            return AudioResult(
                audio_bytes=audio_wav,
                sample_rate=sample_rate,
                duration=duration,
                format='wav'
            )

        except Exception as e:
            logger.error(f"Piper TTS synthesis failed: {e}")
            raise

    def _to_wav(self, audio_data: bytes, sample_rate: int) -> bytes:
        """Convert raw PCM16 to WAV format."""
        wav_io = io.BytesIO()
        with wave.open(wav_io, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_data)
        return wav_io.getvalue()

    def __repr__(self) -> str:
        return f"PiperTTSProvider(model='{self.model_path}', use_cuda={self.use_cuda})"
```

#### Key Implementation Notes:

1. **Audio Format**:
   - Piper outputs raw PCM16
   - VCA expects WAV container (header + PCM16 data)
   - Use `_to_wav()` helper to wrap raw audio

2. **Async Pattern**:
   - Use `asyncio.run_in_executor()` (same as PyTorch Whisper)
   - Prevents blocking event loop during synthesis

3. **Error Handling**:
   - Catch and log exceptions
   - Re-raise to trigger fallback (if implemented)

4. **Metadata**:
   - Calculate duration: `len(audio_samples) / sample_rate`
   - Return sample_rate for resampling if needed

### Phase 4: Factory Registration (5 min)

#### File to Modify:
**`session_manager/tts/factory.py`**

```python
from .providers.piper_tts import PiperTTSProvider

class TTSProviderFactory:
    _providers = {
        'openai_tts': OpenAITTSProvider,
        'mock_tts': MockTTSProvider,
        'piper_tts': PiperTTSProvider,  # ← ADD THIS
    }
```

### Phase 5: Configuration (10 min)

#### File to Modify:
**`session_manager/config.yaml`**

Add Piper configuration section:

```yaml
# TTS Provider Configuration
tts_provider: "piper_tts"  # ← Change from "openai_tts"

# ... existing config ...

# Piper TTS Configuration (Session 11)
piper_tts:
  model_path: "models/piper/en_US-lessac-medium.onnx"
  speaker_id: null         # Some models support multiple speakers
  length_scale: 1.0        # Speaking speed (1.0 = normal, 0.8 = faster, 1.2 = slower)
  noise_scale: 0.667       # Variance in speech (higher = more expressive)
  noise_w: 0.8             # Variance in durations (higher = more natural rhythm)
  use_cuda: false          # GPU acceleration (start with false for GTX 970)
```

#### Parameter Guide:

- **model_path**: Path to .onnx model file (absolute or relative to session_manager/)
- **speaker_id**: For multi-speaker models (usually null for single-speaker)
- **length_scale**: Speaking speed
  - 1.0 = normal speed
  - 0.8 = 25% faster (may improve latency, test for quality)
  - 1.2 = slower (may improve clarity for Dad)
- **noise_scale**: Expressiveness (0.5-1.0 recommended)
- **noise_w**: Rhythm variation (0.5-1.0 recommended)
- **use_cuda**: Set to false initially (CPU inference)

#### File to Modify:
**`session_manager/main.py`**

Add Piper TTS config loading:

```python
# Around line 120 (after pytorch_whisper config block)

elif tts_provider_name == 'piper_tts':
    tts_config = {
        'model_path': settings.get('piper_tts.model_path'),
        'speaker_id': settings.get('piper_tts.speaker_id', None),
        'length_scale': settings.get('piper_tts.length_scale', 1.0),
        'noise_scale': settings.get('piper_tts.noise_scale', 0.667),
        'noise_w': settings.get('piper_tts.noise_w', 0.8),
        'use_cuda': settings.get('piper_tts.use_cuda', False)
    }
```

### Phase 6: Test Script (30 min)

#### File to Create:
**`session_manager/test_piper_tts.py`**

```python
"""
Quick test script for Piper TTS provider
Tests synthesis and measures latency
"""

import asyncio
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from tts.factory import TTSProviderFactory
from config.settings import get_settings


async def test_piper_tts():
    """Test Piper TTS provider with sample text"""

    print("="*70)
    print("PIPER TTS PROVIDER TEST")
    print("="*70)

    # Load settings
    settings = get_settings()

    # Create piper_tts provider
    tts_config = {
        'model_path': settings.get('piper_tts.model_path'),
        'speaker_id': settings.get('piper_tts.speaker_id', None),
        'length_scale': settings.get('piper_tts.length_scale', 1.0),
        'noise_scale': settings.get('piper_tts.noise_scale', 0.667),
        'noise_w': settings.get('piper_tts.noise_w', 0.8),
        'use_cuda': settings.get('piper_tts.use_cuda', False)
    }

    print(f"\n📋 Configuration:")
    for key, value in tts_config.items():
        print(f"   {key}: {value}")

    print(f"\n🔄 Initializing PiperTTSProvider...")
    start_init = time.time()
    provider = TTSProviderFactory.create('piper_tts', tts_config)
    init_time = time.time() - start_init
    print(f"✓ Provider initialized in {init_time:.2f}s")
    print(f"   {provider}")

    # Test synthesis
    test_text = "Hello! This is a test of the Piper text to speech system. How do I sound?"

    print(f"\n📝 Test text: \"{test_text}\"")
    print(f"   Length: {len(test_text)} characters")

    print(f"\n🔊 Synthesizing...")
    start = time.time()
    result = await provider.synthesize(test_text)
    latency = time.time() - start

    # Display results
    print(f"\n" + "="*70)
    print("RESULTS")
    print("="*70)
    print(f"🎵 Audio size: {len(result.audio_bytes) / 1024:.1f} KB")
    print(f"🎚️  Sample rate: {result.sample_rate} Hz")
    print(f"⏱️  Duration: {result.duration:.2f}s")
    print(f"⚡ Latency: {latency:.2f}s")

    if result.duration:
        realtime_factor = latency / result.duration
        print(f"📊 Realtime Factor: {realtime_factor:.2f}x (lower is better)")

        if realtime_factor < 0.5:
            print(f"   💚 EXCELLENT: Much faster than realtime!")
        elif realtime_factor < 1.0:
            print(f"   ✅ GOOD: Faster than realtime")
        elif realtime_factor < 2.0:
            print(f"   ⚠️  OK: Slower than realtime but acceptable")
        else:
            print(f"   ❌ SLOW: Much slower than realtime")

    print("="*70)

    # Compare to target
    target_tts_latency = 1.0  # From config (stretch goal: 0.5s)
    if latency < target_tts_latency:
        savings = target_tts_latency - latency
        print(f"\n✅ UNDER TARGET: {latency:.2f}s < {target_tts_latency:.2f}s (saved {savings:.2f}s)")
    else:
        overage = latency - target_tts_latency
        print(f"\n⚠️  OVER TARGET: {latency:.2f}s > {target_tts_latency:.2f}s (exceeded by {overage:.2f}s)")

    # Save audio for manual verification
    output_path = Path(__file__).parent / 'test_piper_output.wav'
    with open(output_path, 'wb') as f:
        f.write(result.audio_bytes)
    print(f"\n💾 Audio saved: {output_path.name}")
    print(f"   Play with: aplay {output_path.name}")
    print()


if __name__ == "__main__":
    asyncio.run(test_piper_tts())
```

#### Run Test:

```bash
cd /home/indigo/my-project3/Dappva/session_manager
source venv/bin/activate
python test_piper_tts.py

# Listen to output
aplay test_piper_output.wav
```

### Phase 7: Live Testing (30-60 min)

#### Steps:

1. **Start session manager**:
   ```bash
   cd /home/indigo/my-project3/Dappva/session_manager
   source venv/bin/activate
   python main.py
   ```

2. **Check logs for Piper initialization**:
   - Should see: `Initializing PiperTTSProvider: model=...`
   - Should see: `✓ Provider initialized`

3. **Connect Android phone**:
   - VCAAssistant app
   - Connect to session manager WebSocket
   - Verify connection

4. **Test echo response**:
   - Say: "Hello, can you hear me?"
   - Listen for synthesized response
   - Check audio quality

5. **Measure latency**:
   - Monitor logs for latency metrics
   - Check `monitoring/metrics.db`:
     ```bash
     sqlite3 monitoring/metrics.db "SELECT provider, COUNT(*), AVG(latency_ms) FROM tts_latencies GROUP BY provider;"
     ```

6. **Iterate if needed**:
   - Adjust `length_scale` for speed/quality tradeoff
   - Try different voice models
   - Enable GPU if CPU insufficient (and compatible)

---

## Troubleshooting Guide

### Issue 1: Piper Installation Fails

**Symptom**: `pip install piper-tts` fails or package not found

**Possible Causes**:
- Package name incorrect
- No Python package (CLI only)

**Solutions**:
1. Check official Piper docs for Python installation
2. Try: `pip install piper-phonemize onnxruntime`
3. Fall back to CLI subprocess approach if no Python package
4. Compile from source if necessary (see Piper GitHub)

### Issue 2: Missing espeak-ng

**Symptom**: Error about phonemization or espeak-ng not found

**Solution**:
```bash
# WSL/Ubuntu
sudo apt-get update
sudo apt-get install espeak-ng

# Verify
espeak-ng --version
```

### Issue 3: Model Download Fails

**Symptom**: 404 or network error downloading .onnx model

**Solution**:
1. Check HuggingFace model repository is accessible
2. Download manually via browser, copy to `models/piper/`
3. Use `wget` with correct URL (check for redirects)
4. Ensure both `.onnx` and `.onnx.json` files downloaded

### Issue 4: Audio Format Mismatch

**Symptom**: Static, distorted audio, or playback errors

**Possible Causes**:
- Wrong sample rate (22kHz model but VCA expects 16kHz)
- Incorrect PCM format (not 16-bit)
- WAV header missing or malformed

**Solutions**:
1. Check model config (.onnx.json) for sample_rate
2. Resample if needed:
   ```python
   import librosa
   import soundfile as sf

   audio, sr = librosa.load(audio_path, sr=None)
   audio_16k = librosa.resample(audio, orig_sr=sr, target_sr=16000)
   sf.write('output_16k.wav', audio_16k, 16000, subtype='PCM_16')
   ```
3. Verify WAV header with: `file test_piper_output.wav`
4. Use `_to_wav()` helper to ensure correct format

### Issue 5: High Latency (>1s)

**Symptom**: Synthesis takes longer than target

**Possible Causes**:
- Large model (>50MB)
- Inefficient phonemization
- CPU underperforming

**Solutions**:
1. Try smaller model (e.g., `-low` quality variant)
2. Increase `length_scale` to 0.8 (faster speaking speed)
3. Check CPU usage during synthesis (should be high)
4. Investigate GPU acceleration (if compatible with GTX 970)
5. Profile with: `python -m cProfile test_piper_tts.py`

### Issue 6: Poor Audio Quality

**Symptom**: Robotic, garbled, or unnatural-sounding speech

**Possible Causes**:
- Model quality too low
- Incorrect noise_scale / noise_w parameters
- Audio corruption during processing

**Solutions**:
1. Try higher quality model (`-high` variant)
2. Adjust parameters:
   ```yaml
   noise_scale: 0.667  # Default
   noise_w: 0.8        # Default
   ```
3. Test with longer, natural sentences (short text may sound robotic)
4. Verify audio file plays correctly: `aplay test_piper_output.wav`

### Issue 7: GPU Acceleration Not Working

**Symptom**: `use_cuda: true` has no effect or crashes

**Possible Causes**:
- ONNX Runtime CUDA provider not installed
- Maxwell FP16 issue (like faster-whisper)
- Piper models require specific CUDA features

**Solutions**:
1. **Don't prioritize GPU** - CPU latency likely sufficient
2. If pursuing GPU:
   ```bash
   pip install onnxruntime-gpu
   ```
3. Check ONNX Runtime docs for CUDA EP requirements
4. Verify with:
   ```python
   import onnxruntime as ort
   print(ort.get_available_providers())
   # Should include 'CUDAExecutionProvider'
   ```
5. If FP16 errors appear, stick with CPU (Maxwell limitation)

---

## Success Validation Checklist

After implementation, verify:

- [ ] **Installation**: Piper and dependencies installed in venv
- [ ] **Model Download**: .onnx and .onnx.json files present in models/piper/
- [ ] **Provider Class**: PiperTTSProvider created and functional
- [ ] **Factory Registration**: piper_tts registered in TTSProviderFactory
- [ ] **Configuration**: piper_tts section in config.yaml, tts_provider switched
- [ ] **Test Script**: test_piper_tts.py runs successfully
- [ ] **Audio Quality**: test_piper_output.wav sounds natural
- [ ] **Latency Target**: Synthesis latency ≤1s (ideally ≤0.5s)
- [ ] **Live Testing**: Session manager + Android phone echo response works
- [ ] **Latency Tracking**: metrics.db contains piper_tts latency entries
- [ ] **End-to-End**: Total pipeline (STT + TTS + other) under 10s target

---

## Reference Files

### Existing VCA Files to Reference:

- **STT Provider Example**: [stt/providers/pytorch_whisper.py](session_manager/stt/providers/pytorch_whisper.py)
- **TTS Base Class**: [tts/base.py](session_manager/tts/base.py)
- **TTS Factory**: [tts/factory.py](session_manager/tts/factory.py)
- **OpenAI TTS Provider** (current): [tts/providers/openai_tts.py](session_manager/tts/providers/openai_tts.py)
- **Config Settings**: [config.yaml](session_manager/config.yaml)
- **Main Entry Point**: [main.py](session_manager/main.py)

### External Resources:

- **Piper GitHub**: https://github.com/rhasspy/piper
- **Piper Voice Models**: https://huggingface.co/rhasspy/piper-voices
- **ONNX Runtime Docs**: https://onnxruntime.ai/docs/
- **ONNX Runtime Python API**: https://onnxruntime.ai/docs/api/python/

---

## Post-Implementation: Documentation Tasks

After Piper TTS is operational:

1. **Update SESSION-11-SUMMARY.md**:
   - Document Piper implementation
   - Record latency results
   - Note any GTX 970 GPU findings
   - Compare to OpenAI TTS baseline

2. **Update PROVIDER-SWITCHING-GUIDE.md**:
   - Add piper_tts provider documentation
   - Update latency targets with actual results
   - Document voice model selection

3. **Update CHANGELOG.md**:
   - Record Piper TTS implementation
   - Note dependency changes (onnxruntime, espeak-ng, etc.)

4. **Create PHASE-3-COMPLETION-STATUS.md** (if both STT + TTS local):
   - Mark Phase 3 (Local STT/TTS) as complete
   - Document total pipeline latency
   - Plan Phase 4 next steps

---

## Expected Timeline

| Phase | Task | Time Estimate |
|-------|------|---------------|
| 1 | Research + validation | 30-60 min |
| 2 | Installation | 15-30 min |
| 3 | PiperTTSProvider implementation | 45-90 min |
| 4 | Factory registration | 5 min |
| 5 | Configuration | 10 min |
| 6 | Test script | 30 min |
| 7 | Live testing | 30-60 min |
| **Total** | | **2.5-4.5 hours** |

**Recommendation**: Budget 4 hours for first implementation, including troubleshooting time.

---

## Key Learnings from PyTorch Whisper (Apply to Piper)

1. **Start with CPU**: Avoid GPU complications until CPU performance validated
2. **Check architecture compatibility**: Maxwell has limitations (FP16 penalty)
3. **Venv installation preferred**: No system library installations if possible
4. **Test early, test often**: Create test script before live integration
5. **Document parameters**: Tuning options important for optimization
6. **Use async pattern**: `run_in_executor()` prevents event loop blocking
7. **Validate audio format**: VCA expects PCM16 16kHz mono in WAV container

---

## Questions to Answer During Implementation

1. **Does Piper have a Python package, or must we use CLI subprocess?**
   - Impacts implementation complexity and error handling

2. **What's the actual CPU latency for Piper on this hardware?**
   - Determines if GPU acceleration is necessary

3. **Which voice model provides best quality/latency tradeoff?**
   - May need to test 2-3 models

4. **Does Piper support FP32 mode on CUDA for Maxwell GPUs?**
   - Critical for GPU acceleration (if pursued)

5. **Are there any hidden system dependencies beyond espeak-ng?**
   - Impacts installation complexity and reproducibility

---

## Emergency Fallback Plan

If Piper implementation encounters major blockers:

1. **Revert to OpenAI TTS**: Already functional, keep as backup
2. **Document blockers**: Note specific errors for future sessions
3. **Explore alternatives**:
   - **Coqui TTS**: Another local neural TTS (heavier dependencies)
   - **espeak-ng**: Fast but robotic (not ideal for VCA)
   - **Festival**: Classic TTS (poor quality)
4. **Defer to Phase 4**: Mark as future optimization, focus on other tasks

**Don't spend >6 hours troubleshooting** - document issues and move forward.

---

## Contact Points for Next Session

### What to Ask Me (Previous Session):

- "Did you encounter any Piper-specific issues during research?"
  - **Answer**: No research conducted yet - this is your starting point

- "Are there any VCA architecture changes needed for TTS?"
  - **Answer**: No - provider factory already supports plug-and-play TTS providers

- "What audio format does VCA expect?"
  - **Answer**: PCM16, 16kHz mono, WAV container format

### What to Report Back:

- Actual Piper latency results (target: ≤1s)
- Audio quality assessment (subjective: Does it sound natural?)
- Any installation issues encountered
- GTX 970 GPU compatibility findings (if investigated)
- Total pipeline latency (STT + TTS + other)

---

## Final Notes

**Remember**:
- PyTorch Whisper achieved 3.13s (under 4s target) ✅
- Piper TTS needs to achieve ≤1s to reach ≤10s total pipeline
- CPU inference is likely sufficient - don't overcomplicate with GPU
- Dad's use case prioritizes accuracy and naturalness over speed
- Test with live session manager + phone to validate real-world performance

**Good luck with the implementation!** This handover document should provide everything needed to continue where Session 10 left off.

---

**Handover Status**: ✅ COMPLETE
**Next Session Start**: Phase 1 (Research and Validation)
