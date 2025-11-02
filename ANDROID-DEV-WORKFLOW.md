# Android Development Workflow Guide

**Project**: VCA Assistant
**Purpose**: Complete workflow for Android app development using WSL2 + command-line builds
**Created**: 2025-11-02

---

## Overview

This guide documents the complete development workflow for the VCA Assistant Android app, from code editing to testing on your Samsung A05 device.

### The Hybrid Workflow

Due to Android Studio's WSL2 Gradle sync issues, we use a **hybrid approach**:

1. **Edit code** in Android Studio (Windows) - Get syntax highlighting, autocomplete, Claude Code integration
2. **Build & install** from WSL2 terminal - Fast, reliable command-line builds
3. **Test** on Samsung A05 - Real device testing via USB debugging

---

## Prerequisites Checklist

### ✅ Development Environment
- [x] Android Studio installed via JetBrains Toolbox (Windows)
- [x] JDK 21 installed in WSL2 Ubuntu
- [x] Gradle 8.9 configured
- [x] Android SDK installed at `C:\Users\Mike\AppData\Local\Android\Sdk`
- [x] Project location: `/home/indigo/my-project3/Dappva/VCAAssistant`

### ✅ Phone Setup (Samsung A05)
- [x] Developer Mode enabled
- [x] USB Debugging enabled
- [x] Connected via USB cable

---

## Part 1: Phone Setup & USB Debugging

### Enable Developer Mode (Samsung A05)

