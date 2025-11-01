# Home Assistant & Docker Installation Plan
**VCA 1.0 - Session 3**
**Date:** 2025-11-01
**Status:** In Progress

## Overview
Install Docker and Home Assistant Container on WSL2 (Ubuntu on Windows) to support the VCA 1.0 implementation roadmap. This installation completes Phase 0 (Environment Preparation) requirements for the voice assistant infrastructure.

## VCA Implementation Milestones

Based on analysis of [vca1.0-implementation-plan.md](vca1.0-implementation-plan.md), the complete project follows this milestone sequence:

### 6-Step Milestone Sequence
1. **Lock persona + guardrails base prompt** (Persona grounding)
2. **Ship MVP voice wake path with immediate stop controls** (Wake + listen UX)
3. **Stand up memory scaffolding + consent layer** before launching external automations
4. **Integrate RAG retrieval + orientation loop** once baseline chat is stable
5. **Layer on Home Assistant and n8n automations** after safety reviews
6. **Run end-to-end tests with Dad** and document operational runbooks

### Implementation Phases (0-6)

**Phase 0 – Environment Preparation** ← *Current installation completes this*
- Install Home Assistant (optional integration)
- Configure PC runtime (Python 3.11+, Node 20)
- Ensure secure LAN connectivity
- Provision API keys for LLM/TTS

**Phase 1 – Audio & Wake Pipeline**
- Build Android service for wake-word + streaming
- Implement PC endpoint & VAD-driven auto-stop
- Add immediate "stop listening" guard

**Phase 2 – Session Manager & Baseline Chat**
- Implement ASR + LLM pipeline with brief-response formatter
- Add Dad-specific persona prompt using dad_profile_pre_filled_voice_assistant.md

**Phase 3 – Memory Foundation**
- Define schemas for Priority Packs (A: Daily orientation, C: Tech how-tos, D: Contacts, I: Safety)
- Implement save/forget flows with audit logging

**Phase 4 – Retrieval Augmentation**
- Connect vector store
- Wire retrieval to conversation context
- Add query planners for quick facts vs. list retrieval vs. scripted help

**Phase 5 – Automations & Integrations**
- Connect Home Assistant and/or n8n for device control, reminders, and escalations
- Add notification routing (SMS/WhatsApp) per safety rules

**Phase 6 – Hardening & UX Polish**
- Usability testing with Dad
- Latency tuning
- Offline fallbacks (local LLM and ASR models)
- Monitoring/alerting
- Documentation handoff

## Testing Checkpoints by Phase

### Phase 0 Testing (This Installation)
- ✅ Docker installed and running
- ✅ Home Assistant accessible at http://localhost:8123
- ✅ Container auto-restart configured
- ✅ Permissions configured (developer root access, Dad docker group access)

### Phase 1 Testing
- Wake-word accuracy
- Latency measurement
- 2-3 second silence detection
- "Cancel that" phrase response time

### Phase 2 Testing
- ASR accuracy with NZ accent
- Brief-response formatting (≤3 sentences)
- Persona consistency

### Phase 3 Testing
- Save/forget flows
- Redaction middleware (strips card numbers, OTPs, passwords)
- Soft-delete recovery (24-hour window)
- Pack schema integrity

### Phase 4 Testing
- Vector store retrieval accuracy
- Pack filtering functionality
- Data freshness indicators

### Phase 5 Testing
- Home Assistant webhook integration
- n8n automation execution
- Notification routing (SMS/WhatsApp)

### Phase 6 Testing (End-to-End)
- Usability testing with Dad
- Offline fallback behavior
- Latency under load
- Monitoring accuracy
- "Stop conversation" instant response + graceful resume

## Priority Packs Structure

**Pack A – Daily Orientation**
- Day/date, weather, top 3 plans
- Supports "What's today?" queries
- Auto-generated daily summary (5 bullets at 8pm)

**Pack C – Tech How-Tos**
- Step-by-step guides for device tasks
- Examples: answer WhatsApp, reconnect headset, Wi-Fi fix
- Stores workflow metadata for reuse

**Pack D – Contacts & Relationships**
- Who's who, phone numbers, last interactions
- Fast relational SQL queries

**Pack I – Safety & Check-ins**
- Trigger phrases, escalation order, check-in schedules
- Safety logs and automation results

## Permission Strategy

**Developer (Mike/current user)**: Root access via sudo for full control during development

**Dad user**: Added to docker group for non-root container access
- Avoids permission issues during testing
- Can interact with containers without sudo
- Safe for end-user testing scenarios

**Docker socket**: Accessible to docker group members

## Installation Steps

