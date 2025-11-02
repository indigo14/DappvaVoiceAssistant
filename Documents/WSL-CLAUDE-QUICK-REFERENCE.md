# WSL + Claude Code Quick Reference

**For all Claude sessions working on this project**

> This is a concise reference for common WSL + Claude Code issues. For complete troubleshooting, see [WSL-problems with Claude.md](./WSL-problems%20with%20Claude.md)

**Documentation Standard:** All project documentation should be placed in the `Documents/` folder.

---

## Critical WSL Issues for Claude Code

### File System Performance
**Problem:** Slow or incomplete search results when working across file systems on WSL.

**Solution:** Ensure projects are located in the Linux filesystem (`/home/`) rather than Windows filesystem (`/mnt/c/`).

**Current project location:** `/home/indigo/my-project3/Dappva` ✓ (Correct location)

---

### npm/Node.js Path Conflicts
**Problem:** WSL may use Windows npm/node instead of Linux versions, causing "node not found" errors.

**Quick Check:**
```bash
which npm    # Should show /usr/... or ~/.nvm/... (NOT /mnt/c/...)
which node   # Should show /usr/... or ~/.nvm/... (NOT /mnt/c/...)
```

**Quick Fix:**
```bash
# Load nvm in current session
source ~/.nvm/nvm.sh

# Or add to ~/.bashrc permanently:
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
```

---

### Search and Discovery
**Problem:** Search tool, `@file` mentions, agents, and slash commands not working.

**Solution:** Install system ripgrep:
```bash
sudo apt install ripgrep
```

---

## JetBrains IDE Integration (IMPORTANT FOR THIS PROJECT)

### IDE Not Detected on WSL2
**Problem:** "No available IDEs detected" errors when using JetBrains IDEs (IntelliJ, PyCharm, WebStorm, etc.) with Claude Code on WSL2.

**Cause:** WSL2 networking (NAT mode) or Windows Firewall blocking connections.

**Solution Option 1: Configure Windows Firewall** (Recommended)

1. Find your WSL2 IP address:
   ```bash
   wsl hostname -I
   # Example: 172.21.123.456
   ```

2. Open PowerShell as Administrator:
   ```powershell
   New-NetFirewallRule -DisplayName "Allow WSL2 Internal Traffic" -Direction Inbound -Protocol TCP -Action Allow -RemoteAddress 172.21.0.0/16 -LocalAddress 172.21.0.0/16
   ```
   (Adjust IP range based on your WSL2 subnet)

3. Restart IDE and Claude Code

**Solution Option 2: Switch to Mirrored Networking**

Add to `.wslconfig` in Windows user directory (`C:\Users\YourName\.wslconfig`):
```ini
[wsl2]
networkingMode=mirrored
```

Then restart WSL:
```powershell
wsl --shutdown
```

### ESC Key Not Working in JetBrains Terminals
**Problem:** ESC key doesn't interrupt Claude Code in JetBrains terminal.

**Solution:**
1. Go to Settings → Tools → Terminal
2. Either:
   - Uncheck "Move focus to the editor with Escape", OR
   - Click "Configure terminal keybindings" and delete "Switch focus to Editor" shortcut
3. Apply changes

---

## Quick Command Reference

| Issue | Command |
|-------|---------|
| Check WSL status | `wsl --list --verbose` (PowerShell) |
| Shutdown WSL | `wsl --shutdown` (PowerShell) |
| Check node/npm paths | `which node && which npm` |
| Load nvm | `source ~/.nvm/nvm.sh` |
| Install ripgrep | `sudo apt install ripgrep` |
| Check WSL IP | `wsl hostname -I` |
| Check Claude health | `claude doctor` |

---

## WSL Backup Information

For complete backup and restore procedures, see:
- [WSL-BACKUP-RESTORE-REFERENCE.md](./WSL-BACKUP-RESTORE-REFERENCE.md)

**Current backups:**
- Primary: `E:\WSL-Backups\Ubuntu_backup_2025-11-02.tar`
- Secondary: `F:\Coding backup\Ubuntu_backup_2025-11-02.tar`

---

## Getting Help

1. **Full troubleshooting guide:** [WSL-problems with Claude.md](./WSL-problems%20with%20Claude.md)
2. **Run diagnostics:** `claude doctor`
3. **Report bugs:** `/bug` command or [GitHub Issues](https://github.com/anthropics/claude-code/issues)
4. **Ask Claude:** Claude has built-in access to its documentation

---

**Last Updated:** 2025-11-02
**Project:** VCA 1.0 - Voice Conversation Assistant
