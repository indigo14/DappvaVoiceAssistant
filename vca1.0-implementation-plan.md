# VCA 1.0 Implementation Plan

## 1. Objectives & Guardrails (from Dad profile & session notes)
- Deliver hands-free voice activation (no push-to-talk) with reliable pause detection and an explicit “stop” phrase.
- Keep responses brief (≤3 sentences) with numbered options when relevant; always confirm before acting on calls, messages, or data edits.
- Support 95% uptime on home network, fall back gracefully when offline, and never become obtrusive—easy suspend/resume is mandatory.
- Maintain a durable memory vault governed by save/forget phrases, daily auto-summaries, and a strict redaction policy (no secrets, no card numbers).
- Allow Michael to review/edit structures; only Dad and Michael can see stored memories.

## 2. System Architecture Overview
1. **Audio capture (phone A05)**  
   - Android foreground service listens for wake phrase (“Hey Assistant” placeholder) using on-device wake-word engine (e.g., [Picovoice Porcupine](https://picovoice.ai/porcupine/) or open-source [Vosk KW](https://github.com/alphacep/vosk-api)).  
   - On wake, stream microphone audio to PC via secure WebSocket/WebRTC; auto-stop after 2–3 s silence or “Cancel that.”
2. **Session manager (PC hub)**  
   - Receives audio, performs ASR (local Whisper medium via [faster-whisper](https://github.com/guillaumekln/faster-whisper) for privacy; optional cloud fallback).  
   - Manages conversation state, applies guardrails (sensitive topic filters, activity time-outs), routes to memory layer and LLM.
3. **Memory & RAG services**  
   - Structured store (PostgreSQL/SQLite) holds “packs” defined in Dad profile; vector store (LanceDB/Chroma) enables semantic retrieval for unstructured notes.  
   - Save/forget hooks enforce opt-in phrases; daily cron writes orientation summaries.
4. **LLM layer**  
   - Start on “frontier” hosted model (e.g., Claude 3.5 Sonnet or GPT-4.1) through existing API client; design abstractions so a local model (e.g., via Ollama) can drop in later.
5. **Response synthesis**  
   - Apply concise-response template, optional streaming TTS (ElevenLabs / OpenAI or local Piper) back to phone; support “Repeat/Slower” commands.
6. **Control & stop mechanisms**  
   - Global “Stop for now” phrase pauses session manager for configurable duration, with quick resume.  
   - Dad can mute audio capture from headset button (hardware override) or phone toggle.

## 3. Implementation Phases
- **Phase 0 – Environment prep**  
  Install Home Assistant (optional integration), configure PC runtime (Python 3.11, Node 20), ensure secure LAN connectivity, provision API keys for chosen LLM/TTS.
- **Phase 1 – Audio & wake pipeline**  
  Build Android service for wake-word + streaming, implement PC endpoint & VAD-driven auto-stop, add immediate “stop listening” guard.
- **Phase 2 – Session manager & baseline chat**  
  Implement ASR + LLM pipeline with brief-response formatter, add Dad-specific persona prompt using `dad_profile_pre_filled_voice_assistant.md`.
- **Phase 3 – Memory foundation**  
  Define schemas for Priority Packs (A: Daily orientation, C: Tech how-tos, D: Contacts, I: Safety) and implement save/forget flows with audit logging.
- **Phase 4 – Retrieval Augmentation**  
  Connect vector store, wire retrieval to conversation context, add query planners for quick facts vs. list retrieval vs. scripted help.
- **Phase 5 – Automations & integrations**  
  Connect Home Assistant and/or n8n for device control, reminders, and escalations; add notification routing (SMS/WhatsApp) per safety rules.
- **Phase 6 – Hardening & UX polish**  
  Usability testing with Dad, latency tuning, offline fallbacks (local LLM and ASR models), monitoring/alerting, documentation handoff.

## 4. Memory Strategy (aligning with Packs A–P)
- **Data model**  
  - Relational tables for key-value packs (Contacts, Safety rules, Checklists) with `edited_by`, `confidence`, `last_reviewed`.  
  - Document store or Markdown vault for narrative packs (Journal, Health visits) with versioning.  
  - Vector embeddings (MiniLM or nomic-embed) for semantic search across all text, namespaced per pack.
- **Save flows**  
  - Intent classifier detects “Save/Remember” utterances, prompts for pack + title when ambiguous, echoes back stored summary for confirmation.  
  - Daily auto-journal uses scheduler to compose 5 bullets from conversation log; user can veto.
- **Forget & privacy**  
  - Soft-delete with reversible window (e.g., 24 h) to avoid accidental loss; full purge on explicit “Forget that.”  
  - Redaction middleware strips card numbers, OTPs, passwords before storage.
- **Retrieval patterns**  
  - Use retrieval recipes per pack (e.g., direct SQL for Contacts, vector search with filter `pack='Tech How-Tos'` for step-by-step guides).  
  - Provide meta prompts like “List my saved Tech How-Tos” for transparency.

## 5. Plug-and-Play RAG Platforms (2025 review)
- **AnythingLLM (Mintplex Labs)** – Self-hostable chat + RAG suite with drag-and-drop ingestion, LanceDB default vector store, multi-LLM support, built-in agents and TTS/STT. Fastest path via Docker; suits small-team deployment with UI driven memory management.  
  _Source:_ [Mintplex Labs README (Nov 2025)](https://github.com/Mintplex-Labs/anything-llm).
- **Flowise** – Visual node-based builder for LangChain graphs; npm install (`npm install -g flowise`, `npx flowise start`) or Docker. Great for composing custom pipelines (ASR → Guardrails → RAG → LLM) without heavy coding; integrates with dozens of vector DBs.  
  _Source:_ [Flowise README (Nov 2025)](https://github.com/FlowiseAI/Flowise).
- **Onyx (fka Danswer)** – All-in-one open-source AI workspace with enterprise-grade search, connectors to 40+ data sources, hybrid search + knowledge graph, Docker installer script. Useful if you need multi-user permissions and analytics.  
  _Source:_ [Onyx README (Nov 2025)](https://github.com/danswer-ai/danswer).
- **Selection guidance:**  
  1. Start with AnythingLLM for quickest “upload docs → chat” baseline and built-in embeddings.  
  2. Add Flowise if you need bespoke routing (e.g., different prompts for Packs).  
  3. Graduate to Onyx when you need advanced permissioning or large document volumes.

## 6. Home Assistant Fit Check
- **Beyond device control:** Offers automation engine (time/location/event triggers), dashboards tailored for accessibility, voice assistants (Assist/Wake Words) with local processing, notification routing (mobile push, TTS, media players), energy monitoring, and scene scripting. Integrates with 1,000+ services and can call webhooks/n8n flows—ideal for coordinating reminders, lighting cues, or safety escalations tied to Dad’s routines.
- **Open-source status:** Core project released under Apache 2.0 license, maintained by Nabu Casa + community; 100% self-hostable with optional paid cloud relay. Active community adds integrations weekly; you retain full data ownership on local installs.

## 7. Guardrails & Safety Layers
- Implement configurable content filters (e.g., restrict medical/financial advice), sensitive-topic warnings, and “Do-not-do” list enforcement before actions execute.  
- Log all interventions with timestamps and decision rationale for later review by Michael.  
- Provide quick toggle on phone to snooze assistant or disable wake word when concentration is needed.

## 8. Immediate Next Actions
1. Choose wake-word SDK and confirm Android app constraints on the A05.  
2. Decide on initial RAG platform (AnythingLLM vs. Flowise) and provision local Docker host.  
3. Draft schema + migration files for Packs A, C, D, I to unblock Phase 3 development.  
4. Prototype “stop conversation” UX on phone (button + phrase) to ensure non-obtrusive behavior before live testing.

---

## 9. Decision Notes & Clarifications (2025-11-01)
- **Wake-word capture options for Samsung A05 / HA:**  
  - Picovoice Porcupine SDK (Android or Home Assistant Wyoming integration) – lightweight, offline, customizable keywords.  
  - Home Assistant Assist pipeline with [openWakeWord](https://www.home-assistant.io/voice_assistant/open_wake_word/) – runs on PC or HA Yellow; phone app can relay audio via Companion App.  
  - Vosk-Kaldi keyword spotting or Coqui STT on Android – open source but heavier footprint; better suited to PC-side detection if streaming raw audio.  
  - If wake-word runs on phone, ensure persistent foreground service and ability to suspend quickly (“stop listening”) to avoid distractions.
- **Packs A / C / D / I (from Dad profile vault structure):**  
  - **Pack A – Daily Orientation:** day/date, weather, top 3 plans; supports “What’s today?” queries.  
  - **Pack C – Tech How-Tos:** step-by-step guides for device tasks (answer WhatsApp, reconnect headset, Wi-Fi fix).  
  - **Pack D – Contacts & Relationships:** who’s who, phone numbers, last interactions.  
  - **Pack I – Safety & Check-ins:** trigger phrases, escalation order, check-in schedules.  
  These packs deserve first-class schemas so save/retrieve flows stay fast and auditable.
- **Home Assistant role (beyond device control):**  
  - Run Assist voice pipelines (wake word, STT, intent handling) locally; can forward intents to coding agents or AnythingLLM via webhooks.  
  - Automate reminders, safety check-ins, lighting cues, and materialized “stop assistant” scenes.  
  - Expose dashboards for Dad/Michael, log events, and trigger n8n workflows for complex automations.
- **AnythingLLM integration touchpoints:**  
  - REST & WebSocket APIs for ingesting documents, launching chats, and invoking built-in agents.  
  - Webhooks allow coding agents (LangChain, LLM runners) or n8n to push new notes into workspaces.  
  - Supports STT/TTS and can sit behind HA or n8n automations as the conversational memory hub.
- **TTS/STT pipeline choices:**  
  - PC-first approach: run Whisper (STT) + Piper or ElevenLabs (TTS) on desktop to minimize Android load; stream audio back to phone.  
  - Latency considerations: Whisper-medium on GPU ≈ 0.6–1.0× realtime; Piper TTS ~150 ms per sentence. Buffer audio responses before playback to avoid stutter.  
  - Fallback: use Android-native STT/TTS if PC unreachable; keep pipeline modular.
- **Automation split (HA vs. n8n):**  
  - Let Home Assistant handle real-time household automations, context sensing, and voice triggers.  
  - Use n8n for integrations HA lacks (e.g., complex API choreography, document processing, syncing with coding agents). Existing familiarity with n8n supports rapid iteration; HA can call n8n via REST nodes when needed.

### 9.1 Locked Decisions (2025-11-01)
- **Primary wake-word host:** Home Assistant Assist pipeline running openWakeWord on the PC hub (or HA container). Phone Companion App forwards audio on wake; headset button remains hardware override.  
  - Setup notes for future session: install HA `assist_pipeline` add-on, enable openWakeWord model tuned for NZ English, map “Stop for now” and “Cancel that” intents to pause automation.
- **Assist pipeline location:** Home Assistant is authoritative for wake → STT → intent handoff; session manager will subscribe via HA WebSocket API (`assist_pipeline/run`) to receive transcripts and state updates.  
  - Keep Android service minimal (capture + transport) to conserve battery and avoid duplicate hotword detection.
- **RAG platform:** AnythingLLM selected. Standing up is deferred, but future sessions should follow the “Docker Quickstart” below.

### 9.2 AnythingLLM Docker Quickstart (for future stand-up)
1. **Prereqs:** Docker + Docker Compose on the PC hub, `.env` with OpenAI/Anthropic keys (or local model URLs), choose storage path (e.g., `/opt/anythingllm`).  
2. **Obtain compose file:**  
   ```bash
   curl -fsSL https://raw.githubusercontent.com/Mintplex-Labs/anything-llm/master/docker-compose.yml -o docker-compose.yml
   ```  
   Verify version in repo if this link changes.
3. **Configure environment:** Duplicate accompanying `.env.example`, set `ANYTHINGLLM_SERVER_URL=http://localhost:3001`, `VECTOR_DB=lancedb` (default), and point `DATA_DIR` to mounted volume.  
4. **Launch:** `docker compose up -d` from install directory; wait for server on `http://localhost:3001`.  
5. **Post-setup tasks:**  
   - Create “Dad-Vault” workspace; upload initial Packs A/C/D/I seed docs.  
   - Generate API token (Settings → API Keys) for session manager + n8n.  
   - Enable built-in STT/TTS only if PC has headroom; otherwise integrate external Whisper/Piper services configured in Section 5.
6. **Shutdown / maintenance:** `docker compose down` for stop; schedule nightly `docker compose logs --tail 100` check for errors.

## 9. Build Plan Aligned to Dad Profile Script
| Work Item | Description | Key Requirements | Memory Touchpoints | Dependencies |
|-----------|-------------|------------------|--------------------|--------------|
| Persona grounding | Parse `voiceAssistantScripts/dad_profile_pre_filled_voice_assistant.md` into structured prompts and guardrails; expose version + checksum for auditing. | Use Dad’s preferred naming (“Dad/Warren”), enforce ≤3 sentence replies, numbered options, “Stop for now” phrase. | Load baseline Packs A (Orientation) & D (Contacts) as seed memories. | Phase 2 session manager, confirming latest profile edits. |
| Wake + listen UX | Replace push-to-talk default with wake phrase pipeline on the A05; add headset button override and quick pause. | Wake phrase tolerance for NZ accent, 2–3 s silence auto-stop, manual “Cancel” phrase. | Log each wake event with `session_id`, `timestamp`, `stop_reason`. | Phase 1 audio components, local wake-word SDK proof. |
| Memory scaffolding | Implement pack schemas (A, C, D, I, Tech How-Tos) with CRUD APIs and redaction filters described in the profile. | Enforce opt-in save (“Save that”), explicit confirm before persisting, soft-delete window. | Vector store namespace per pack; relational tables for structured data. | Phase 3 storage stack stood up. |
| Consent & guardrails | Add middleware that checks for do-not-do items before executing automations or external calls. | Block storing card numbers/OTP, require re-ask if sensitive topics flagged, provide quick snooze toggle. | Tag memories with `privacy_level` for future audits. | Session manager + Home Assistant/n8n integration. |
| Orientation loop | Daily 5-bullet summary generation + prompt Dad for confirmation, respecting quiet hours. | Trigger at 8pm if no interactions post 3pm, respect “Stop conversation” state. | Save summary to Pack A with `auto_generated=true` metadata. | Scheduler + memory scaffold. |
| Retrieval recipes | Implement per-pack retrieval handlers (SQL vs vector) and surface “What’s saved in Tech How-Tos?” responses. | Always state data freshness and offer “Need to edit?” option. | Use RAG chain with pack filter + recency weighting. | Phase 4 RAG infra. |
| Home Assistant bridge | Connect session manager to Home Assistant Assist + webhook API for automations and notifications. | Support quick actions (lights, reminders), escalate via preferred contact order. | Store automation results as Pack I safety logs when relevant. | Home Assistant environment ready, API tokens stored securely. |
| Automation workflows | Restore n8n flows (or recreate) for multi-step automations, triggered via session manager or Home Assistant events. | Provide confirmation dialogue before executing each automation, log completions. | Write workflow metadata (name, inputs, status) to Pack C Tech How-Tos for future reuse. | n8n deployment reachable, API creds configured. |
| Testing & pause UX | Conduct usability sessions with Dad; verify “Stop conversation” works instantly and assistant resumes gracefully. | Document fallback instructions if home network down; ensure push notification to Michael on failures. | Record test notes in Pack A orientation journal for traceability. | All primary pipelines implemented. |

### Milestone sequencing
1. Lock persona + guardrails base prompt (Persona grounding).  
2. Ship MVP voice wake path with immediate stop controls (Wake + listen UX).  
3. Stand up memory scaffolding + consent layer before launching external automations.  
4. Integrate RAG retrieval + orientation loop once baseline chat is stable.  
5. Layer on Home Assistant and n8n automations after safety reviews.  
6. Run end-to-end tests with Dad and document operational runbooks.
