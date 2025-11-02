# Home Assistant Environment Exploration

## Goals
- Enable hands-free voice assistant (VCA) and coding agents to run with minimal user intervention.
- Leverage Home Assistant for device orchestration, guardrails, and automations while maintaining privacy.
- Rebuild plug-and-play RAG and automation stacks (n8n) lost after the computer reset.

## Home Assistant Capabilities Relevant to Dad’s Setup
- Native dashboards, automation engine, energy management, and organization tooling ship with core install; all operate locally for privacy-first control.[^1]
- Built-in Assist voice stack provides configurable wake-word workflows, optional cloud LLM hooks, and companion app access—useful for routing headset/phone commands to Home Assistant scenes or scripts.[^2]
- Licensing: Home Assistant Core is released under Apache 2.0, ensuring full-source availability and permissive self-hosting.[^3]

## Environment Plan for Coding Agents
1. **Provision Home Assistant (HAOS or Container)**  
   - Install on always-on PC (except for restarts) or dedicated mini-PC; enable the Supervisor for add-ons (Whisper, ESPHome).  
   - Create dedicated “Dad VCA” user with limited dashboard scoped to assistant status + quick actions.
   - Create dedicated “Mike VCA” user with unlimited dashboard scoped to administrator  status + quick actions.
2. **Expose Automation Hooks for Agents**  
   - Define Assist intents and HA scripts for common routines (reminders, check-ins) so coding agents can call REST/webhook endpoints without broad admin credentials.  
   - Configure Long-Lived Access Tokens scoped to automations for the session manager and n8n.
3. **Agent Runtime Sandbox**  
   - Run VCA session manager + coding agents in Docker/Podman on same host.  
   - Mount shared volume for memory store (PostgreSQL/SQLite + vector DB) and expose internal network endpoints (`http://ha.local:8123`, `http://n8n:5678`).
4. **Testing & GUI Support**  
   - Keep HA dashboards plus n8n editor UI accessible so user can validate agent-triggered flows.  
   - Log every automation invocation back to memory Pack I (Safety) for audit.

## Plug-and-Play RAG Options (quick restore)
- **AnythingLLM** – “All-in-one AI app” with drag-and-drop ingestion, multi-user support, agent builder, and citations; install via Docker or desktop app for the fastest private chat-with-docs baseline.[^4]
- **Flowise** – Visual LangChain builder with global npm install (`npm install -g flowise`, `npx flowise start`) or Docker; ideal when you need custom pipelines (ASR → guardrails → retrieval → LLM) without heavy coding.[^5]
- **Open WebUI** – Self-hosted AI platform with built-in RAG pipeline, Ollama/OpenAI connectors, RBAC, voice/video chat, and document library; deploy via Docker/Kubernetes or `pip`.[^6]

### Selection Guidance
1. Start with AnythingLLM for immediate document-grounded conversations and shared workspace permissions.  
2. Layer Flowise when bespoke retrieval chains or branching logic are required.  
3. Use Open WebUI if you need an integrated chat UX with role-based access and voice features that complement the VCA prototype.

## n8n Automation Path
- n8n offers 400+ integrations, LangChain-native AI nodes, and self-hostable workflow canvas—ideal for bridging Home Assistant events with external services (SMS, WhatsApp, webhooks).[^7]
- Recreate critical flows (safety escalations, reminders) and expose them as HTTP endpoints that the session manager or Home Assistant can call.  
- Store workflow metadata (name, inputs, last run) in Pack C (Tech How-Tos) for transparency and quick retraining.

## Next Steps
1. Spin up Home Assistant (supervised install) and document network endpoints and tokens.  
2. Deploy AnythingLLM container alongside memory database; ingest existing Dad profile + Tech How-Tos.  
3. Restore n8n workflows, connect to Home Assistant and session manager, and test stop/snooze automations.

[^1]: Home Assistant “Getting started” navigation (dashboards, automations, energy): https://www.home-assistant.io/getting-started/  
[^2]: Home Assistant Assist voice control overview (local/cloud processing, companion access): https://www.home-assistant.io/voice_control/  
[^3]: Home Assistant Core license (Apache 2.0): https://raw.githubusercontent.com/home-assistant/core/master/LICENSE.md  
[^4]: AnythingLLM README (features, agent builder, multi-user): https://raw.githubusercontent.com/Mintplex-Labs/anything-llm/master/README.md  
[^5]: Flowise README (visual builder, quick start commands): https://raw.githubusercontent.com/FlowiseAI/Flowise/main/README.md  
[^6]: Open WebUI README (built-in RAG, voice/video, RBAC): https://raw.githubusercontent.com/open-webui/open-webui/main/README.md  
[^7]: n8n README (workflow automation, LangChain AI nodes, integrations): https://raw.githubusercontent.com/n8n-io/n8n/master/README.md
