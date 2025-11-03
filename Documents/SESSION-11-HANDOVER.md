# SESSION 11 HANDOVER: LLM Integration Ready

**Date**: 2025-11-03
**From**: Session 11 (Local TTS Implementation)
**To**: Session 12 (LLM Integration)
**Handover Status**: ✅ Complete - Ready for LLM implementation

---

## Quick Start for Session 12

### Primary Task: LLM Integration
Implement the Language Model provider system to complete the core VCA 1.0 pipeline (STT → LLM → TTS).

### Environment Setup
```bash
cd /home/indigo/my-project3/Dappva/session_manager
source venv/bin/activate
```

### Current System Status
- ✅ STT: PyTorch Whisper GPU working (0.71s warmed, Session 10)
- ✅ TTS: Piper TTS CPU working (0.570s warmed, Session 11)
- ⏳ LLM: Not yet implemented (next task)
- ✅ Session Manager: WebSocket server operational
- ✅ VAD: Voice Activity Detection working

### Target Metrics
- **Current Pipeline**: 4.38s total (STT 0.71s + LLM 2.5s + TTS 0.57s + overhead 0.6s)
- **Goal**: Stay under 10s total latency
- **Status**: ✅ 5.62s headroom available

---

## What Session 11 Accomplished

### ✅ Implemented Local TTS (Piper TTS)
- **Result**: 81% faster than OpenAI TTS (0.570s vs 3.0s)
- **Architecture**: CPU-optimized ONNX Runtime, non-autoregressive model
- **Model**: en_US-lessac-medium.onnx (61MB)
- **Quality**: Excellent audio output

### ✅ Attempted XTTS-v2 (Failed, Too Slow)
- **Result**: 9s average latency (too slow for production)
- **Reason**: Large autoregressive model + Maxwell GPU limitations
- **Learning**: GPU not always faster than CPU for small models

### ✅ Critical Discovery: PyTorch Version Lock
- **Finding**: PyTorch 2.2.2+cu121 MUST be preserved for Maxwell GPU
- **Risk**: Newer versions may break CUDA compatibility
- **Strategy**: Use `pip install <package> --no-deps` + manual dependencies
- **Documentation**: Added to CHANGELOG.md

### ✅ Warmup Testing
- **Finding**: Warmed-up models perform 1.5x faster than cold-start
- **TTS**: 0.86s cold → 0.570s warmed
- **STT**: 3.13s cold → 0.71s warmed (from Session 10)
- **Implication**: Real-world performance much better than cold benchmarks

---

## System Architecture Overview

### Modular Provider System (Established Pattern)
```
session_manager/
├── stt/
│   ├── base.py                    # STTProvider abstract base
│   ├── factory.py                 # Factory pattern for provider creation
│   └── providers/
│       ├── pytorch_whisper.py     # ✅ Working (Session 10)
│       └── openai_whisper.py      # ✅ Working (fallback)
├── tts/
│   ├── base.py                    # TTSProvider abstract base
│   ├── factory.py                 # Factory pattern for provider creation
│   └── providers/
│       ├── piper_tts.py           # ✅ Working (Session 11, RECOMMENDED)
│       ├── coqui_tts.py           # ✅ Working but slow (not recommended)
│       ├── openai_tts.py          # ✅ Working (fallback)
│       └── mock_tts.py            # ✅ Working (testing)
└── llm/                           # ⏳ TODO: Create this structure
    ├── base.py                    # LLMProvider abstract base
    ├── factory.py                 # Factory pattern for provider creation
    └── providers/
        ├── openai_llm.py          # ⏳ TODO: GPT-5-mini integration
        └── mock_llm.py            # ⏳ TODO: Testing mock
```

### Configuration Pattern (config.yaml)
```yaml
# Existing (working):
stt_provider: "pytorch_whisper"    # or "openai_whisper"
tts_provider: "piper_tts"          # or "openai_tts", "coqui_tts", "mock_tts"

# TODO for Session 12:
llm_provider: "openai_llm"         # New config needed
```

### Factory Pattern (to follow for LLM)
```python
# session_manager/llm/factory.py (to be created)
from .base import LLMProvider
from .providers.openai_llm import OpenAILLMProvider
from .providers.mock_llm import MockLLMProvider

_providers = {
    'openai_llm': OpenAILLMProvider,
    'mock_llm': MockLLMProvider,
}

class LLMProviderFactory:
    @staticmethod
    def create(provider_name: str, config: dict) -> LLMProvider:
        if provider_name not in _providers:
            raise ValueError(f"Unknown LLM provider: {provider_name}")
        return _providers[provider_name](config)
```

---

## Implementation Guide for Session 12

### Step 1: Create LLM Base Class
**File**: `session_manager/llm/base.py`

