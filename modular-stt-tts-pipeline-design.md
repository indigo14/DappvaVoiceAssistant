# Modular STT/TTS Pipeline Design
**VCA 1.0 - Critical Architecture Decision**
**Date:** 2025-11-01
**Session:** 3

## Context & Requirements

### Dad's Speech Challenge
- **Key constraint**: Dad's speech is sometimes slurred and unclear for human listeners
- **Critical requirement**: STT system must handle non-standard speech patterns
- **Design implication**: Pipeline MUST support easy model swapping for experimentation
- **Success criteria**: Ability to understand Dad's speech is paramount - will determine final STT choice

### Design Philosophy
**"Build for experimentation, not commitment"**

The STT/TTS pipeline must be:
1. **Model-agnostic**: Swap between OpenAI, Whisper variants, Deepgram, etc. with config change only
2. **Provider-agnostic**: Cloud vs. local switching should be seamless
3. **Testable**: Easy A/B testing with same audio samples
4. **Documented**: Clear comparison metrics for each model tried
5. **Fallback-capable**: Graceful degradation when primary model fails

### Testing Priority
> "We may want to experiment further with STT to find a good fit for user."

This is **not** a "set and forget" decision. The pipeline architecture must support:
- Testing multiple STT models with Dad's actual speech
- Recording accuracy metrics per model
- Quick model switching without code changes
- Hybrid approaches (e.g., cloud for unclear speech, local for clear)

## Modular Pipeline Architecture

### Layer 1: Audio Interface (Model-Independent)
**Purpose**: Capture and prepare audio in standardized format

```
┌─────────────────────────────────────────────────┐
│          Audio Capture & Preprocessing          │
│  (Phone → WebSocket → Audio Buffer)             │
│                                                  │
│  Output: Standardized PCM/WAV @ 16kHz mono      │
└─────────────────────────────────────────────────┘
                       │
                       ▼
```

**Key Design Points:**
- Output format: 16kHz, 16-bit, mono PCM (universal STT input)
- No model-specific preprocessing at this layer
- Reusable audio buffer for A/B testing

### Layer 2: STT Provider Abstraction
**Purpose**: Unified interface for all STT models

```python
# Abstract base class
class STTProvider(ABC):
    @abstractmethod
    def transcribe(self, audio_data: bytes) -> TranscriptionResult:
        """
        Transcribe audio to text.

        Args:
            audio_data: Raw audio bytes (16kHz, 16-bit, mono)

        Returns:
            TranscriptionResult with text, confidence, metadata
        """
        pass

    @abstractmethod
    def get_metadata(self) -> dict:
        """Return provider name, model, version, capabilities"""
        pass
```

**TranscriptionResult Schema:**
```python
@dataclass
class TranscriptionResult:
    text: str                    # Transcribed text
    confidence: float            # 0.0 - 1.0 confidence score
    language: str                # Detected/specified language
    processing_time: float       # Seconds taken
    provider: str                # Which STT provider was used
    model: str                   # Specific model name/version
    metadata: dict               # Provider-specific extras
    segments: List[Segment]      # Word-level timings (if available)

@dataclass
class Segment:
    start: float                 # Start time in audio
    end: float                   # End time in audio
    text: str                    # Segment text
    confidence: float            # Segment confidence
```

### Layer 3: Concrete STT Implementations
**Purpose**: Model-specific providers (plug-and-play)

```
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  OpenAI Whisper  │  │  Local Whisper   │  │   Deepgram API   │
│   (Cloud API)    │  │   (GPU/faster)   │  │     (Cloud)      │
└──────────────────┘  └──────────────────┘  └──────────────────┘
         │                     │                      │
         └─────────────────────┴──────────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  STT Provider Pool  │
                    │  (Registry Pattern) │
                    └─────────────────────┘
```

#### Supported Providers (Planned)

