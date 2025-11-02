# VCA Android App - Build Commands Quick Reference

**You'll use these 3 commands instead of Android Studio's Build/Run buttons.**

---

## 📱 Setup Phone (One-Time Only)

### Enable USB Debugging on Samsung A05:
1. **Settings** → **About Phone**
2. Tap **"Build Number"** 7 times (enables Developer Mode)
3. Go back to **Settings** → **Developer Options**
4. Toggle **"USB Debugging"** ON
5. Connect phone via USB cable
6. Tap **"Allow"** when phone asks about USB debugging

### Verify Phone Connected:
```bash
adb devices
```

**Expected output:**
```
List of devices attached
R58RA2xxxxx    device
```

If you see "device" - you're ready!

---

## 🔨 Build & Install Commands

### Go to Project Directory:
```bash
cd /home/indigo/my-project3/Dappva/VCAAssistant
```

### Build the App:
```bash
./gradlew assembleDebug
```
- Takes ~1-2 minutes first time
- Creates APK: `app/build/outputs/apk/debug/app-debug.apk`
- Like clicking: Build → Build APK

### Install on Phone:
```bash
./gradlew installDebug
```
- Installs APK on connected Samsung A05
- Takes ~10-20 seconds
- Like clicking: Run ▶️ button

### Build + Install (Combined):
```bash
./gradlew installDebug
```
This builds AND installs in one command!

---

## 🔄 Development Workflow

### Typical Work Session:

1. **Edit code in Android Studio**
   - Use Claude Code (`Ctrl+Esc`) to generate modules
   - Save files (`Ctrl+S`)

2. **Build from terminal:**
   ```bash
   ./gradlew installDebug
   ```

3. **Test on Samsung A05**
   - App automatically launches after install
   - Test the new features

4. **Repeat** - edit, build, test

---

## 🧹 Useful Commands

### Clean Build (if things go wrong):
```bash
./gradlew clean
./gradlew installDebug
```

### Build Without Installing:
```bash
./gradlew assembleDebug
```

### Uninstall App from Phone:
```bash
./gradlew uninstallDebug
```

### See All Available Commands:
```bash
./gradlew tasks
```

---

## 🐛 Debugging

### View Logs from Phone:
```bash
adb logcat | grep VCA
```

### Attach Android Studio Debugger:
1. Install app: `./gradlew installDebug`
2. Launch app on phone
3. In Android Studio: **Run** → **Attach Debugger to Android Process**
4. Select `com.vca.assistant`
5. Set breakpoints, inspect variables

---

## ⚡ Quick Commands Cheat Sheet

Copy these to a text file for easy reference:

```bash
# Go to project
cd /home/indigo/my-project3/Dappva/VCAAssistant

# Build and install
./gradlew installDebug

# Clean build
./gradlew clean assembleDebug

# Check phone connected
adb devices

# View logs
adb logcat | grep VCA
```

---

## ❓ Troubleshooting

### "No devices found"
**Problem**: Phone not connected or USB debugging off

**Fix**:
1. Check USB cable connected
2. Enable USB debugging on phone
3. Tap "Allow" on phone popup
4. Run: `adb devices`

### "BUILD FAILED"
**Problem**: Compilation error in code

**Fix**:
1. Read error message (shows file and line number)
2. Fix the code error
3. Run: `./gradlew installDebug` again

### "Installation failed"
**Problem**: App already installed with different signature

**Fix**:
```bash
./gradlew uninstallDebug
./gradlew installDebug
```

---

## 🎯 First Test Build

Let's make sure everything works:

```bash
# 1. Check phone connected
adb devices

# 2. Build and install
cd /home/indigo/my-project3/Dappva/VCAAssistant
./gradlew installDebug

# 3. Expected output:
# BUILD SUCCESSFUL in 1m 23s
# App installed on Samsung A05
```

The app should launch automatically on your phone!

---

**You're all set!** These commands replace Android Studio's Build/Run buttons.