1. **Open Settings** on your phone
2. **Navigate to**: Settings → About Phone → Software Information
3. **Tap "Build Number" 7 times** (you'll see a toast message: "Developer mode enabled")
4. **Go back** to main Settings menu
5. **Find "Developer Options"** (usually under Settings → System or at bottom of Settings)

### Enable USB Debugging

1. **Open Developer Options**
2. **Scroll down to "USB Debugging"**
3. **Toggle it ON**
4. **Accept the prompt** "Allow USB debugging?"

### Verify ADB Connection

```bash
# Connect phone via USB cable

# Check if device is recognized
adb devices

# Expected output:
# List of devices attached
# <device-serial>    device

# If you see "unauthorized", check phone for authorization prompt and tap "Allow"
```

**Troubleshooting**:
- If `adb` command not found, you may need to use the full path: `/mnt/c/Users/Mike/AppData/Local/Android/Sdk/platform-tools/adb`
- If device shows as "offline", unplug and replug USB cable
- If device not showing, try a different USB cable or port
- Make sure USB is set to "File Transfer" mode (not just charging)

---

## Part 2: Build Commands

### Navigate to Project Directory

```bash
cd /home/indigo/my-project3/Dappva/VCAAssistant
```

### Essential Build Commands

#### Clean Build
Removes all build artifacts and rebuilds from scratch:
```bash
./gradlew clean build --no-daemon
```
**Use when**: Major code changes, dependency updates, or mysterious build errors

**Build time**: ~1m 18s

---

#### Build Debug APK
Creates debug APK without installing:
```bash
./gradlew assembleDebug
```
**Output location**: `app/build/outputs/apk/debug/app-debug.apk`

**Use when**: You want to manually distribute the APK

---

#### Install Debug APK
**Most common command** - builds and installs in one step:
```bash
./gradlew installDebug
```
**This command**:
1. Compiles all Kotlin code
2. Packages resources
3. Creates debug APK
4. Installs to connected device via ADB
5. Replaces any previous version

**Build time**: ~45s (incremental), ~1m 18s (clean)

**Success output**:
```
BUILD SUCCESSFUL in 45s
42 actionable tasks: 42 executed
```

---

#### Fast Incremental Build
After initial build, subsequent builds are much faster:
```bash
./gradlew installDebug
```
Only rebuilds changed files. Typical time: 10-30s

---

#### Uninstall from Phone
```bash
./gradlew uninstallDebug
```
Or via ADB:
```bash
adb uninstall com.vca.assistant
```

---

#### View Build Outputs
```bash
# List all build tasks
./gradlew tasks

# View project structure
./gradlew projects

# Check dependencies
./gradlew dependencies
```

---

## Part 3: Creating Files on Phone

### Method A: Using ADB Push (Recommended for Testing)

**Advantage**: Fast, scriptable, works from WSL2 terminal

```bash
# Navigate to a temp directory or project root
cd /home/indigo/my-project3/Dappva/VCAAssistant

# Create the test file locally
echo "Hello World" > hello-world.txt

# Create the VCA directory on phone (if it doesn't exist)
adb shell mkdir -p /sdcard/Documents/VCA

# Push file to phone
adb push hello-world.txt /sdcard/Documents/VCA/

# Verify it was created
adb shell ls -la /sdcard/Documents/VCA/

# Read the file contents to verify
adb shell cat /sdcard/Documents/VCA/hello-world.txt
```

**Expected output**:
```
hello-world.txt: 1 file pushed, 0 skipped. 0.0 MB/s (12 bytes in 0.001s)
```

---

### Method B: Manual Creation (Using Phone)

**Advantage**: Realistic user experience, tests real-world scenarios

1. **Open "My Files" app** on Samsung A05 (or "Files" app)
2. **Navigate to Internal Storage** → Documents
3. **Create new folder** named "VCA" (if it doesn't exist)
   - Tap ⋮ (three dots) → New folder → Name it "VCA"
4. **Open VCA folder**
5. **Create new file**:
   - Tap ⋮ (three dots) → New file
   - Name it "hello-world.txt"
6. **Edit the file**:
   - Tap the file to open
   - Select your preferred text editor
   - Type "Hello World"
   - Save

---

### Method C: ADB Shell Interactive

**Advantage**: Direct shell access, useful for debugging

```bash
# Open interactive shell on phone
adb shell

# Navigate to Documents
cd /sdcard/Documents

# Create VCA directory
mkdir -p VCA

# Navigate into it
cd VCA

# Create file with content
echo "Hello World" > hello-world.txt

# Verify
cat hello-world.txt

# Exit shell
exit
```

---

## Part 4: Grant Storage Permissions

The app needs permission to read files from `/sdcard/Documents/VCA/`.

### Option A: Grant Manually (Faster for Testing)

1. **Open Settings** on phone
2. **Navigate to**: Settings → Apps → VCA Assistant
3. **Tap "Permissions"**
4. **Find "Files and media" or "Storage"**
5. **Select "Allow"**

### Option B: Grant via ADB

```bash
# For Android 12 and below
adb shell pm grant com.vca.assistant android.permission.READ_EXTERNAL_STORAGE

# For Android 13+
adb shell pm grant com.vca.assistant android.permission.READ_MEDIA_IMAGES
```

---

## Part 5: Complete Testing Workflow

### Step-by-Step: Hello World Test

#### 1. Build and Install the App
```bash
cd /home/indigo/my-project3/Dappva/VCAAssistant
./gradlew installDebug
```

Wait for `BUILD SUCCESSFUL` message.

---

#### 2. Create the Test File on Phone
```bash
# Create file locally
echo "Hello World" > hello-world.txt

# Create directory on phone
adb shell mkdir -p /sdcard/Documents/VCA

# Push to phone
adb push hello-world.txt /sdcard/Documents/VCA/

# Verify
adb shell cat /sdcard/Documents/VCA/hello-world.txt
```

**Expected**: Should output "Hello World"

---

#### 3. Grant Storage Permission
```bash
adb shell pm grant com.vca.assistant android.permission.READ_EXTERNAL_STORAGE
```

Or manually via Settings → Apps → VCA Assistant → Permissions → Files and media → Allow

---

#### 4. Launch the App

**On your phone**:
1. Open app drawer
2. Find "VCA Assistant" app icon
3. Tap to launch

**Expected behavior**:
- App should open immediately
- Screen should display: **"Hello World"** (the contents of your file)

---

#### 5. Test Error Handling

**Delete the file**:
```bash
adb shell rm /sdcard/Documents/VCA/hello-world.txt
```

**Force-stop and relaunch the app**:
```bash
adb shell am force-stop com.vca.assistant
# Then manually launch app on phone
```

**Expected behavior**:
- App should display: **"File not found. Please create /sdcard/Documents/VCA/hello-world.txt"**

---

#### 6. Test File Update

**Update file contents**:
```bash
echo "Updated content from WSL2!" > hello-world.txt
adb push hello-world.txt /sdcard/Documents/VCA/
```

**Restart the app**:
```bash
adb shell am force-stop com.vca.assistant
# Launch manually on phone
```

**Expected behavior**:
- App should display: **"Updated content from WSL2!"**

---

## Part 6: View Logs (Debugging)

### Real-time Logcat Monitoring

```bash
# View all logs from your app
adb logcat | grep VCA

# View all Android logs (verbose)
adb logcat

# Clear logs first, then monitor
adb logcat -c
adb logcat | grep -i "vca\|error\|exception"

# Save logs to file
adb logcat > app-logs.txt
```

### View Crash Reports

```bash
# View only errors and warnings
adb logcat *:E *:W

# View app crashes
adb logcat | grep -i "crash\|fatal\|exception"
```

---

## Part 7: Common Build Issues & Solutions

### Issue: `BUILD FAILED` - Gradle Daemon

**Error**:
```
Gradle Daemon is not available
```

**Solution**:
```bash
# Kill any running daemons
./gradlew --stop

# Rebuild
./gradlew clean build --no-daemon
```

---

### Issue: `adb: device offline`

**Solution**:
```bash
# Restart ADB server
adb kill-server
adb start-server
adb devices
```

---

### Issue: Permission Denied

**Error**:
```
Permission denied: /sdcard/Documents/VCA/hello-world.txt
```

**Solution**:
1. Check permissions were granted: Settings → Apps → VCA Assistant → Permissions
2. Re-grant via ADB:
   ```bash
   adb shell pm grant com.vca.assistant android.permission.READ_EXTERNAL_STORAGE
   ```

---

### Issue: File Not Found (but file exists)

**Debugging**:
```bash
# Verify file exists
adb shell ls -la /sdcard/Documents/VCA/

# Check file permissions
adb shell ls -l /sdcard/Documents/VCA/hello-world.txt

# Verify path in app logs
adb logcat | grep "hello-world"
```

**Common causes**:
- File created in wrong location
- Typo in filename (Linux is case-sensitive)
- Permission not granted

---

### Issue: App Crashes on Launch

**Debugging**:
```bash
# View crash logs
adb logcat | grep -i "crash\|exception\|fatal"

# Install with verbose output
./gradlew installDebug --info
```

---

## Part 8: Quick Reference

### One-Command Testing Cycle

```bash
# Complete rebuild, install, and launch in one command chain
cd /home/indigo/my-project3/Dappva/VCAAssistant && \
./gradlew installDebug && \
adb shell am force-stop com.vca.assistant && \
adb shell am start -n com.vca.assistant/.MainActivity
```

---

### File Management Commands

```bash
# Create file on phone
adb shell "echo 'Your text here' > /sdcard/Documents/VCA/hello-world.txt"

# Read file from phone
adb shell cat /sdcard/Documents/VCA/hello-world.txt

# Delete file
adb shell rm /sdcard/Documents/VCA/hello-world.txt

# List directory contents
adb shell ls -la /sdcard/Documents/VCA/

# Pull file from phone to WSL2
adb pull /sdcard/Documents/VCA/hello-world.txt ./
```

---

### App Management Commands

```bash
# Install app
./gradlew installDebug

# Uninstall app
./gradlew uninstallDebug

# Force-stop app
adb shell am force-stop com.vca.assistant

# Launch app
adb shell am start -n com.vca.assistant/.MainActivity

# Clear app data (reset to fresh install state)
adb shell pm clear com.vca.assistant
```

---

## Part 9: Development Best Practices

### Workflow Recommendations

1. **Edit in Android Studio**
   - Open project from `\\wsl$\Ubuntu\home\indigo\my-project3\Dappva\VCAAssistant`
   - Use for syntax highlighting, autocomplete, refactoring
   - Save frequently (Ctrl+S)

2. **Build in WSL2 Terminal**
   - Keep a terminal window open in VSCode or Windows Terminal
   - Run `./gradlew installDebug` after saving changes
   - Watch for compilation errors

3. **Test on Real Device**
   - Always test on Samsung A05 (not emulator)
   - Keep USB debugging enabled
   - Monitor logs via `adb logcat`

4. **Iterate Quickly**
   - Make small, incremental changes
   - Build and test frequently
   - Use incremental builds (don't always use `clean`)

---

### When to Use Each Build Command

| Command | Use Case | Build Time |
|---------|----------|------------|
| `./gradlew installDebug` | Normal development (most common) | 10-45s |
| `./gradlew clean build` | After major changes, dependency updates | ~1m 18s |
| `./gradlew assembleDebug` | Create APK without installing | ~45s |
| `./gradlew tasks` | List available build tasks | 5s |

---

## Part 10: Next Steps After Hello World Test

Once the hello-world test succeeds, you're ready to implement the full VCA app!

### Implementation Order (Recommended)

1. **WebSocket Client** (`WebSocketClient.kt`)
   - Connect to Session Manager at `ws://192.168.X.X:5000/ws`
   - Test with echo messages

2. **Audio Recorder** (`AudioRecorder.kt`)
   - Record microphone input
   - Test with simple audio file creation

3. **Wake Word Detector** (`WakeWordDetector.kt`)
   - Download Vosk model to `/sdcard/Documents/VCA/models/`
   - Test wake word detection offline

4. **Audio Player** (`AudioPlayer.kt`)
   - Play audio responses from Session Manager
   - Test with sample WAV file

5. **Voice Assistant Service** (`VoiceAssistantService.kt`)
   - Integrate all components
   - Full end-to-end pipeline

6. **Enhanced MainActivity**
   - Add permissions requests
   - Add UI controls (start/stop)
   - Add status indicators

### Reference Documentation

- **Full implementation guide**: [android-app-development-guide.md](android-app-development-guide.md)
- **Architecture overview**: [ARCHITECTURE-REVISED-NO-HA.md](ARCHITECTURE-REVISED-NO-HA.md)
- **Session Manager details**: [session_manager/README.md](session_manager/README.md)

---

## Part 11: Troubleshooting Checklist

Before asking for help, verify:

- [ ] Phone shows as `device` (not `unauthorized` or `offline`) in `adb devices`
- [ ] Build completes with `BUILD SUCCESSFUL` message
- [ ] App appears in phone's app drawer
- [ ] Storage permissions granted (Settings → Apps → VCA Assistant → Permissions)
- [ ] File exists at exact path: `/sdcard/Documents/VCA/hello-world.txt`
- [ ] File has readable contents (`adb shell cat /sdcard/Documents/VCA/hello-world.txt`)
- [ ] App launches without crashing
- [ ] Logs show no errors (`adb logcat | grep -i error`)

---

## Summary

### The Complete Cycle

```
┌─────────────────────────────────────────────────────────────┐
│  1. EDIT CODE (Android Studio - Windows)                    │
│     ↓                                                        │
│  2. SAVE FILES (Ctrl+S)                                      │
│     ↓                                                        │
│  3. BUILD & INSTALL (WSL2 Terminal)                          │
│     ./gradlew installDebug                                   │
│     ↓                                                        │
│  4. TEST ON PHONE (Samsung A05)                              │
│     Launch app, verify behavior                              │
│     ↓                                                        │
│  5. CHECK LOGS (WSL2 Terminal)                               │
│     adb logcat | grep VCA                                    │
│     ↓                                                        │
│  6. ITERATE (Back to step 1)                                 │
└─────────────────────────────────────────────────────────────┘
```

**Build time**: 10-45s (incremental), 1m 18s (clean)
**Total cycle time**: ~1-2 minutes per iteration

---

## Success Criteria

You'll know this workflow is successful when:

✅ You can edit code in Android Studio
✅ Build completes in WSL2 terminal without errors
✅ App installs on Samsung A05 automatically
✅ App reads and displays "Hello World" from the text file
✅ You can update the file and see changes after restarting app
✅ Error messages appear when file is missing

**Once this test passes, you're ready to build the full VCA app!**

---

**Document Version**: 1.0
**Last Updated**: 2025-11-02
**Project**: VCA Assistant Android App
**Author**: Development workflow with Claude Code