| Provider | Type | Models | Slurred Speech Potential | Priority |
|----------|------|--------|-------------------------|----------|
| **OpenAI Whisper API** | Cloud | large-v3 | ✅ Excellent (best baseline) | **Phase 1** |
| **Local Whisper** | Local GPU | tiny/base/small/medium | ✅ Good (v3 fine-tuned) | **Phase 3** |
| **Deepgram** | Cloud | nova-2, enhanced | ✅ Good (medical/accent models) | Testing |
| **Google Cloud STT** | Cloud | chirp, latest_long | ⚠️ Unknown for NZ slurred | Testing |
| **Azure Speech** | Cloud | Neural voices | ⚠️ Unknown | Testing |
| **Vosk** | Local CPU | Small models | ⚠️ Lower accuracy | Fallback |
| **Coqui STT** | Local | Open source | ⚠️ Requires training | Advanced |

### Layer 4: Model Selection Engine
**Purpose**: Choose best STT provider based on context

```python
class STTRouter:
    def __init__(self, config: dict):
        self.providers = {}
        self.primary = config['primary_stt']
        self.fallback = config['fallback_stt']
        self.test_mode = config.get('test_mode', False)

    def transcribe(self, audio_data: bytes, context: dict = None) -> TranscriptionResult:
        """
        Route to appropriate STT provider based on:
        - Network availability (local vs cloud)
        - Audio clarity (confidence from previous utterances)
        - User preference (Dad may prefer certain voice)
        - Test mode (parallel A/B testing)
        """

        # Test mode: run multiple models in parallel for comparison
        if self.test_mode:
            return self._parallel_test(audio_data)

        # Normal mode: primary with fallback
        try:
            result = self.providers[self.primary].transcribe(audio_data)

            # Low confidence? Try fallback
            if result.confidence < 0.6:
                fallback_result = self.providers[self.fallback].transcribe(audio_data)
                if fallback_result.confidence > result.confidence:
                    return fallback_result

            return result

        except Exception as e:
            logger.warning(f"Primary STT failed: {e}, using fallback")
            return self.providers[self.fallback].transcribe(audio_data)
```

### Layer 5: TTS Provider Abstraction
**Purpose**: Unified interface for all TTS models

```python
class TTSProvider(ABC):
    @abstractmethod
    def synthesize(self, text: str, voice: str = None) -> TTSResult:
        """
        Convert text to speech audio.

        Args:
            text: Text to speak
            voice: Optional voice identifier

        Returns:
            TTSResult with audio data and metadata
        """
        pass

    @abstractmethod
    def list_voices(self) -> List[Voice]:
        """Return available voices for this provider"""
        pass

@dataclass
class TTSResult:
    audio_data: bytes            # PCM/WAV audio bytes
    sample_rate: int             # e.g., 24000 Hz
    format: str                  # 'wav', 'mp3', 'pcm'
    duration: float              # Seconds
    provider: str                # Which TTS provider
    voice: str                   # Voice identifier used
    processing_time: float       # Generation time
    metadata: dict               # Provider-specific extras
```

### Layer 6: Concrete TTS Implementations

| Provider | Type | Voices | Quality | Latency | Priority |
|----------|------|--------|---------|---------|----------|
| **OpenAI TTS** | Cloud | 6 voices | Excellent | 1-2s | **Phase 1** |
| **Piper** | Local | 50+ | Very Good | <0.2s | **Phase 3** |
| **ElevenLabs** | Cloud | Custom cloning | Excellent | 1-3s | Optional |
| **Coqui TTS** | Local | Custom | Good | 0.5-1s | Advanced |

## Configuration-Driven Model Selection

