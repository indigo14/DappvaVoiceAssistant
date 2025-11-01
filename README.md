# Dappva Voice Assistant (VCA 1.0)

A hands-free, privacy-focused voice chat assistant designed for Dad, featuring modular STT/TTS architecture optimized for slurred speech recognition.

## Overview

VCA 1.0 is a hybrid voice assistant that combines the convenience of mobile voice I/O with the power of local PC processing. The system is specifically designed to handle Dad's speech patterns through an adaptable, model-agnostic STT pipeline that allows easy experimentation and optimization.

### Architecture

**Hybrid Design**: Phone for Voice I/O + PC for Brain & Memory

```
Headset ↔ A05 (Bluetooth) → Phone App (Voice Activation)
    ↓
Home Wi-Fi
    ↓
PC (Session Manager + RAG + LLM Processing)
    ↓
Home Assistant → AnythingLLM → n8n Automation
```

### Key Features

- **Voice-Activated**: Hands-free operation (no push-to-talk)
- **Privacy-First**: Local processing where possible, cloud when needed
- **Modular STT/TTS**: Easy model swapping via configuration (no code changes)
- **Optimized for Slurred Speech**: Built for experimentation to find best STT model
- **Home Automation Ready**: Integrates with Home Assistant for device control
- **RAG-Enabled**: Uses AnythingLLM for memory and context retrieval
- **Flexible Automation**: n8n integration for workflow automation

## Current Status

**Phase 0: Environment Preparation - 95% Complete**

- ✅ Docker Engine installed and verified
- ✅ Home Assistant 2025.10.4 deployed in container
- ✅ User accounts created (Mike VCA admin + Dad VCA user)
- ✅ Long-Lived Access Tokens generated
- ✅ OpenAI API key provisioned
- ✅ Hardware analysis completed (GTX 970 GPU suitable for local Whisper)
- ✅ STT/TTS strategy decided (start cloud, migrate to local)
- ✅ Modular pipeline architecture designed
- ⏳ Pending: Node.js 20 installation (~15 min)

**Ready to begin Phase 1: Audio & Wake Pipeline Development**

## Tech Stack

### Infrastructure
- **OS**: WSL2 Ubuntu (Linux 6.6.87.2-microsoft-standard-WSL2)
- **Container Platform**: Docker Engine 28.5.1 + Compose v2.40.3
- **Automation Hub**: Home Assistant 2025.10.4 (Container)

### STT/TTS (Modular)
- **Phase 1-2**: OpenAI Whisper API + TTS (cloud, quick MVP)
- **Phase 3-4**: Local Whisper Small (GPU) + Piper TTS + cloud fallback
- **Alternative Testing**: Deepgram, Google Cloud Speech, Azure Speech

### LLM & Memory
- **LLM**: OpenAI GPT-4 (frontier model, start)
- **RAG Platform**: AnythingLLM (Docker deployment planned)
- **Workflow Automation**: n8n (previously configured, to be restored)

### Hardware
- **GPU**: NVIDIA GTX 970 (4GB VRAM, CUDA 12.6)
- **CPU**: Intel i7-4770
- **RAM**: 16GB total (7.7GB allocated to WSL2, expandable)
- **Performance**: Suitable for Whisper Small (3-5x realtime inference)

## Project Structure

```
Dappva/
├── README.md                                    # This file
├── CHANGELOG.md                                 # Detailed session logs
├── AGENTS.md                                    # Agent coordination notes
├── requirements.txt                             # Python dependencies
├── .env.example                                 # Environment variables template
├── .gitignore                                   # Excluded files/directories
├── credentials/                                 # API keys & secrets (git-ignored)
│   └── README.md                               # Credential management guide
├── voiceAssistantScripts/
│   └── dad_profile_pre_filled_voice_assistant.md
├── vca1.0-implementation-plan.md               # Original implementation plan
├── modular-stt-tts-pipeline-design.md          # Modular STT/TTS architecture
├── stt-tts-hardware-analysis.md                # Hardware capabilities analysis
├── ha-docker-installation-plan.md              # Docker + HA setup guide
├── home-assistant-environment-exploration.md   # HA exploration notes
├── phase-0-completion-status.md                # Phase 0 status tracker
└── promptlibrary.txt                           # Prompt templates
```

## Installation & Setup

### Prerequisites
- WSL2 with Ubuntu (or native Linux)
- Docker Engine 28+ with Compose v2+
- OpenAI API key
- Home network connectivity

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/DappvaVoiceAssistant.git
   cd DappvaVoiceAssistant
   ```

2. **Set up credentials**
   ```bash
   # Copy environment template to credentials directory
   cp .env.example credentials/.env

   # Edit and fill in your API keys
   nano credentials/.env
   ```

3. **Install dependencies**
   ```bash
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or: venv\Scripts\activate  # Windows

   # Install Python packages
   pip install -r requirements.txt
   ```

4. **Start Home Assistant** (if not already running)
   ```bash
   docker run -d \
     --name homeassistant \
     --restart=unless-stopped \
     --network=host \
     -v /home/indigo/homeassistant/config:/config \
     -e TZ=Pacific/Auckland \
     ghcr.io/home-assistant/home-assistant:stable
   ```

5. **Access Home Assistant**
   - Open `http://localhost:8123`
   - Complete onboarding wizard
   - Generate Long-Lived Access Token (Profile → Security)
   - Add token to `credentials/.env`