**Pattern to follow** (based on STT/TTS):
```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, AsyncIterator

@dataclass
class LLMMessage:
    role: str  # 'system', 'user', 'assistant'
    content: str

@dataclass
class LLMResult:
    content: str
    model: str
    tokens_used: Optional[int] = None
    finish_reason: Optional[str] = None

class LLMProvider(ABC):
    """Abstract base class for LLM providers"""

    def __init__(self, config: dict):
        self.config = config
        self.model = config.get('model', 'gpt-4o-mini')
        self.temperature = config.get('temperature', 0.7)
        self.max_tokens = config.get('max_tokens', 1000)

    @abstractmethod
    async def generate(self, messages: List[LLMMessage]) -> LLMResult:
        """Generate a response from the LLM"""
        pass

    @abstractmethod
    async def generate_stream(self, messages: List[LLMMessage]) -> AsyncIterator[str]:
        """Generate a streaming response from the LLM"""
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}(model='{self.model}', temp={self.temperature})"
```

### Step 2: Create OpenAI LLM Provider
**File**: `session_manager/llm/providers/openai_llm.py`

**Key points**:
- Use `openai` package (already installed from Session 10)
- Support both regular and streaming responses
- Handle API errors gracefully
- Log token usage for cost tracking
- Use GPT-4o-mini as default (fast, cheap, good quality)

**Example structure**:
```python
import asyncio
import logging
from typing import List, AsyncIterator
from openai import AsyncOpenAI

from ..base import LLMProvider, LLMMessage, LLMResult

logger = logging.getLogger(__name__)

class OpenAILLMProvider(LLMProvider):
    """OpenAI LLM provider (GPT-4o-mini, GPT-5-mini, etc.)"""

    def __init__(self, config: dict):
        super().__init__(config)
        api_key = config.get('api_key')
        if not api_key:
            raise ValueError("OpenAI API key required")

        self.client = AsyncOpenAI(api_key=api_key)
        self.system_prompt = config.get('system_prompt',
            "You are Nabu, a helpful voice assistant.")

    async def generate(self, messages: List[LLMMessage]) -> LLMResult:
        """Generate a complete response"""
        # Convert messages to OpenAI format
        openai_messages = [{"role": msg.role, "content": msg.content}
                          for msg in messages]

        # Call OpenAI API
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=openai_messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )

        # Extract result
        content = response.choices[0].message.content
        tokens = response.usage.total_tokens if response.usage else None
        finish_reason = response.choices[0].finish_reason

        logger.info(f"LLM response: {len(content)} chars, {tokens} tokens")

        return LLMResult(
            content=content,
            model=response.model,
            tokens_used=tokens,
            finish_reason=finish_reason
        )

    async def generate_stream(self, messages: List[LLMMessage]) -> AsyncIterator[str]:
        """Generate a streaming response"""
        openai_messages = [{"role": msg.role, "content": msg.content}
                          for msg in messages]

        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=openai_messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stream=True
        )

        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
```

### Step 3: Create Mock LLM Provider (for testing)
**File**: `session_manager/llm/providers/mock_llm.py`

**Purpose**: Fast testing without API calls

```python
import asyncio
from typing import List, AsyncIterator
from ..base import LLMProvider, LLMMessage, LLMResult

class MockLLMProvider(LLMProvider):
    """Mock LLM provider for testing"""

    async def generate(self, messages: List[LLMMessage]) -> LLMResult:
        await asyncio.sleep(0.1)  # Simulate processing
        return LLMResult(
            content="This is a mock response from the LLM.",
            model="mock-model",
            tokens_used=50
        )

    async def generate_stream(self, messages: List[LLMMessage]) -> AsyncIterator[str]:
        words = "This is a mock streaming response from the LLM.".split()
        for word in words:
            await asyncio.sleep(0.05)
            yield word + " "
```

### Step 4: Create Factory
**File**: `session_manager/llm/factory.py`

Follow the pattern from `stt/factory.py` and `tts/factory.py`.

### Step 5: Add Configuration
**File**: `session_manager/config.yaml`

Add new section:
```yaml
# LLM Configuration
llm_provider: "openai_llm"  # Options: openai_llm, mock_llm

openai_llm:
  model: "gpt-4o-mini"  # or "gpt-5-mini" when available
  api_key: "${OPENAI_API_KEY}"
  temperature: 0.7
  max_tokens: 1000
  system_prompt: "You are Nabu, a helpful voice assistant for Warren. You provide concise, friendly responses."

mock_llm:
  model: "mock-model"
  response: "This is a mock response."
```

### Step 6: Update main.py
**File**: `session_manager/main.py`