### config.yaml (Example)
```yaml
# VCA STT/TTS Configuration
# Change models here without code changes

stt:
  # Primary STT provider
  primary: "openai_whisper"

  # Fallback when primary fails or low confidence
  fallback: "local_whisper_small"

  # Test mode: run multiple models in parallel for comparison
  test_mode: false

  # Confidence threshold to trigger fallback
  confidence_threshold: 0.6

  # Provider-specific configs
  providers:
    openai_whisper:
      api_key: ${OPENAI_API_KEY}
      model: "whisper-1"
      language: "en"
      temperature: 0.0  # More deterministic for slurred speech

    local_whisper_small:
      model_size: "small"
      device: "cuda"
      compute_type: "float16"
      language: "en"
      beam_size: 5  # Higher for better accuracy with unclear speech

    local_whisper_medium:
      model_size: "medium"
      device: "cuda"
      compute_type: "float16"
      language: "en"
      beam_size: 5

    deepgram:
      api_key: ${DEEPGRAM_API_KEY}
      model: "nova-2"
      tier: "enhanced"  # Better for accents

    vosk_local:
      model_path: "./models/vosk-model-en-nz-0.22"
      sample_rate: 16000

tts:
  # Primary TTS provider
  primary: "openai_tts"

  # Fallback when primary fails
  fallback: "piper_local"

  # Provider-specific configs
  providers:
    openai_tts:
      api_key: ${OPENAI_API_KEY}
      voice: "nova"  # Dad may prefer different voice
      model: "tts-1"
      speed: 1.0  # Adjustable if Dad prefers slower speech

    piper_local:
      voice: "en_NZ-aotearoa-medium"
      speaker: 0
      length_scale: 1.0  # Speech speed
      noise_scale: 0.667
      noise_w: 0.8

# Model testing and comparison
testing:
  # Enable to record all transcriptions for comparison
  record_comparisons: true
  comparison_log: "./data/stt_comparisons.jsonl"

  # When enabled, run these models in parallel for every utterance
  parallel_test_models:
    - "openai_whisper"
    - "local_whisper_small"
    # - "deepgram"  # Uncomment to test

  # Save audio samples for later testing
  save_audio_samples: true
  sample_directory: "./data/audio_samples/"
```

## STT Model Comparison Framework

### A/B Testing Workflow

```python
class STTComparison:
    """Framework for comparing STT models on same audio samples"""

    def __init__(self, config_path: str):
        self.config = load_config(config_path)
        self.results_log = []

    def test_audio_sample(self, audio_path: str, ground_truth: str = None):
        """
        Test same audio across multiple STT models.

        Args:
            audio_path: Path to test audio file
            ground_truth: Known correct transcription (optional)
        """
        audio_data = load_audio(audio_path)
        results = {}

        for model_name in self.config['testing']['parallel_test_models']:
            provider = self.get_provider(model_name)

            start_time = time.time()
            result = provider.transcribe(audio_data)
            result.processing_time = time.time() - start_time

            results[model_name] = result

        # Calculate accuracy if ground truth provided
        if ground_truth:
            for model_name, result in results.items():
                result.wer = calculate_word_error_rate(result.text, ground_truth)
                result.accuracy = 1.0 - result.wer

        # Log results
        self.log_comparison(audio_path, results, ground_truth)

        return results

    def generate_comparison_report(self):
        """Generate markdown report comparing all tested models"""
        # Aggregate metrics across all test samples
        # Output: ./reports/stt_comparison_YYYYMMDD.md
        pass
```

### Comparison Metrics

For each STT model tested, track:

| Metric | Description | Importance for Slurred Speech |
|--------|-------------|-------------------------------|
| **Word Error Rate (WER)** | % words incorrectly transcribed | ⭐⭐⭐⭐⭐ Critical |
| **Confidence Score** | Model's self-reported confidence | ⭐⭐⭐ Useful for triggering fallback |
| **Processing Time** | Latency from audio → text | ⭐⭐⭐ Affects conversation flow |
| **Intelligibility** | Can VCA understand intent? | ⭐⭐⭐⭐⭐ Critical (measured via downstream success) |
| **Consistency** | Same audio → same text? | ⭐⭐⭐ Important for reliability |
| **Cost** | API charges or compute cost | ⭐⭐ Secondary to accuracy |

### Testing Protocol for Dad's Speech

```markdown
## STT Testing Protocol - Dad's Slurred Speech

### Phase 1: Baseline Establishment (Week 1-2)
1. Use OpenAI Whisper API as baseline (best accuracy expected)
2. Collect 20-30 sample utterances from Dad:
   - 10 clear speech samples
   - 10 moderately slurred samples
   - 10 heavily slurred samples
3. Record ground truth (what Dad intended to say)
4. Measure baseline WER and intelligibility

### Phase 2: Local Model Testing (Week 3-4)
1. Deploy Local Whisper Small on GTX 970
2. Re-run all 30 samples through local model
3. Compare WER, confidence, intelligibility
4. Identify which samples work better on which model

### Phase 3: Alternative Provider Testing (Week 5-6)
1. Test Deepgram Nova-2 Enhanced (medical/accent specialization)
2. Test Google Cloud Speech Chirp (if needed)
3. Compare against OpenAI and Local Whisper baselines

### Phase 4: Hybrid Strategy Tuning (Week 7-8)
1. Implement confidence-based routing:
   - If Whisper confidence >0.8 → use result
   - If confidence 0.6-0.8 → try secondary model
   - If confidence <0.6 → ask Dad to repeat
2. Measure improvement in intelligibility
3. Document optimal thresholds and fallback rules

### Success Criteria
- **Minimum acceptable WER**: <15% on clear speech, <30% on slurred
- **Intelligibility**: VCA understands intent ≥85% of the time
- **Dad's satisfaction**: Subjective rating ≥7/10 on "feels understood"
```

