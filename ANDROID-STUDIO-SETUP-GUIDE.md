# Android Studio Setup Guide - Windows with WSL2 Integration
**VCA 1.0 - Custom Android App Development**
**Date:** 2025-11-02
**Platform:** Windows Android Studio + WSL2 Ubuntu Project Files

---

## Overview

This guide walks through setting up Android Studio on Windows to develop the VCA Android app while keeping project files in WSL2 Ubuntu filesystem.

**Architecture:**
```
Windows Android Studio (Native)
         ↕
   UNC Path Access
         ↕
WSL2 Ubuntu Filesystem (/home/indigo/my-project3/Dappva/)
         ↕
Claude Code CLI (WSL2 Terminal)
```

**Key Benefits:**
- Full Android Studio features (emulator, debugging, build tools)
- Claude Code integration for AI-assisted development
- Seamless file sync between Windows and WSL2
- Physical device testing (Samsung A05)

---

## Prerequisites

### Before You Begin

**Installed:**
- ✅ Windows 10/11 with WSL2 enabled
- ✅ Android Studio (installed via JetBrains Toolbox)
- ✅ WSL2 Ubuntu distribution

**Required:**
- [ ] JDK 17+ (will verify/install)
- [ ] Android SDK (will install via AS)
- [ ] WSL2 project directory accessible

**Device:**
- Samsung A05 (Android 15) for testing

---

## Step 1: Verify Android Studio Installation

### 1.1 Check Installation Location

**Via JetBrains Toolbox:**
1. Open JetBrains Toolbox
2. Verify Android Studio is listed
3. Note version (should be Koala 2024.1.1+ or later)

**Expected Location:**
```
C:\Users\<YourUsername>\AppData\Local\JetBrains\Toolbox\apps\AndroidStudio\
```

### 1.2 Launch Android Studio

1. Click "Android Studio" in JetBrains Toolbox
2. You should see the "Welcome to Android Studio" start page
3. ✅ **YOU ARE HERE**

---

## Step 2: Initial Android Studio Configuration

### 2.1 Install Android SDK

**From Welcome Screen:**
1. Click **"More Actions"** → **"SDK Manager"**
2. In SDK Manager window:
   - **SDK Platforms** tab:
     - Check ☑ **Android 14.0 (API 34)** (latest)
     - Check ☑ **Android 8.0 (Oreo) API 26** (minimum for VCA)
   - **SDK Tools** tab:
     - Check ☑ **Android SDK Build-Tools 34**
     - Check ☑ **Android Emulator** (optional, for testing)
     - Check ☑ **Android SDK Platform-Tools** (includes adb)
     - Check ☑ **Google Play Services** (optional)
3. Click **"Apply"**
4. Accept licenses
5. Click **"OK"** to download and install (may take 10-20 minutes)

**Note SDK Location:**
```
Default: C:\Users\<YourUsername>\AppData\Local\Android\Sdk
```

### 2.2 Verify JDK Installation

**Check if JDK 17+ is installed:**

**Option A: From Android Studio**
1. Click **"More Actions"** → **"SDK Manager"**
2. Click **"SDK Tools"** tab
3. Check if **"JDK (Java Development Kit)"** is listed
4. If not listed, Android Studio will use embedded JDK (this is OK)

**Option B: From PowerShell**
```powershell
# Open PowerShell
java -version

# Expected output (if installed):
# openjdk version "17.x.x" or higher
```

**If Java not found:**
- Android Studio includes embedded JDK 17
- No action needed for VCA development
- Gradle will use embedded JDK automatically

---

## Step 3: Verify WSL2 Access from Windows

### 3.1 Test WSL2 Mount

**From Windows File Explorer:**
1. Press `Win + E` to open File Explorer
2. In address bar, type: `\\wsl$\`
3. Press Enter
4. You should see your WSL2 distributions listed (e.g., `Ubuntu`)

**Navigate to project directory:**
```
\\wsl$\Ubuntu\home\indigo\my-project3\Dappva\
```

**Expected Files:**
- CHANGELOG.md
- phase-0-completion-status.md
- android-app-development-guide.md
- session_manager/ (directory)
- etc.

**If WSL2 mount not working:**
```bash
# From WSL2 terminal, verify WSL is running:
wsl --status