### Detailed Setup Guides
- [Docker + Home Assistant Installation](ha-docker-installation-plan.md)
- [Modular STT/TTS Pipeline Design](modular-stt-tts-pipeline-design.md)
- [Hardware Analysis & Recommendations](stt-tts-hardware-analysis.md)

## Development Phases

### Phase 0: Environment Preparation (95% Complete)
- ✅ Infrastructure setup (Docker, Home Assistant)
- ✅ API key provisioning
- ✅ Hardware analysis
- ⏳ Node.js 20 installation

### Phase 1: Audio & Wake Pipeline (Next)
- Home Assistant Assist pipeline configuration
- openWakeWord integration
- Whisper STT + OpenAI TTS setup
- Basic voice loop testing

### Phase 2: Session Manager (PC-Side)
- WebSocket audio handling
- STT/TTS provider abstraction
- Basic conversation flow
- Testing with Dad

### Phase 3: AnythingLLM RAG Deployment
- Docker deployment
- Memory store setup
- Context retrieval integration
- Local Whisper Small transition

### Phase 4: Conversation Logic & Guardrails
- Intent recognition
- Context management
- Privacy controls
- "Stop listening" command

### Phase 5: n8n Automation Restoration
- Workflow automation
- Home Assistant integrations
- Scheduled tasks

### Phase 6: Priority Packs
- **Pack 1**: Dad's room environment control
- **Pack 2**: Kitchen helpers & timers
- **Pack 3**: Music & entertainment
- **Pack 4**: Health & medication reminders

## Design Philosophy

### Modular STT/TTS Architecture
**"Build for experimentation, not commitment"**

The pipeline is designed to:
1. **Swap models** with config changes only (no code edits)
2. **A/B test** multiple STT providers on same audio samples
3. **Gracefully degrade** from local to cloud when needed
4. **Prioritize accuracy** for Dad's slurred speech over cost/latency
5. **Document results** to inform model selection

See [modular-stt-tts-pipeline-design.md](modular-stt-tts-pipeline-design.md) for full architecture.

### Privacy & Guardrails
- Non-obtrusive: Can stop conversation anytime for concentration
- Local-first: Use local models when possible, cloud when needed
- Secure: API keys stored in `credentials/`, never committed to git
- Transparent: Always know what's being sent to cloud vs processed locally

## Configuration

### STT/TTS Model Selection

Edit `config.yaml` (to be created in Phase 2):

```yaml
stt:
  primary: "openai_whisper"           # Start with cloud
  fallback: "local_whisper_small"     # Future: local fallback
  confidence_threshold: 0.6           # Trigger fallback if below

tts:
  primary: "openai_tts"
  voice: "nova"                       # Dad's preferred voice
```

**No code changes needed** to switch models - just edit config and restart.

## Testing Strategy

### STT Model Evaluation for Dad's Speech

1. **Phase 1 (Weeks 1-2)**: Baseline with OpenAI Whisper API
   - Collect 30 test samples (10 clear, 10 moderate, 10 slurred)
   - Measure Word Error Rate (WER) and intelligibility

2. **Phase 3 (Weeks 3-4)**: Local Whisper Small testing
   - Re-run samples through local model
   - Compare accuracy, latency, cost

3. **Phase 5 (Weeks 5-6)**: Alternative providers (Deepgram, etc.)
   - Test if needed based on Phase 1-3 results
   - Implement confidence-based hybrid routing

**Success Criteria**:
- WER: <15% on clear speech, <30% on slurred
- Dad's "feeling understood" score: ≥7/10
- Conversation success rate: ≥85%

## Contributing

This is a personal project for Dad's use, but design patterns and architecture may be useful for others building voice assistants for users with speech difficulties.

## Documentation

### Key Reference Documents
- [CHANGELOG.md](CHANGELOG.md) - Detailed session logs and decisions
- [vca1.0-implementation-plan.md](vca1.0-implementation-plan.md) - Original implementation plan
- [modular-stt-tts-pipeline-design.md](modular-stt-tts-pipeline-design.md) - STT/TTS architecture
- [stt-tts-hardware-analysis.md](stt-tts-hardware-analysis.md) - Hardware capabilities
- [ha-docker-installation-plan.md](ha-docker-installation-plan.md) - Infrastructure setup
- [phase-0-completion-status.md](phase-0-completion-status.md) - Current status

## License

Private project. All rights reserved.

## Contact

**Developer**: Michael Yardley (michaelyardley7@gmail.com)
**Purpose**: Voice assistant for Dad with slurred speech recognition

---

**Next Steps**: Complete Phase 0 (Node.js 20 install) → Begin Phase 1 (Audio & Wake Pipeline)

Last Updated: 2025-11-01