Add LLM initialization (similar to STT/TTS):
```python
# Around line 150, after TTS initialization
from llm.factory import LLMProviderFactory

# Load LLM provider
llm_provider_name = settings.get('llm_provider', 'openai_llm')
logger.info(f"🤖 Initializing LLM provider: {llm_provider_name}")

if llm_provider_name == 'openai_llm':
    llm_config = {
        'model': settings.get('openai_llm.model', 'gpt-4o-mini'),
        'api_key': settings.get('openai_llm.api_key'),
        'temperature': settings.get('openai_llm.temperature', 0.7),
        'max_tokens': settings.get('openai_llm.max_tokens', 1000),
        'system_prompt': settings.get('openai_llm.system_prompt',
            'You are Nabu, a helpful voice assistant.')
    }
elif llm_provider_name == 'mock_llm':
    llm_config = {
        'model': settings.get('mock_llm.model', 'mock-model'),
        'response': settings.get('mock_llm.response', 'This is a mock response.')
    }
else:
    raise ValueError(f"Unknown LLM provider: {llm_provider_name}")

llm_provider = LLMProviderFactory.create(llm_provider_name, llm_config)
logger.info(f"✓ LLM provider initialized: {llm_provider}")
```

### Step 7: Integrate into WebSocket Handler
**File**: `session_manager/main.py` (WebSocket handler)

Add LLM call in the processing pipeline:
```python
# After STT completes (around line 250)
transcript = stt_result.text
logger.info(f"📝 Transcript: {transcript}")

# Check for stop phrase
if any(phrase in transcript.lower() for phrase in STOP_PHRASES):
    logger.info("🛑 Stop phrase detected")
    # ... existing stop logic

# Generate LLM response
logger.info("🤖 Generating LLM response...")
llm_start = time.time()

messages = [
    LLMMessage(role='system', content=llm_provider.system_prompt),
    LLMMessage(role='user', content=transcript)
]

llm_result = await llm_provider.generate(messages)
llm_latency = time.time() - llm_start

logger.info(f"✓ LLM response: {len(llm_result.content)} chars, {llm_latency:.2f}s")

# Generate TTS for LLM response
logger.info("🔊 Generating TTS for response...")
tts_result = await tts_provider.synthesize(llm_result.content)

# Send response audio back to client
await websocket.send_bytes(tts_result.audio_bytes)
```

### Step 8: Create Test Script
**File**: `session_manager/test_llm.py`

Test LLM provider in isolation (similar to `test_piper_tts.py`):
```python
import asyncio
from llm.factory import LLMProviderFactory
from llm.base import LLMMessage
from config.settings import get_settings

async def test_llm():
    settings = get_settings()

    # Test OpenAI LLM
    llm_config = {
        'model': settings.get('openai_llm.model', 'gpt-4o-mini'),
        'api_key': settings.get('openai_llm.api_key'),
        'temperature': 0.7,
        'max_tokens': 100,
    }

    llm = LLMProviderFactory.create('openai_llm', llm_config)

    messages = [
        LLMMessage(role='user', content='Hello, what is the weather like today?')
    ]

    result = await llm.generate(messages)
    print(f"Response: {result.content}")
    print(f"Tokens: {result.tokens_used}")

if __name__ == "__main__":
    asyncio.run(test_llm())
```

---

## Critical Information

### PyTorch Version Lock ⚠️
**MUST PRESERVE**: `torch==2.2.2+cu121`, `torchaudio==2.2.2+cu121`

**Why**: This version works with Maxwell GPU (GTX 970). Newer versions may break CUDA compatibility.

**How to install packages safely**:
```bash
pip install <package> --no-deps  # Prevent automatic dependency upgrades
pip install <dependency>          # Manually install each dependency
```

**Check before any pip install**:
```bash
pip show torch  # Verify version is still 2.2.2+cu121
```

### API Keys (from .env file)
```bash
OPENAI_API_KEY=<key_from_session_3>  # Used for both STT fallback and LLM
```

### Current Working Directory
```bash
/home/indigo/my-project3/Dappva/session_manager/
```

### Virtual Environment
```bash
source venv/bin/activate
```

### Git Status
- Branch: `main`
- Status: Clean (all Session 11 changes committed)
- Recent commits:
  - `2f3ee43` Phase 2: PyTorch Whisper GPU acceleration + Provider system + Latency monitoring
  - `0499815` Phase 1 completion: Session Manager + Android App + comprehensive documentation

---

## Expected LLM Performance

### GPT-4o-mini (Recommended)
- **Latency**: ~1-2s for short responses (50-100 tokens)
- **Cost**: $0.15/1M input tokens, $0.60/1M output tokens (very cheap)
- **Quality**: Excellent for voice assistant tasks
- **Context**: 128K tokens

### GPT-5-mini (Future Alternative)
- **Latency**: ~2-3s (similar to GPT-4o-mini)
- **Cost**: TBD (likely similar or cheaper)
- **Quality**: Expected to be better than GPT-4o-mini
- **Availability**: Not yet released (check OpenAI docs)