# If WSL not running, start it:
wsl
```

### 3.2 Create Android Project Directory in WSL2

**From WSL2 terminal:**
```bash
# Navigate to project root
cd /home/indigo/my-project3/Dappva

# Create Android app directory
mkdir -p VCAAssistant

# Verify creation
ls -la VCAAssistant/

# Expected output:
# drwxr-xr-x 2 indigo indigo 4096 Nov  2 12:34 VCAAssistant
```

**From Windows, verify accessible:**
```
\\wsl$\Ubuntu\home\indigo\my-project3\Dappva\VCAAssistant
```

---

## Step 4: Create VCA Android Project

### 4.1 Start New Project

**From Android Studio Welcome Screen:**
1. Click **"New Project"**
2. Select **"Empty Activity"** template
3. Click **"Next"**

### 4.2 Configure Project

**Project Configuration:**
- **Name:** `VCA Assistant`
- **Package name:** `com.vca.assistant`
- **Save location:** `\\wsl$\Ubuntu\home\indigo\my-project3\Dappva\VCAAssistant`

  ⚠️ **IMPORTANT:** Type this EXACT path in the location field

- **Language:** Kotlin
- **Minimum SDK:** API 26 ("Oreo"; Android 8.0)
- **Build configuration language:** Kotlin DSL (build.gradle.kts)

**Click "Finish"**

### 4.3 Wait for Initial Sync

**Android Studio will:**
1. Create project structure
2. Download Gradle wrapper
3. Download dependencies
4. Sync Gradle files

**This may take 5-10 minutes on first run.**

**Progress shown in bottom status bar:**
```
Building 'VCA Assistant' Gradle project info...
Gradle sync in progress...
```

**When complete, you'll see:**
```
BUILD SUCCESSFUL in 2m 34s
```

---

## Step 5: Verify Project Structure

### 5.1 Check Files in WSL2

**From WSL2 terminal:**
```bash
cd /home/indigo/my-project3/Dappva/VCAAssistant

# List directory structure
tree -L 2 -a

# Expected output:
# .
# ├── .gradle/
# ├── .idea/
# ├── app/
# │   ├── build.gradle.kts
# │   ├── src/
# │   └── ...
# ├── gradle/
# ├── build.gradle.kts
# ├── settings.gradle.kts
# ├── gradle.properties
# └── gradlew
```

**If `tree` not installed:**
```bash
# Simpler check:
ls -la /home/indigo/my-project3/Dappva/VCAAssistant/

# Verify these exist:
# - app/
# - gradle/
# - build.gradle.kts
# - settings.gradle.kts
```

### 5.2 Verify in Android Studio

**Project Structure View:**
1. In Android Studio, click **"Project"** tab (left sidebar)
2. Change dropdown from "Android" to **"Project"**
3. Expand folders to see:
   ```
   VCAAssistant/
   ├── app/
   │   ├── src/
   │   │   ├── main/
   │   │   │   ├── java/com/vca/assistant/
   │   │   │   │   └── MainActivity.kt
   │   │   │   ├── res/
   │   │   │   └── AndroidManifest.xml
   │   │   └── test/
   │   └── build.gradle.kts
   ├── gradle/
   ├── build.gradle.kts
   └── settings.gradle.kts
   ```

---

## Step 6: Configure Project for VCA Requirements

### 6.1 Update app/build.gradle.kts

**Open in Android Studio:**
1. Navigate to `app/build.gradle.kts`
2. Replace contents with VCA configuration:

**File:** `VCAAssistant/app/build.gradle.kts`
```kotlin
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.vca.assistant"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.vca.assistant"
        minSdk = 26
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }
}