### 1. Install Docker Engine on WSL2
```bash
# Update package index
sudo apt-get update

# Install prerequisites
sudo apt-get install -y ca-certificates curl gnupg

# Add Docker's official GPG key
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Update apt again
sudo apt-get update

# Install Docker packages
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Start Docker service
sudo service docker start

# Verify installation
docker --version
docker compose version
```

### 2. Configure Docker Permissions
```bash
# Add current user (indigo) to docker group
sudo usermod -aG docker indigo

# If Dad's user account exists, add it too
# sudo usermod -aG docker dad

# Apply group changes (may need to log out/in or restart shell)
newgrp docker

# Test docker access without sudo
docker run hello-world
```

### 3. Deploy Home Assistant Container
```bash
# Create configuration directory
sudo mkdir -p /opt/homeassistant/config
sudo chown -R indigo:indigo /opt/homeassistant

# Pull Home Assistant image
docker pull ghcr.io/home-assistant/home-assistant:stable

# Run Home Assistant container
docker run -d \
  --name homeassistant \
  --privileged \
  --restart=unless-stopped \
  -e TZ=Pacific/Auckland \
  -v /opt/homeassistant/config:/config \
  --network=host \
  ghcr.io/home-assistant/home-assistant:stable
```

**Container Configuration:**
- `--name homeassistant`: Easy container reference
- `--privileged`: Access to USB devices (for future Zigbee/Z-Wave integration)
- `--restart=unless-stopped`: Auto-restart on PC boot (except manual stops)
- `-e TZ=Pacific/Auckland`: New Zealand timezone
- `-v /opt/homeassistant/config:/config`: Persistent configuration
- `--network=host`: Host network mode for device discovery

### 4. Verify Home Assistant Access
```bash
# Wait for startup (usually 60-90 seconds)
sleep 90

# Check container logs
docker logs homeassistant --tail 50

# Verify container is running
docker ps | grep homeassistant

# Test web UI access
curl -I http://localhost:8123
```

**Expected Result:**
- Web UI accessible at `http://localhost:8123`
- Onboarding wizard appears on first access

## Home Assistant Container Management

### Common Commands
```bash
# View logs
docker logs homeassistant -f

# Stop Home Assistant
docker stop homeassistant

# Start Home Assistant
docker start homeassistant

# Restart Home Assistant
docker restart homeassistant

# Remove container (keeps config)
docker rm homeassistant

# Check resource usage
docker stats homeassistant
```

### Configuration Files
- **Location**: `/opt/homeassistant/config/`
- **Main config**: `/opt/homeassistant/config/configuration.yaml`
- **Logs**: `/opt/homeassistant/config/home-assistant.log`
- **Database**: `/opt/homeassistant/config/home-assistant_v2.db`

## Phase 0 Completion Checklist

### Environment Setup Status
- ✅ **Platform**: WSL2 (Linux 6.6.87.2-microsoft-standard-WSL2)
- ✅ **Python**: 3.12.3 (meets 3.11+ requirement)
- ⏳ **Docker**: Installing...
- ⏳ **Home Assistant**: Pending Docker installation
- ⏳ **Node 20**: Not yet installed (needed for n8n)
- ⏳ **API Keys**: Not yet provisioned (Claude/OpenAI for LLM, ElevenLabs/OpenAI for TTS)

### Home Assistant Initial Configuration (Post-Installation)
1. Complete onboarding wizard
   - Create "Mike VCA" admin user (developer/Michael)
   - Create "Dad VCA" limited user (for Dad)
2. Generate Long-Lived Access Tokens
   - Session manager token
   - n8n automation token
   - Development/testing token
3. Document endpoints and credentials
4. Prepare for Supervisor add-on installation (Phase 1 prep):
   - Whisper (STT)
   - Piper (TTS)
   - openWakeWord (wake-word detection)

## Next Steps After Installation

### Immediate (Complete Phase 0)
1. Access Home Assistant web UI at `http://localhost:8123`
2. Complete onboarding wizard
3. Create user accounts (Mike admin + Dad limited)
4. Generate API tokens
5. Install Node 20 via nvm or apt
6. Provision LLM/TTS API keys

### Phase 1 Preparation (Audio & Wake Pipeline)
1. Install Home Assistant Supervisor add-ons:
   - Whisper for local STT
   - Piper for local TTS
   - openWakeWord for wake-word detection
2. Configure Assist pipeline for NZ English
3. Set up custom intents: "Stop for now", "Cancel that"
4. Test HA WebSocket API (`assist_pipeline/run`) connectivity

