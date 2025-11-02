# Android Studio WSL2 Write Permission Workaround
**Date:** 2025-11-02
**Issue:** Android Studio cannot write to `\\wsl$\Ubuntu\` paths during project creation

---

## The Problem

JetBrains IDEs (including Android Studio) have a known limitation with WSL2:
- **Reading from WSL2:** ✅ Works perfectly
- **Writing to WSL2 during project creation:** ❌ Fails with "not writable" error
- **Editing existing files in WSL2:** ✅ Works fine after project is created

**Root cause:** Windows file permissions vs WSL2 filesystem permissions conflict during initial project scaffold.

---

## Solution: Two-Step Approach

### Step 1: Create Project in Windows Temp Location

**From Android Studio New Project dialog:**

1. **Save location:** Use Windows path (NOT WSL2)
   ```
   C:\Users\<YourUsername>\AndroidStudioProjects\VCAAssistant
   ```

2. **Other settings:**
   - Name: `VCA Assistant`
   - Package name: `com.vca.assistant`
   - Language: Kotlin
   - Minimum SDK: API 26 ("Oreo"; Android 8.0)
   - Build configuration: Kotlin DSL (build.gradle.kts)

3. Click **"Finish"**

4. Wait for Gradle sync to complete (~5-10 minutes first time)

### Step 2: Move Project to WSL2

**After Gradle sync completes:**

**Close Android Studio** (important - close it completely)

**From WSL2 terminal:**
```bash
# Navigate to Dappva directory
cd /home/indigo/my-project3/Dappva

# Copy project from Windows to WSL2
cp -r /mnt/c/Users/<YourUsername>/AndroidStudioProjects/VCAAssistant ./

# Verify copy
ls -la VCAAssistant/

# Expected output:
# app/
# gradle/
# build.gradle.kts
# settings.gradle.kts
# etc.

# Fix permissions (ensure proper ownership)
chown -R indigo:indigo VCAAssistant/
chmod -R u+rw VCAAssistant/
```

**From Windows (optional cleanup):**
```powershell
# Delete the Windows temp copy (saves disk space)
Remove-Item -Recurse -Force "C:\Users\<YourUsername>\AndroidStudioProjects\VCAAssistant"
```

### Step 3: Reopen Project from WSL2

**Open Android Studio**

**From Welcome screen:**
1. Click **"Open"**
2. Navigate to: `\\wsl$\Ubuntu\home\indigo\my-project3\Dappva\VCAAssistant`
3. Click **"OK"**

**Android Studio will:**
- Open project from WSL2 path ✅
- Read all files successfully ✅
- Allow editing files ✅
- Build/compile works ✅
- Gradle sync works ✅

**Note:** The "not writable" error only affects initial project creation, not ongoing development.

---

## Alternative: Use WSL2 Native Development (Advanced)

If the above doesn't work, you can develop entirely in WSL2:

### Install Android Studio in WSL2 with WSLg

**Requirements:**
- Windows 11 (WSLg built-in)
- OR Windows 10 with WSLg installed

**Install in WSL2:**
```bash
# Install dependencies
sudo apt update
sudo apt install -y openjdk-17-jdk

# Download Android Studio for Linux
cd /tmp
wget https://redirector.gvt1.com/edgedl/android/studio/ide-zips/2024.1.1.12/android-studio-2024.1.1.12-linux.tar.gz

# Extract to /opt
sudo tar -xzf android-studio-*-linux.tar.gz -C /opt/

# Launch
/opt/android-studio/bin/studio.sh
```

**Pros:**
- Native WSL2 development
- No permission issues
- Full file system access

**Cons:**
- GUI may be slower (WSLg overhead)
- No Android Emulator (requires nested virtualization)
- More complex setup

---

## Recommended Approach

**Use the two-step workaround (Steps 1-3 above):**
1. Create project in Windows
2. Move to WSL2 via `cp` command
3. Reopen from WSL2 path

**Why this works:**
- Initial scaffolding happens in Windows (no permission issues)
- Development happens in WSL2 (Claude Code access, fast builds)
- Best of both worlds

---

## Verification Steps

After moving project to WSL2 and reopening:

**1. Check project path in AS:**
- Look at bottom-right of AS window
- Should show: `\\wsl$\Ubuntu\home\indigo\my-project3\Dappva\VCAAssistant`

**2. Test file editing:**
- Open `app/src/main/java/com/vca/assistant/MainActivity.kt`
- Make a small edit (add a comment)
- Save (Ctrl+S)
- Verify no errors

**3. Test Gradle sync:**
- Click "File" → "Sync Project with Gradle Files"
- Should complete successfully

**4. Verify from WSL2:**
```bash
# Check recent modification
ls -lt /home/indigo/my-project3/Dappva/VCAAssistant/app/src/main/java/com/vca/assistant/

# Should show MainActivity.kt with recent timestamp
```

---

## Next Steps After Setup

Once project is in WSL2 and reopened:

1. **Install Claude Code [Beta] plugin**
   - Settings → Plugins → Marketplace
   - Search "Claude Code [Beta]"
   - Install and restart

2. **Configure dependencies**
   - Update `app/build.gradle.kts` (see ANDROID-STUDIO-SETUP-GUIDE.md Step 6)
   - Add OkHttp, Vosk, Coroutines

3. **Start development**
   - Press Ctrl+Esc to launch Claude Code
   - Ask Claude to generate WebSocketClient.kt

---

## Troubleshooting

### Issue: "Cannot sync Gradle" after moving to WSL2

**Solution:**
```bash
# From WSL2, regenerate Gradle wrapper
cd /home/indigo/my-project3/Dappva/VCAAssistant
./gradlew wrapper --gradle-version 8.9
```

### Issue: "JDK not found" in AS

**Solution:**
- File → Project Structure → SDK Location
- Set JDK location to AS embedded JDK:
  ```
  C:\Program Files\Android\Android Studio\jbr
  ```

### Issue: Files not updating in AS after WSL2 changes

**Solution:**
- File → Invalidate Caches → "Invalidate and Restart"

---

## Summary

✅ **Working solution:** Create in Windows → Move to WSL2 → Reopen from WSL2
❌ **Doesn't work:** Direct creation in `\\wsl$\` path (permission error)
⚠️ **Known limitation:** JetBrains IDEs + WSL2 initial write permissions

**Total time:** ~15-20 minutes (including Gradle sync)

---

**Document Status:** Active workaround for WSL2 development
**Last Updated:** 2025-11-02
**Related:** ANDROID-STUDIO-SETUP-GUIDE.md (main guide)