dependencies {
    // Core Android
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.appcompat:appcompat:1.6.1")
    implementation("com.google.android.material:material:1.11.0")
    implementation("androidx.constraintlayout:constraintlayout:2.1.4")

    // Coroutines
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")

    // WebSocket (OkHttp)
    implementation("com.squareup.okhttp3:okhttp:4.12.0")

    // Vosk Speech Recognition
    implementation("com.alphacephei:vosk-android:0.3.47")

    // Permissions
    implementation("com.google.accompanist:accompanist-permissions:0.33.2-alpha")

    // Testing
    testImplementation("junit:junit:4.13.2")
    androidTestImplementation("androidx.test.ext:junit:1.1.5")
    androidTestImplementation("androidx.test.espresso:espresso-core:3.5.1")
}
```

**Click "Sync Now"** when prompted (top-right of editor)

### 6.2 Update AndroidManifest.xml

**Open:** `VCAAssistant/app/src/main/AndroidManifest.xml`

**Replace with:**
```xml
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools">

    <!-- Network permissions -->
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />

    <!-- Audio permissions -->
    <uses-permission android:name="android.permission.RECORD_AUDIO" />
    <uses-permission android:name="android.permission.MODIFY_AUDIO_SETTINGS" />

    <!-- Foreground service (always-on listening) -->
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE_MICROPHONE" />
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />

    <!-- Wake lock (prevent sleep during session) -->
    <uses-permission android:name="android.permission.WAKE_LOCK" />

    <application
        android:allowBackup="true"
        android:dataExtractionRules="@xml/data_extraction_rules"
        android:fullBackupContent="@xml/backup_rules"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/Theme.VCAAssistant"
        tools:targetApi="31">

        <!-- Main Activity -->
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:screenOrientation="portrait">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

    </application>