### Phase 3 Preparation (Memory Foundation)
1. Deploy AnythingLLM container (deferred from earlier sessions)
2. Create Docker network bridge for container communication
3. Configure shared volumes for memory store

### Phase 5 Preparation (Automations)
1. Deploy n8n container
2. Connect n8n to Home Assistant webhooks
3. Restore previous automation workflows

## Architecture Integration Points

### Home Assistant Role
- **Wake-word processing**: Primary host for openWakeWord detection
- **STT/TTS pipeline**: Assist pipeline manages Whisper + Piper
- **Intent handling**: Routes "Stop for now" and "Cancel that" to automation scenes
- **Automation engine**: Triggers reminders, safety check-ins, lighting cues
- **Webhook endpoints**: Exposes REST API for session manager and n8n

### Session Manager Integration
- Subscribes to HA WebSocket API for Assist pipeline events
- Receives transcripts from Whisper STT
- Sends responses to Piper TTS
- Triggers automations via HA REST API
- Logs all interactions to memory packs

### AnythingLLM Integration (Phase 3/4)
- REST & WebSocket APIs for document ingestion
- Workspace: "Dad-Vault" containing Packs A, C, D, I
- Vector store: LanceDB (default)
- API token shared with session manager and n8n

### n8n Integration (Phase 5)
- Workflow automation for complex multi-step processes
- Triggers: Home Assistant events, session manager webhooks
- Actions: SMS/WhatsApp notifications, external API calls
- Stores workflow metadata in Pack C (Tech How-Tos)

## Network Topology

```
┌─────────────────────────────────────────────────────┐
│                  WSL2 Host Network                  │
│                                                     │
│  ┌──────────────┐    ┌─────────────┐              │
│  │ Home Assist  │◄───┤  Session    │              │
│  │  :8123       │    │  Manager    │              │
│  └──────┬───────┘    └──────┬──────┘              │
│         │                   │                      │
│         │   ┌───────────────▼─────┐                │
│         └──►│  AnythingLLM        │                │
│             │  :3001              │                │
│             └───────────┬─────────┘                │
│                         │                          │
│                  ┌──────▼─────┐                    │
│                  │    n8n     │                    │
│                  │   :5678    │                    │
│                  └────────────┘                    │
│                                                     │
│  Home Network: 95% uptime, PC always-on           │
└─────────────────────────────────────────────────────┘
                           │
                           ▼
                   ┌───────────────┐
                   │  Samsung A05  │
                   │  (Phone App)  │
                   │  Audio I/O    │
                   └───────────────┘
```

## References
- [vca1.0-implementation-plan.md](vca1.0-implementation-plan.md) - Full implementation roadmap
- [home-assistant-environment-exploration.md](home-assistant-environment-exploration.md) - HA capabilities research
- [CHANGELOG.md](CHANGELOG.md) - Project-wide decisions log
- [Home Assistant Installation Docs](https://www.home-assistant.io/installation/)
- [Docker Documentation](https://docs.docker.com/)

## Installation Log

### Docker Installation
- **Date**: 2025-11-01
- **Status**: ✅ Successfully installed and configured
- **Version**: Docker 28.5.1, Compose v2.40.3
- **Service Status**: Running
- **Issue Fixed**: Removed docker-credential-desktop.exe reference from `~/.docker/config.json` (leftover from Docker Desktop)
- **User Groups**: indigo added to docker group (non-root access confirmed)
- **Test Result**: `docker run hello-world` successful

### Home Assistant Deployment
- **Date**: 2025-11-01
- **Status**: ✅ Running and accessible
- **Home Assistant Version**: 2025.10.4
- **Container ID**: `9f67751192b21a09e9d6c66bf2981743b0b1b36a002e002f7147e47c04ff03bc`
- **Container Name**: `homeassistant`
- **Network Mode**: Host
- **Restart Policy**: `unless-stopped` (survives PC reboots)
- **Timezone**: Pacific/Auckland (NZ)
- **Config Location**: `/home/indigo/homeassistant/config/`
- **Database**: SQLite `home-assistant_v2.db` (initialized)
- **Web UI Access**:
  - Local: `http://localhost:8123` ✅
  - WSL IP: `http://172.20.177.188:8123`
  - HTTP Status: 302 (redirect to onboarding)
- **First Access**: Ready for onboarding wizard

### Installation Notes
- Docker was already installed on system (version 28.5.1)
- Only needed to fix credential helper configuration
- Used `/home/indigo/homeassistant/config` instead of `/opt/homeassistant` (user has full access without sudo)
- Container started successfully on first attempt
- All configuration files generated automatically
- Home Assistant initialized in ~30 seconds
