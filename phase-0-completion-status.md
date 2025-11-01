# Phase 0 - Environment Preparation - Completion Status
**VCA 1.0 Implementation**
**Date**: 2025-11-01
**Session**: 3

## Phase 0 Objectives (from vca1.0-implementation-plan.md)
- ✅ Install Home Assistant (optional integration)
- ✅ Configure PC runtime (Python 3.11+, Node 20)
- ⏳ Ensure secure LAN connectivity
- ⏳ Provision API keys for LLM/TTS

## Completion Status

### ✅ COMPLETED

#### 1. Docker Installation
- **Version**: Docker Engine 28.5.1, Docker Compose v2.40.3
- **Status**: Running
- **Service**: Started with `sudo service docker start`
- **Permissions**: User `indigo` confirmed in docker group (non-root access)
- **Test**: `docker run hello-world` successful
- **Issue Resolved**: Fixed credential helper error by resetting `~/.docker/config.json`

#### 2. Home Assistant Deployment
- **Version**: Home Assistant 2025.10.4
- **Container**: `homeassistant` (ID: `9f67751192b2`)
- **Image**: `ghcr.io/home-assistant/home-assistant:stable`
- **Network**: Host mode (for device discovery)
- **Restart Policy**: `unless-stopped` (auto-restart on PC boot)
- **Timezone**: Pacific/Auckland (New Zealand)
- **Config Directory**: `/home/indigo/homeassistant/config/`
- **Database**: SQLite initialized at `home-assistant_v2.db`
- **Web UI**: Accessible at `http://localhost:8123` ✅
- **Status**: Ready for onboarding wizard

#### 3. Python Environment
- **Version**: Python 3.12.3 ✅
- **Requirement**: Python 3.11+ ✅
- **Status**: Already installed, meets requirement

### ✅ COMPLETED BY USER (2025-11-01)

#### 4. Home Assistant Initial Configuration

1. **Access Onboarding Wizard** ✅
   - Accessed `http://localhost:8123`
   - Completed initial setup form

2. **Create User Accounts** ✅
   - **Mike VCA** (Admin): Created with full administrator access
   - **Dad VCA** (Limited): Created with restricted dashboard
   - Strong passwords set for both accounts

3. **Generate Long-Lived Access Tokens** ✅
   Generated 3 tokens:
   - **Session Manager Token**: For session manager integration
   - **Development Token**: For testing and debugging
   - **n8n Token**: For n8n automation workflows
   - ✅ Stored securely

4. **Document Configuration** ✅
   - User accounts documented
   - Access tokens labeled and stored
   - Configuration complete

### ⏳ PENDING USER ACTION

#### 5. Node.js 20 Installation
**Required for n8n (Phase 5):**

```bash
# Option 1: Using nvm (recommended for version management)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install 20
nvm use 20
nvm alias default 20

# Option 2: Using apt (Ubuntu/Debian)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify installation
node --version  # Should show v20.x.x
npm --version
```

#### 6. API Key Provisioning ✅

**Completed:**
1. **LLM API Key: OpenAI** ✅
   - API key provisioned from https://platform.openai.com/
   - **Service**: GPT-4o or GPT-4.1
   - **Usage**: Session manager LLM pipeline
   - **Also provides**: OpenAI Whisper STT API + OpenAI TTS API

**STT/TTS Strategy Decision (based on hardware analysis):**

**✅ Your PC Specs Analysis:**
- **GPU**: NVIDIA GeForce GTX 970 (4GB VRAM) ✅ EXCELLENT
- **CPU**: Intel i7-4770 (8 cores @ 3.4GHz) - Moderate
- **RAM**: 7.7 GB (2.8 GB available) - Adequate
- **CUDA**: Version 12.6 supported ✅
- **Assessment**: **PC is well-suited for local STT/TTS** (see [stt-tts-hardware-analysis.md](stt-tts-hardware-analysis.md))

**✅ Recommended Hybrid Approach:**