## Implementation Phases

### Phase 1: Cloud-Only with Comparison Logging (Week 1-2)
**Goal**: Get assistant working while collecting comparison data

```python
# session_manager/stt.py
stt_router = STTRouter(config={
    'primary_stt': 'openai_whisper',
    'fallback_stt': 'openai_whisper',  # Same provider (no local yet)
    'test_mode': False,
})

# But enable comparison logging
comparison_tracker = STTComparison(config_path='config.yaml')
comparison_tracker.config['testing']['record_comparisons'] = True
```

**Deliverable**: Working VCA + baseline STT performance data

### Phase 2: Add Local Whisper as Option (Week 3-4)
**Goal**: Deploy local model and run parallel tests

```python
# Add local provider
stt_router = STTRouter(config={
    'primary_stt': 'openai_whisper',
    'fallback_stt': 'local_whisper_small',
    'test_mode': True,  # Run both in parallel for comparison
})
```

**Deliverable**: WER comparison report, local model performance data

### Phase 3: Confidence-Based Hybrid (Week 5-6)
**Goal**: Optimize for Dad's speech patterns

```python
stt_router = STTRouter(config={
    'primary_stt': 'local_whisper_small',  # Fast, free, local
    'fallback_stt': 'openai_whisper',      # More accurate for slurred
    'confidence_threshold': 0.7,           # Tuned from testing
    'test_mode': False,
})
```

**Deliverable**: Production-ready hybrid STT with optimal model selection

### Phase 4: Continuous Improvement (Ongoing)
**Goal**: Adapt to Dad's speech over time

- Monthly WER analysis
- Collect edge cases (misunderstood utterances)
- Test new models (e.g., Whisper large-v3 when VRAM allows)
- Fine-tune local models on Dad's voice (advanced)

## Code Structure

```
vca1.0/
├── session_manager/
│   ├── audio/
│   │   ├── capture.py          # Layer 1: Audio interface
│   │   ├── preprocessor.py     # Normalize to 16kHz mono
│   │   └── vad.py              # Voice activity detection
│   ├── stt/
│   │   ├── base.py             # Layer 2: STTProvider abstract class
│   │   ├── providers/
│   │   │   ├── openai_whisper.py      # OpenAI Whisper API
│   │   │   ├── local_whisper.py       # faster-whisper GPU
│   │   │   ├── deepgram.py            # Deepgram API
│   │   │   ├── vosk.py                # Vosk local
│   │   │   └── __init__.py
│   │   ├── router.py           # Layer 4: Model selection engine
│   │   ├── comparison.py       # Testing framework
│   │   └── __init__.py
│   ├── tts/
│   │   ├── base.py             # Layer 5: TTSProvider abstract class
│   │   ├── providers/
│   │   │   ├── openai_tts.py          # OpenAI TTS API
│   │   │   ├── piper.py               # Piper local TTS
│   │   │   ├── elevenlabs.py          # ElevenLabs API
│   │   │   └── __init__.py
│   │   ├── router.py           # TTS selection engine
│   │   └── __init__.py
│   └── config.yaml             # All model configs here
├── data/
│   ├── audio_samples/          # Collected test samples
│   ├── stt_comparisons.jsonl   # Comparison results log
│   └── models/                 # Downloaded model files
├── tests/
│   ├── test_stt_providers.py   # Unit tests for each provider
│   ├── test_stt_router.py      # Test routing logic
│   └── test_audio_samples/     # Known-good test cases
└── reports/
    └── stt_comparison_YYYYMMDD.md  # Generated reports
```

## Documentation Requirements

### 1. Model Switching Guide
**File**: `docs/model-switching-guide.md`