</manifest>
```

**Save file** (Ctrl+S)

### 6.3 Verify Gradle Sync

**After saving both files:**
1. Click **"Sync Now"** in top-right banner
2. Wait for Gradle sync to complete (may take 2-5 minutes to download dependencies)
3. Check bottom status bar shows: **"BUILD SUCCESSFUL"**

**If sync fails:**
- Check error messages in "Build" tab (bottom panel)
- Common issues:
  - Internet connection needed (downloads dependencies)
  - Proxy settings (if behind corporate firewall)
  - JDK version mismatch (use embedded JDK 17)

---

## Step 7: Test Build

### 7.1 Clean Build

**From Android Studio menu:**
1. Click **"Build"** → **"Clean Project"**
2. Wait for completion (~30 seconds)
3. Click **"Build"** → **"Rebuild Project"**
4. Wait for completion (2-5 minutes first time)

**Check "Build" output:**
```
BUILD SUCCESSFUL in 3m 12s
45 actionable tasks: 45 executed
```

### 7.2 Verify APK Creation

**After successful build:**
```
Build output:
VCAAssistant/app/build/outputs/apk/debug/app-debug.apk created
```

✅ **Build successful! Android project is configured correctly.**

---

## Step 8: Install Claude Code [Beta] Plugin

### 8.1 Open Plugin Manager

**From Android Studio:**
1. Click **"File"** → **"Settings"** (or `Ctrl+Alt+S`)
2. Navigate to **"Plugins"** in left sidebar
3. Click **"Marketplace"** tab

### 8.2 Install Plugin

**Search and install:**
1. Type `Claude Code` in search box
2. Find **"Claude Code [Beta]"** by Anthropic PBC
3. Click **"Install"**
4. Click **"Accept"** on plugin agreement
5. Click **"Restart IDE"** when prompted

**Android Studio will restart (may take 1-2 minutes)**

### 8.3 Verify Installation

**After restart:**
1. Open Android Studio
2. Press `Ctrl+Esc` (Windows) or `Cmd+Esc` (Mac)
3. Claude Code terminal should open at bottom of IDE

**If Claude Code doesn't open:**
- Check plugin is enabled: **"Settings"** → **"Plugins"** → **"Installed"**
- Verify Claude Code CLI is installed in WSL2:
  ```bash
  # From WSL2 terminal:
  claude-code --version
  ```

---

## Step 9: Configure Samsung A05 for Testing

### 9.1 Enable Developer Options

**On Samsung A05:**
1. Open **"Settings"**
2. Navigate to **"About phone"**
3. Tap **"Build number"** 7 times
4. You'll see message: "Developer mode enabled"

### 9.2 Enable USB Debugging

**On Samsung A05:**
1. Go back to **"Settings"**
2. Scroll down to **"Developer options"**
3. Toggle **"Developer options"** ON
4. Scroll down to **"USB debugging"**
5. Toggle **"USB debugging"** ON
6. Confirm security warning

### 9.3 Connect Device

**Physical connection:**
1. Connect Samsung A05 to PC via USB cable
2. On phone, you'll see popup: **"Allow USB debugging?"**
3. Check ☑ **"Always allow from this computer"**
4. Tap **"Allow"**

**Verify in Android Studio:**
1. Click device dropdown (top toolbar, next to green play button)
2. You should see: **"Samsung SM-A055F"** (or similar)
3. If not visible:
   - Try different USB cable
   - Ensure USB mode is "File Transfer" (not just charging)
   - Restart Android Studio

---

## Step 10: Test Run on Device

### 10.1 Run App

**From Android Studio:**
1. Select **"Samsung SM-A055F"** from device dropdown
2. Click green **"Run"** button (▶) or press `Shift+F10`
3. Wait for build and deployment (~1-2 minutes first run)

**On Samsung A05:**
- App will install automatically
- App will launch
- You should see default "Hello World" or empty activity

✅ **If app runs successfully, setup is complete!**

---

## Step 11: Using Claude Code with Android Studio

### 11.1 Quick Launch

**From Android Studio:**
- Press `Ctrl+Esc` to open Claude Code terminal
- Terminal opens at bottom of IDE
- Claude Code has access to your project files

### 11.2 File Context Sharing

**Automatic context:**
- Current file you're editing is automatically shared with Claude
- Current selection (highlighted code) is shared

**Manual file references:**
- Press `Ctrl+Alt+K` (Windows) or `Cmd+Option+K` (Mac)
- Insert file path into Claude Code prompt

### 11.3 Diff Viewer Integration

**When Claude suggests code changes:**
1. Claude shows changes in Android Studio's native diff viewer
2. Side-by-side comparison (old code vs new code)
3. Accept/reject changes with familiar AS controls

### 11.4 Example Workflow

**Generate WebSocket client:**
1. Press `Ctrl+Esc` to open Claude Code
2. Type prompt:
   ```
   Generate WebSocketClient.kt for VCA project that connects to
   ws://192.168.1.100:5000/audio-stream using OkHttp3
   ```
3. Claude generates code
4. Review in diff viewer
5. Accept changes
6. File created in `app/src/main/java/com/vca/assistant/websocket/`

---

## Troubleshooting

### Issue 1: "Cannot resolve symbol 'okhttp3'"

**Symptom:** Red underlines in code after adding OkHttp dependency

**Solution:**
1. Click **"File"** → **"Invalidate Caches"**
2. Check **"Invalidate and Restart"**
3. Wait for restart and re-indexing (~2-3 minutes)

### Issue 2: Gradle sync fails with "Connection timeout"

**Symptom:** Gradle cannot download dependencies

**Solution:**
```bash
# Check internet connection
# If behind proxy, configure in gradle.properties:

# File: VCAAssistant/gradle.properties
systemProp.http.proxyHost=proxy.example.com
systemProp.http.proxyPort=8080
systemProp.https.proxyHost=proxy.example.com
systemProp.https.proxyPort=8080
```

### Issue 3: WSL2 path not accessible

**Symptom:** "Path does not exist" when opening WSL2 project

**Solution:**
```bash
# From WSL2 terminal, verify WSL is running:
wsl --list --running

# If not running:
wsl

# Verify path exists:
ls -la /home/indigo/my-project3/Dappva/VCAAssistant/

