# Credentials Storage

This directory is for storing sensitive information like API keys, tokens, and credentials.

## Security Notice

**IMPORTANT**: This entire directory is excluded from git via `.gitignore`. Never commit actual credentials to version control.

## Setup Instructions

1. Copy the `.env.example` file from the project root to this directory:
   ```bash
   cp ../.env.example .env
   ```

2. Edit `.env` and fill in your actual credentials:
   ```bash
   nano .env
   # or
   code .env
   ```

3. Verify the file is not tracked by git:
   ```bash
   git status
   # credentials/ should NOT appear in the output
   ```

## What to Store Here

- `.env` - Environment variables with API keys and secrets
- `*.key` - Private keys
- `*.pem` - SSL certificates
- `tokens.json` - OAuth tokens or session tokens
- Any other sensitive configuration files

## Current Required Credentials

### Phase 0-1 (Minimum Viable Product)
- **OpenAI API Key** - For Whisper STT, TTS, and LLM
- **Home Assistant Token** - Long-Lived Access Token from HA

### Phase 3+ (Optional/Future)
- **Deepgram API Key** - Alternative STT provider
- **ElevenLabs API Key** - High-quality TTS
- **AnythingLLM API Key** - RAG platform authentication
- **n8n Credentials** - Automation webhooks

## Generating Home Assistant Token

1. Open Home Assistant at `http://localhost:8123`
2. Click on your profile (bottom left)
3. Scroll to "Long-Lived Access Tokens"
4. Click "Create Token"
5. Name it (e.g., "VCA Session Manager", "Development", "n8n")
6. Copy the token immediately (it won't be shown again)
7. Paste into `credentials/.env` as `HA_TOKEN=your_token_here`

## Best Practices

- **Never share** the contents of this directory
- **Never commit** files from this directory to git
- **Keep backups** in a secure location (password manager, encrypted storage)
- **Rotate keys** regularly for security
- **Use different keys** for development vs production environments

## Troubleshooting

If credentials are accidentally committed to git:
1. Remove from git history: `git filter-branch` or BFG Repo-Cleaner
2. Rotate all exposed credentials immediately
3. Review `.gitignore` to prevent future accidents

## File Structure Example

```
credentials/
├── README.md          # This file (safe to commit)
├── .env              # Your actual credentials (NEVER commit)
├── .gitkeep          # Keep directory in git (optional)
└── backup/           # Local backups (also excluded from git)
```