```markdown
# How to Switch STT/TTS Models

## Change Primary STT Model

Edit `config.yaml`:
```yaml
stt:
  primary: "local_whisper_small"  # Change this line
```

Restart session manager:
```bash
docker restart session-manager
```

## Test New Model Before Switching

1. Add model to test list:
```yaml
testing:
  parallel_test_models:
    - "openai_whisper"
    - "local_whisper_small"
    - "deepgram"  # New model to test
```

2. Enable test mode:
```yaml
stt:
  test_mode: true
```

3. Have Dad speak to assistant
4. Review comparison report:
```bash
python scripts/generate_stt_report.py
```

5. Choose best performer and set as primary
```

### 2. STT Provider Documentation
**File**: `docs/stt-providers.md`

For each provider, document:
- Setup instructions (API keys, model downloads)
- Configuration options
- Performance characteristics (latency, accuracy)
- Cost structure
- Best use cases
- Limitations

### 3. Testing Protocol Documentation
**File**: `docs/testing-dad-speech.md`

- How to collect test samples
- Ground truth recording process
- Running comparison tests
- Interpreting results
- When to switch models

### 4. Troubleshooting Guide
**File**: `docs/stt-troubleshooting.md`

- Common transcription errors
- How to debug low confidence
- Network failures and fallback
- GPU memory issues (local Whisper)
- Provider-specific issues

## Key Design Principles

### 1. **Abstraction Over Commitment**
Never hardcode model-specific logic in session manager. Always use provider interface.

❌ **Bad**:
```python
# Hardcoded to OpenAI
import openai
result = openai.Audio.transcribe("whisper-1", audio_file)
```

✅ **Good**:
```python
# Model-agnostic
stt_provider = get_stt_provider(config['stt']['primary'])
result = stt_provider.transcribe(audio_data)
```

### 2. **Configuration Over Code**
Model selection via config file, not code changes.

### 3. **Comparison Over Guessing**
Always measure, never assume which model works best for Dad.

### 4. **Graceful Degradation**
If primary fails, fall back. If fallback fails, ask Dad to repeat.

### 5. **Privacy-First Fallback**
Default to local when possible, cloud when needed. Never the reverse.

## Success Metrics

### Technical Metrics
- **Model swap time**: <5 minutes (config change + restart)
- **Parallel testing overhead**: <2x latency (acceptable for testing phase)
- **Fallback reliability**: 99%+ (secondary model always available)

### User Experience Metrics
- **Dad's "feeling understood" score**: ≥7/10
- **Conversation success rate**: ≥85% (intent correctly interpreted)
- **Frustration events**: <1 per 10 interactions ("I have to repeat myself")

### Operational Metrics
- **Monthly STT cost**: <$10 (optimized via local primary)
- **Test samples collected**: ≥100 in first month
- **Model comparison reports**: Weekly during Phase 1-3

## Next Steps

1. **Phase 1 (Current)**:
   - ✅ Use OpenAI Whisper API (already set up)
   - ✅ Enable comparison logging
   - ⏳ Collect 30 test samples from Dad (Week 1-2)

2. **Phase 3 (Weeks 3-4)**:
   - Deploy Local Whisper Small on GTX 970
   - Run parallel comparison tests
   - Generate first comparison report

3. **Phase 5 (Weeks 5-6)**:
   - Test Deepgram or alternative if needed
   - Implement confidence-based hybrid routing
   - Optimize for Dad's speech patterns

4. **Ongoing**:
   - Monthly WER analysis
   - Quarterly model re-evaluation
   - Fine-tuning as new models emerge

## References
- [faster-whisper Documentation](https://github.com/guillaumekln/faster-whisper)
- [OpenAI Whisper API](https://platform.openai.com/docs/guides/speech-to-text)
- [Deepgram Nova-2](https://developers.deepgram.com/docs/nova-2)
- [Word Error Rate (WER) Calculation](https://en.wikipedia.org/wiki/Word_error_rate)
- [vca1.0-implementation-plan.md](vca1.0-implementation-plan.md)
- [stt-tts-hardware-analysis.md](stt-tts-hardware-analysis.md)

---

**Bottom Line**: The STT pipeline is built for experimentation, not permanence. Dad's ability to be understood drives all model selection decisions. The architecture makes switching models as easy as editing a config file.