# From PowerShell, test mount:
Test-Path "\\wsl$\Ubuntu\home\indigo\my-project3\Dappva\VCAAssistant"
```

### Issue 4: Device not showing in Android Studio

**Symptom:** Samsung A05 not listed in device dropdown

**Solution:**
1. Ensure USB debugging enabled on phone
2. Try different USB cable (some cables are charge-only)
3. Check device manager in Windows (should show "Android Device")
4. Install Samsung USB drivers if needed
5. Run from PowerShell:
   ```powershell
   # Check ADB can see device:
   cd C:\Users\<YourUsername>\AppData\Local\Android\Sdk\platform-tools\
   .\adb.exe devices

   # Expected output:
   # List of devices attached
   # R58RA2XXXXX    device
   ```

### Issue 5: Build fails with "JDK not found"

**Symptom:** "No JDK found" or "Unsupported Java version"

**Solution:**
1. **"File"** → **"Project Structure"**
2. Click **"SDK Location"**
3. Set **"JDK location"** to:
   ```
   C:\Program Files\Android\Android Studio\jbr
   ```
   (Android Studio's embedded JDK 17)
4. Click **"Apply"** → **"OK"**
5. Sync Gradle again

---

## File Locations Reference

### Windows Paths

**Android Studio:**
```
C:\Users\<YourUsername>\AppData\Local\JetBrains\Toolbox\apps\AndroidStudio\
```

**Android SDK:**
```
C:\Users\<YourUsername>\AppData\Local\Android\Sdk\
```

**VCA Project (via WSL2 mount):**
```
\\wsl$\Ubuntu\home\indigo\my-project3\Dappva\VCAAssistant\
```

### WSL2 Paths

**VCA Project:**
```bash
/home/indigo/my-project3/Dappva/VCAAssistant/
```

**Project Structure:**
```
VCAAssistant/
├── app/
│   ├── src/
│   │   └── main/
│   │       ├── java/com/vca/assistant/
│   │       │   └── MainActivity.kt
│   │       ├── res/
│   │       │   ├── layout/
│   │       │   │   └── activity_main.xml
│   │       │   └── values/
│   │       │       └── strings.xml
│   │       └── AndroidManifest.xml
│   └── build.gradle.kts
├── gradle/
├── build.gradle.kts
├── settings.gradle.kts
└── gradle.properties
```

---

## Next Steps

### Immediate (After Setup Complete)

1. **Verify Claude Code integration**
   - Press `Ctrl+Esc` in Android Studio
   - Test generating sample Kotlin code

2. **Review android-app-development-guide.md**
   - Contains complete VCA app architecture
   - Includes all code samples for WebSocket, audio, wake-word

3. **Start implementation**
   - Generate WebSocketClient.kt using Claude
   - Implement AudioRecorder.kt
   - Add Vosk wake-word detection

### Development Workflow

**Typical session:**
1. Open Android Studio (Windows)
2. Press `Ctrl+Esc` to open Claude Code
3. Ask Claude to generate code (e.g., "Create AudioRecorder class")
4. Review changes in diff viewer
5. Accept and build
6. Test on Samsung A05
7. Iterate with Claude for fixes/improvements

### Integration with Session Manager

**When ready to test end-to-end:**
1. Start Session Manager in WSL2:
   ```bash
   cd /home/indigo/my-project3/Dappva/session_manager
   source venv/bin/activate
   python main.py
   ```

2. Update WebSocket URL in Android app to PC's IP:
   ```kotlin
   // In VoiceAssistantService.kt:
   const val SERVER_URL = "ws://192.168.1.100:5000/audio-stream"
   ```

3. Run app on Samsung A05
4. Test wake-word → audio streaming → Session Manager

---

## Summary

✅ **You have successfully:**
- Installed Android Studio via JetBrains Toolbox
- Configured Android SDK (API 26-34)
- Created VCA Android project in WSL2 filesystem
- Configured project with required dependencies (OkHttp, Vosk, Coroutines)
- Installed Claude Code [Beta] plugin
- Set up Samsung A05 for USB debugging
- Verified end-to-end build and deployment

✅ **You can now:**
- Develop Android app with full Android Studio features
- Use Claude Code AI assistance for code generation
- Build and test on physical Samsung A05 device
- Seamlessly sync files between Windows AS and WSL2
- Integrate with Session Manager running in WSL2

**Ready for VCA Android app development!**

---

**Document Status:** Complete
**Last Updated:** 2025-11-02
**Next:** Begin Android app implementation (see android-app-development-guide.md)