### Target
- **LLM latency target**: 2.5s (assumed in pipeline calculations)
- **Total pipeline target**: <10s (currently projecting 4.38s warmed up)

---

## Session Context Management (Future Enhancement)

For Phase 3+, consider implementing:
- **Conversation history**: Store last N messages for context
- **User preferences**: Remember user's name, location, preferences
- **RAG integration**: AnythingLLM integration for knowledge base queries
- **Memory system**: Short-term (session) and long-term (persistent) memory

For now, **start simple**: Just send single user message + system prompt.

---

## Testing Strategy

1. **Unit test**: `test_llm.py` - Test LLM provider in isolation
2. **Integration test**: Test STT → LLM → TTS pipeline end-to-end
3. **Latency benchmark**: Measure LLM response times (cold vs warmed)
4. **Quality test**: Verify response quality and relevance
5. **Error handling**: Test API failures, rate limits, timeouts

---

## Common Issues & Solutions

### Issue: OpenAI API Key Not Found
**Solution**: Check `.env` file has `OPENAI_API_KEY=<key>`

### Issue: Rate Limiting
**Solution**: Implement exponential backoff retry logic

### Issue: Response Too Long
**Solution**: Adjust `max_tokens` in config, or truncate LLM responses

### Issue: Streaming Not Working
**Solution**: Ensure WebSocket can handle incremental sends, or use non-streaming mode first

---

## Files to Reference

### Existing Patterns (for reference)
- `session_manager/stt/base.py` - Abstract base class pattern
- `session_manager/stt/factory.py` - Factory pattern
- `session_manager/stt/providers/pytorch_whisper.py` - Provider implementation example
- `session_manager/tts/providers/piper_tts.py` - Async synthesis pattern
- `session_manager/config.yaml` - Configuration structure
- `session_manager/main.py` - WebSocket handler and initialization

### Documentation
- `CHANGELOG.md` - Full project history
- `Documents/SESSION-10-SUMMARY.md` - STT implementation (PyTorch Whisper)
- `Documents/SESSION-11-SUMMARY.md` - TTS implementation (Piper TTS)
- `PROJECT_HISTORY.md` - High-level project overview

---

## Success Criteria for Session 12

✅ **Minimum**:
1. LLM provider system created (base class + factory)
2. OpenAI LLM provider implemented (GPT-4o-mini)
3. Mock LLM provider implemented (for testing)
4. Configuration added to config.yaml
5. LLM integrated into main.py WebSocket handler
6. Basic test script working (`test_llm.py`)

✅ **Stretch Goals**:
1. End-to-end pipeline test (STT → LLM → TTS)
2. Latency benchmark for LLM
3. Streaming response implementation
4. Conversation history (basic session memory)
5. Error handling and fallback logic

---

## Questions to Resolve in Session 12

1. **Streaming vs Non-Streaming**: Start with non-streaming for simplicity, add streaming later?
2. **Session Memory**: How many messages to keep in context? Start with 0 (stateless)?
3. **System Prompt**: Finalize Nabu's personality and capabilities description
4. **Response Length**: Max tokens for voice responses (shorter is better for latency)
5. **Error Handling**: How to handle LLM failures? Fallback to canned responses?

---

## Additional Notes

### Dad's Context
- **User**: Warren (Dad)
- **Speech**: Sometimes slurred (STT accuracy critical)
- **Use case**: General assistance, smart home control, information queries
- **Priority**: Usability > fancy features

### System Constraints
- **GPU**: GTX 970 (Maxwell, 4GB VRAM) - already used by STT
- **CPU**: i7-4770 (4 cores, 8 threads) - available for TTS
- **RAM**: 16GB total, 7.7GB allocated to WSL2
- **Network**: Required for LLM (OpenAI API calls)

### Performance Budget
```
Current allocation:
- STT:      0.71s (warmed)  ← Using GPU
- LLM:      2.5s (target)   ← Using network/cloud
- TTS:      0.57s (warmed)  ← Using CPU
- Overhead: 0.6s
─────────────────────────────
Total:      4.38s ✅ (5.62s headroom under 10s target)
```

---

## Final Checklist Before Starting Session 12

- [ ] Read SESSION-11-SUMMARY.md (this was just created)
- [ ] Read SESSION-11-HANDOVER.md (this file)
- [ ] Check CHANGELOG.md for Session 11 entry
- [ ] Verify Python environment: `source venv/bin/activate`
- [ ] Verify PyTorch version: `pip show torch` (should be 2.2.2+cu121)
- [ ] Check OpenAI API key: `echo $OPENAI_API_KEY` or check `.env`
- [ ] Review existing provider patterns (stt/base.py, tts/base.py)
- [ ] Start with creating `llm/base.py` and `llm/factory.py`

---

**Ready to implement LLM integration! Good luck with Session 12! 🚀**

---

**End of Session 11 Handover**