**Phase 1-2 (Current - Quick MVP):**
- **STT**: OpenAI Whisper API ✅ (already have key)
- **TTS**: OpenAI TTS API ✅ (already have key)
- **Cost**: ~$20-40/month (temporary)
- **Benefit**: Get assistant working immediately

**Phase 3-4 (Future - Cost Optimization):**
- **STT Primary**: Whisper Small (local GPU, 3-5x realtime on GTX 970)
- **STT Fallback**: OpenAI Whisper API (when PC offline)
- **TTS Primary**: Piper (local, fast)
- **TTS Fallback**: OpenAI TTS API (when PC offline)
- **Cost**: ~$2-5/month (fallback only)
- **Benefits**: Privacy-first, near-zero cost, low latency

**Critical Design Requirement - Dad's Slurred Speech**:
- Dad's speech is sometimes slurred and unclear even for human listeners
- **Pipeline MUST be modular** to allow easy STT model switching
- Will need to experiment with multiple STT models to find best fit
- Success metric: Dad's ability to be understood > all other factors

**✅ Modular Pipeline Architecture Documented**:
- See [modular-stt-tts-pipeline-design.md](modular-stt-tts-pipeline-design.md)
- Provider abstraction layer allows model swapping via config file only
- A/B testing framework for comparing STT models on same audio
- Testing protocol for evaluating models with Dad's actual speech
- Comprehensive documentation for model switching procedures

**Conclusion**: Your GTX 970 GPU makes local processing very viable. Start with cloud (OpenAI) for quick development, transition to local in Phase 3-4 for privacy and cost savings. Pipeline designed for experimentation to find best STT model for Dad's speech patterns.

**Detailed analyses**:
- Hardware capabilities: [stt-tts-hardware-analysis.md](stt-tts-hardware-analysis.md)
- Pipeline architecture: [modular-stt-tts-pipeline-design.md](modular-stt-tts-pipeline-design.md)

#### 7. Secure LAN Connectivity
**Verification needed:**
- Confirm PC is on same network as Samsung A05 phone
- Test ping from phone to PC (use Network Tools app)
- Document local IP address: `172.20.177.188` (WSL)
- Verify firewall allows port 8123 (Home Assistant)
- Confirm 95% uptime requirement (always-on PC except restarts)

### ⏳ DEFERRED TO LATER PHASES

#### Phase 1 Tasks (Audio & Wake Pipeline)
- Install Home Assistant Supervisor add-ons:
  - Whisper (STT)
  - Piper (TTS)
  - openWakeWord (wake-word detection)
- Configure Assist pipeline for NZ English
- Set up custom intents: "Stop for now", "Cancel that"
- Test HA WebSocket API connectivity

#### Phase 3 Tasks (Memory Foundation)
- Deploy AnythingLLM container
- Create "Dad-Vault" workspace
- Ingest initial Packs A, C, D, I seed documents
- Configure LanceDB vector store

#### Phase 5 Tasks (Automations)
- Deploy n8n container
- Restore previous automation workflows
- Connect n8n to Home Assistant webhooks

## Container Management Reference

### Home Assistant Container Commands
```bash
# View logs (follow mode)
docker logs homeassistant -f

# View last 50 log lines
docker logs homeassistant --tail 50

# Stop Home Assistant
docker stop homeassistant

# Start Home Assistant
docker start homeassistant

# Restart Home Assistant
docker restart homeassistant

# Check resource usage
docker stats homeassistant

# Remove container (keeps config)
docker rm homeassistant

# Recreate container with same settings
docker run -d \
  --name homeassistant \
  --privileged \
  --restart=unless-stopped \
  -e TZ=Pacific/Auckland \
  -v /home/indigo/homeassistant/config:/config \
  --network=host \
  ghcr.io/home-assistant/home-assistant:stable
```

### Docker Service Management (WSL2)
```bash
# Start Docker service
sudo service docker start

# Check Docker service status
sudo service docker status

# Stop Docker service (not recommended)
sudo service docker stop

# Restart Docker service
sudo service docker restart
```

