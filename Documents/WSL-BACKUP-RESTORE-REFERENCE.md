# WSL Backup and Restore Reference Guide

> **Note for all Claude sessions:** Project documentation should be stored in the `Documents/` folder.

**Created:** 2025-11-02
**System:** Ubuntu on WSL2
**Project:** VCA 1.0 - Voice Conversation Assistant

---

## Current Backup Locations

### Active Backups (Created 2025-11-02)
- **Primary:** `E:\WSL-Backups\Ubuntu_backup_2025-11-02.tar`
- **Secondary:** `F:\Coding backup\Ubuntu_backup_2025-11-02.tar`
- **Expected Size:** ~35-45 GB (compressed)

### System State at Backup Time
- **Git Commit:** `2c15a955b03376da6a2ce17edb7fe84c7ff0e3a6`
- **Commit Message:** "Initial commit: Phase 0 completion - VCA 1.0 foundation"
- **Project Status:** VCA 1.0 Phase 1 Complete, Session Manager operational
- **Docker Images:**
  - `ghcr.io/home-assistant/home-assistant:stable` (2.07GB)
  - `rhasspy/wyoming-whisper:latest` (1.55GB)
  - `rhasspy/wyoming-openwakeword:latest` (256MB)

---

## Complete Backup Procedure

### Prerequisites
- Open **Windows PowerShell** (Run as Administrator recommended)
- Ensure sufficient disk space on target drive(s)
- Close all work in WSL and save changes
- Commit any uncommitted git changes

### Step-by-Step Backup Commands

```powershell
# 1. Check current WSL status
wsl --list --verbose

# 2. Shutdown WSL completely (CRITICAL for backup integrity)
wsl --shutdown

# 3. Wait for complete shutdown
Start-Sleep -Seconds 10

# 4. Verify WSL is stopped
wsl --list --verbose
# Should show "Stopped" for all distributions

# 5. Create backup directory (if needed)
New-Item -ItemType Directory -Path "E:\WSL-Backups" -Force

# 6. Export WSL to backup file
# Replace date in filename with current date (YYYY-MM-DD format)
wsl --export Ubuntu "E:\WSL-Backups\Ubuntu_backup_2025-11-02.tar"

# Expected duration: 15-25 minutes
# Expected file size: 35-45 GB

# 7. (Optional) Create second backup to different location
wsl --export Ubuntu "F:\Coding backup\Ubuntu_backup_2025-11-02.tar"

# 8. Verify backup file was created and check size
Get-ChildItem "E:\WSL-Backups\Ubuntu_backup_2025-11-02.tar" | Format-Table Name, Length, LastWriteTime

# 9. Restart WSL
wsl
```

### Quick Backup Command (Single Location)

```powershell
wsl --shutdown; Start-Sleep -Seconds 10; wsl --export Ubuntu "E:\WSL-Backups\Ubuntu_backup_$(Get-Date -Format 'yyyy-MM-dd').tar"; wsl
```

---

## Complete Restore Procedure

### When to Use Restore
- WSL corruption or failure to start
- System rollback needed to previous state
- Migration to new computer
- Recovery after Windows reinstall

### Full System Restore (Replaces Current WSL)

⚠️ **WARNING:** This will DELETE your current WSL Ubuntu installation!

```powershell
# 1. Backup current WSL first (if possible)
wsl --export Ubuntu "E:\WSL-Backups\Ubuntu_current_before_restore.tar"

# 2. Unregister (delete) current Ubuntu distribution
# THIS DELETES ALL CURRENT DATA
wsl --unregister Ubuntu

# 3. Import backup to restore
# This recreates Ubuntu from the backup
wsl --import Ubuntu "C:\WSL\Ubuntu" "E:\WSL-Backups\Ubuntu_backup_2025-11-02.tar"

# 4. Set Ubuntu as default distribution
wsl --set-default Ubuntu

# 5. Start WSL and verify
wsl

# 6. Inside WSL, verify restoration
cd /home/indigo/my-project3/Dappva
ls -la
git status
docker ps -a
```

### Test Restore (Non-Destructive)

**Use this to verify backup integrity WITHOUT affecting your current system:**

```powershell
# 1. Import backup to TEMPORARY test location
wsl --import Ubuntu_Test "E:\WSL-Test" "E:\WSL-Backups\Ubuntu_backup_2025-11-02.tar"

# 2. Start the test instance and verify files
wsl -d Ubuntu_Test bash -c "cd /home/indigo/my-project3/Dappva && ls -la"

# 3. Check project structure
wsl -d Ubuntu_Test bash -c "cd /home/indigo/my-project3/Dappva && git log -1"

# 4. Verify Docker images exist
wsl -d Ubuntu_Test bash -c "docker images"

# 5. Check session manager files
wsl -d Ubuntu_Test bash -c "ls -la /home/indigo/my-project3/Dappva/session_manager"

# 6. When satisfied, DELETE the test instance
wsl --unregister Ubuntu_Test

# 7. Clean up test directory
Remove-Item -Recurse -Force "E:\WSL-Test"
```

### Quick Test Restore Command

```powershell
# Single command to test and cleanup
wsl --import Ubuntu_Test "E:\WSL-Test" "E:\WSL-Backups\Ubuntu_backup_2025-11-02.tar"; wsl -d Ubuntu_Test bash -c "cd /home/indigo/my-project3/Dappva && ls -la && git log -1"; wsl --unregister Ubuntu_Test; Remove-Item -Recurse -Force "E:\WSL-Test"
```