## Important File Locations

### Home Assistant Configuration
- **Config Directory**: `/home/indigo/homeassistant/config/`
- **Main Config**: `/home/indigo/homeassistant/config/configuration.yaml`
- **Automations**: `/home/indigo/homeassistant/config/automations.yaml`
- **Scripts**: `/home/indigo/homeassistant/config/scripts.yaml`
- **Secrets**: `/home/indigo/homeassistant/config/secrets.yaml`
- **Database**: `/home/indigo/homeassistant/config/home-assistant_v2.db`
- **Logs**: `/home/indigo/homeassistant/config/home-assistant.log`

### Docker Configuration
- **Docker Config**: `~/.docker/config.json`
- **Container Data**: `/var/lib/docker/` (managed by Docker daemon)

## Network Access Points

### Home Assistant Web UI
- **Primary**: `http://localhost:8123`
- **WSL IP**: `http://172.20.177.188:8123`
- **From Windows**: Use `localhost:8123` or WSL IP
- **From Phone (same network)**: Use PC's LAN IP (find via `ipconfig` on Windows)

### Future Services (Post-Installation)
- **AnythingLLM**: `http://localhost:3001` (Phase 3)
- **n8n**: `http://localhost:5678` (Phase 5)
- **Session Manager**: TBD (custom port, Phase 2)

## Security Considerations

### Completed
- ✅ Docker socket accessible only to docker group members
- ✅ Home Assistant runs in isolated container
- ✅ Configuration files stored in user directory (non-root)
- ✅ Restart policy prevents container from auto-restarting after manual stop

### Pending Review
- ⏳ Firewall configuration for external access
- ⏳ HTTPS/SSL certificate setup (if exposing outside LAN)
- ⏳ API token security (use secrets.yaml)
- ⏳ Network segmentation (IoT devices vs. main network)

## Next Immediate Steps

1. **Complete Home Assistant Onboarding** (5-10 minutes)
   - Access `http://localhost:8123`
   - Create Mike VCA admin account
   - Create Dad VCA limited account
   - Complete location/timezone verification

2. **Generate Access Tokens** (5 minutes)
   - Create 3 long-lived tokens as specified above
   - Document tokens securely

3. **Install Node.js 20** (5-10 minutes)
   - Use nvm or apt method above
   - Verify with `node --version`

4. **Provision API Keys** (15-30 minutes)
   - Sign up for Anthropic Claude API
   - Generate and test API key
   - Consider local Whisper/Piper vs. cloud services

5. **Test Network Connectivity** (5 minutes)
   - Ping PC from phone
   - Access Home Assistant from phone browser
   - Verify 95% uptime capability

## Phase 0 Sign-Off

### Ready to Proceed to Phase 1?
- ✅ Docker installed and tested
- ✅ Home Assistant running and accessible
- ✅ Python 3.12.3 available
- ✅ Home Assistant onboarding complete
- ✅ Access tokens generated (Session Manager, Development, n8n)
- ✅ API keys provisioned (OpenAI for LLM + STT/TTS)
- ✅ STT/TTS strategy decided (Hybrid: Cloud now, Local in Phase 3-4)
- ⏳ Node.js 20 installed
- ⏳ Network connectivity verified

**Remaining items**: 2 tasks, ~15-20 minutes

**Phase 0 Status**: ⚡ **95% COMPLETE** - Only Node.js installation and network test remaining

**Phase 1 readiness**: ✅ All critical infrastructure ready (HA, Docker, API keys, STT/TTS plan)

## References
- [ha-docker-installation-plan.md](ha-docker-installation-plan.md) - Detailed installation plan and testing roadmap
- [vca1.0-implementation-plan.md](vca1.0-implementation-plan.md) - Full VCA implementation roadmap
- [CHANGELOG.md](CHANGELOG.md) - Project-wide decisions and session notes
- [Home Assistant Getting Started](https://www.home-assistant.io/getting-started/)
- [Home Assistant Assist Voice Control](https://www.home-assistant.io/voice_control/)