---

## Backup Verification Checklist

After creating a backup, verify:

- [ ] Backup file exists at expected location
- [ ] File size is reasonable (35-45 GB for this system)
- [ ] File creation timestamp is recent
- [ ] Test restore completes without errors
- [ ] Test restore contains expected project files
- [ ] Test restore shows correct git commit
- [ ] Docker images are present in test restore

### Verification Commands

```powershell
# Check backup file details
Get-ChildItem "E:\WSL-Backups\*.tar" | Format-Table Name, @{Label="Size (GB)"; Expression={[math]::Round($_.Length/1GB, 2)}}, LastWriteTime

# Compare sizes of multiple backups (should be similar)
Get-ChildItem "E:\WSL-Backups\Ubuntu_backup_2025-11-02.tar", "F:\Coding backup\Ubuntu_backup_2025-11-02.tar" | Format-Table Name, @{Label="Size (GB)"; Expression={[math]::Round($_.Length/1GB, 2)}}
```

---

## Troubleshooting

### Backup Fails with "Access Denied"
- Run PowerShell as Administrator
- Ensure no applications are accessing WSL files
- Verify WSL is fully shutdown: `wsl --shutdown`

### Backup File is Much Smaller Than Expected
- May indicate incomplete backup
- Ensure WSL was fully running before shutdown
- Check if Docker containers/images are present

### Restore Shows "Invalid tar file"
- Backup may be corrupted
- Try alternate backup location
- Verify file size matches expected size
- Do not interrupt backup process

### Test Restore Fails to Start
- Check available disk space on test location
- Ensure unique name for test instance
- Verify backup file is not corrupted
- Check Windows event logs for errors

### Cannot Delete Test Instance
```powershell
# Force terminate if stuck
wsl --terminate Ubuntu_Test
Start-Sleep -Seconds 5
wsl --unregister Ubuntu_Test
```

---

## Best Practices

### Regular Backup Schedule
- **Weekly:** Full WSL export after significant changes
- **Before major updates:** Windows updates, WSL updates, major project changes
- **After milestones:** Project phase completions, working feature implementations
- **Multiple locations:** Keep backups on different physical drives

### Backup Naming Convention
```
Ubuntu_backup_YYYY-MM-DD_description.tar

Examples:
Ubuntu_backup_2025-11-02_phase1_complete.tar
Ubuntu_backup_2025-11-15_before_windows_update.tar
Ubuntu_backup_2025-12-01_working_vca.tar
```

### Storage Management
- Keep at least 2 recent backups (different locations)
- Archive old backups to external drive monthly
- Delete backups older than 3 months (keep milestones)
- Verify backup integrity before deleting old backups

### Before Deleting Old Backups
1. Create fresh backup of current state
2. Verify new backup with test restore
3. Confirm new backup file size is reasonable
4. Document what backup contains (git commit, state)
5. Only then delete old backup

---

## Emergency Recovery

### If WSL Won't Start and You Have Backup

```powershell
# 1. Don't panic - your backup has everything
wsl --shutdown

# 2. Try safe restart first
wsl --list --verbose
# If shows errors, proceed to restore

# 3. Full restore procedure
wsl --unregister Ubuntu
wsl --import Ubuntu "C:\WSL\Ubuntu" "E:\WSL-Backups\Ubuntu_backup_2025-11-02.tar"
wsl --set-default Ubuntu

# 4. Start and verify
wsl
cd /home/indigo/my-project3/Dappva
git status
```

### If No Backup Available
- Reinstall WSL from scratch
- Install Ubuntu from Microsoft Store
- Clone project from git repository
- Reinstall Docker and pull images
- Reconfigure environment

This is why backups are critical!

---

## Additional Resources

### WSL Commands Reference
```powershell
# List all WSL distributions
wsl --list --verbose

# Get WSL version
wsl --version

# Update WSL
wsl --update

# Check disk usage
wsl df -h

# Compact VHDX (reclaim space)
wsl --shutdown
Optimize-VHD -Path "C:\WSL\Ubuntu\ext4.vhdx" -Mode Full
```

### Backup Size Optimization
```bash
# Inside WSL before backup: Clean up to reduce backup size

# Remove Docker containers not needed
docker system prune -a

# Clean apt cache
sudo apt-get clean
sudo apt-get autoclean

# Remove old logs
sudo journalctl --vacuum-time=7d

# Clear bash history if desired
history -c
```

---

## Quick Reference Card

| Task | Command |
|------|---------|
| **Backup WSL** | `wsl --shutdown; wsl --export Ubuntu "E:\backup.tar"` |
| **Restore WSL** | `wsl --unregister Ubuntu; wsl --import Ubuntu "C:\WSL\Ubuntu" "E:\backup.tar"` |
| **Test Backup** | `wsl --import Ubuntu_Test "E:\WSL-Test" "E:\backup.tar"` |
| **Check Status** | `wsl --list --verbose` |
| **Check Backups** | `Get-ChildItem "E:\WSL-Backups\*.tar"` |
| **Shutdown WSL** | `wsl --shutdown` |
| **Start WSL** | `wsl` |

---

**Document Version:** 1.0
**Last Updated:** 2025-11-02
**Author:** VCA Development Team
