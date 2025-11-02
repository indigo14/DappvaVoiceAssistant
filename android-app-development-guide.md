# VCA Android App Development Guide
**VCA 1.0 - Custom Android App**
**Date:** 2025-11-02

## Overview

This guide covers building a custom Android app for Dad's Voice Chat Assistant (VCA), replacing the Home Assistant Companion App approach.

**App Name:** VCA Assistant
**Platform:** Android 8.0+ (API 26+)
**Language:** Kotlin
**Development Time:** 16-24 hours

---

## Prerequisites

### Development Environment

**Required:**
- Android Studio (latest stable)
- JDK 17+
- Android SDK 26+ (Oreo) to 34 (Android 14)
- Samsung A05 phone for testing (Android 15)

**Dependencies:**
- OkHttp 4.12+ (WebSocket client)
- Vosk Android SDK (wake-word detection)
- Kotlin Coroutines (async operations)
- AndroidX libraries

---

## Project Setup

### 1. Create New Android Project

**Android Studio:**
1. File → New → New Project
2. Select **Empty Activity**
3. Configure:
   - Name: `VCA Assistant`
   - Package: `com.vca.assistant`
   - Language: **Kotlin**
   - Minimum SDK: **API 26 (Android 8.0)**
   - Build config: **Kotlin DSL**

### 2. Add Dependencies

**File:** `app/build.gradle.kts`

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

### 3. Add Permissions

**File:** `app/src/main/AndroidManifest.xml`

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

        <!-- Foreground Service -->
        <service
            android:name=".service.VoiceAssistantService"
            android:enabled="true"
            android:exported="false"
            android:foregroundServiceType="microphone" />

    </application>

</manifest>
```

---

## Architecture

### App Components

```
MainActivity
    ├─ UI (status, controls)
    └─ Starts VoiceAssistantService

VoiceAssistantService (Foreground Service)
    ├─ WakeWordDetector (Vosk)
    ├─ AudioRecorder (AudioRecord)
    ├─ WebSocketClient (OkHttp)
    ├─ AudioPlayer (MediaPlayer)
    └─ SessionManager (state management)
```

---

## Implementation

### Step 1: WebSocket Client

**File:** `app/src/main/java/com/vca/assistant/websocket/WebSocketClient.kt`

```kotlin
package com.vca.assistant.websocket

import kotlinx.coroutines.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import okhttp3.*
import okio.ByteString
import java.util.concurrent.TimeUnit

class WebSocketClient(
    private val serverUrl: String,
    private val scope: CoroutineScope
) {
    private var webSocket: WebSocket? = null
    private val client = OkHttpClient.Builder()
        .pingInterval(30, TimeUnit.SECONDS)
        .build()

    private val _connectionState = MutableStateFlow(ConnectionState.DISCONNECTED)
    val connectionState: StateFlow<ConnectionState> = _connectionState

    private val _messages = MutableStateFlow<Message?>(null)
    val messages: StateFlow<Message?> = _messages

    fun connect() {
        if (_connectionState.value == ConnectionState.CONNECTED) return

        val request = Request.Builder()
            .url(serverUrl)
            .build()

        webSocket = client.newWebSocket(request, object : WebSocketListener() {
            override fun onOpen(webSocket: WebSocket, response: Response) {
                _connectionState.value = ConnectionState.CONNECTED
                sendSessionStart()
            }

            override fun onMessage(webSocket: WebSocket, text: String) {
                scope.launch {
                    _messages.emit(Message.Text(text))
                }
            }

            override fun onMessage(webSocket: WebSocket, bytes: ByteString) {
                scope.launch {
                    _messages.emit(Message.Binary(bytes.toByteArray()))
                }
            }

            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                _connectionState.value = ConnectionState.ERROR
            }

            override fun onClosed(webSocket: WebSocket, code: Int, reason: String) {
                _connectionState.value = ConnectionState.DISCONNECTED
            }
        })
    }

    fun sendAudio(audioData: ByteArray) {
        webSocket?.send(ByteString.of(*audioData))
    }

    fun sendMessage(message: String) {
        webSocket?.send(message)
    }

    private fun sendSessionStart() {
        val json = """
            {
                "type": "session_start",
                "timestamp": "${System.currentTimeMillis()}",
                "device_id": "samsung_a05_001"
            }
        """.trimIndent()
        sendMessage(json)
    }

    fun disconnect() {
        val json = """
            {
                "type": "session_end",
                "reason": "user_ended",
                "timestamp": "${System.currentTimeMillis()}"
            }
        """.trimIndent()
        sendMessage(json)

        webSocket?.close(1000, "Session ended")
        _connectionState.value = ConnectionState.DISCONNECTED
    }
}

enum class ConnectionState {
    DISCONNECTED, CONNECTING, CONNECTED, ERROR
}

sealed class Message {
    data class Text(val content: String) : Message()
    data class Binary(val data: ByteArray) : Message()
}
```

### Step 2: Audio Recorder

**File:** `app/src/main/java/com/vca/assistant/audio/AudioRecorder.kt`

```kotlin
package com.vca.assistant.audio

import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

class AudioRecorder(
    private val onAudioData: (ByteArray) -> Unit
) {
    companion object {
        const val SAMPLE_RATE = 16000 // Hz
        const val CHANNEL_CONFIG = AudioFormat.CHANNEL_IN_MONO
        const val AUDIO_FORMAT = AudioFormat.ENCODING_PCM_16BIT
        const val FRAME_DURATION_MS = 30 // milliseconds
        const val FRAME_SIZE = (SAMPLE_RATE * FRAME_DURATION_MS / 1000) * 2 // 960 bytes
    }

    private var audioRecord: AudioRecord? = null
    private var isRecording = false

    fun start() {
        if (isRecording) return

        val bufferSize = AudioRecord.getMinBufferSize(
            SAMPLE_RATE,
            CHANNEL_CONFIG,
            AUDIO_FORMAT
        )

        audioRecord = AudioRecord(
            MediaRecorder.AudioSource.VOICE_RECOGNITION,
            SAMPLE_RATE,
            CHANNEL_CONFIG,
            AUDIO_FORMAT,
            bufferSize
        )

        audioRecord?.startRecording()
        isRecording = true

        CoroutineScope(Dispatchers.IO).launch {
            val buffer = ByteArray(FRAME_SIZE)

            while (isRecording) {
                val read = audioRecord?.read(buffer, 0, buffer.size) ?: 0

                if (read > 0) {
                    onAudioData(buffer.copyOf(read))
                }
            }
        }
    }

    fun stop() {
        isRecording = false
        audioRecord?.stop()
        audioRecord?.release()
        audioRecord = null
    }
}
```

### Step 3: Wake-Word Detector (Vosk)

**File:** `app/src/main/java/com/vca/assistant/wakeword/WakeWordDetector.kt`

```kotlin
package com.vca.assistant.wakeword

import android.content.Context
import org.vosk.Model
import org.vosk.Recognizer
import java.io.File

class WakeWordDetector(
    context: Context,
    private val onWakeWordDetected: () -> Unit
) {
    private var model: Model? = null
    private var recognizer: Recognizer? = null

    companion object {
        const val SAMPLE_RATE = 16000f
        val WAKE_WORDS = listOf("nabu", "assistant", "computer")
    }

    fun initialize(modelPath: String) {
        model = Model(modelPath)
        recognizer = Recognizer(model, SAMPLE_RATE)
        recognizer?.setWords(true)
    }

    fun processAudio(audioData: ByteArray): Boolean {
        val recognizer = this.recognizer ?: return false

        if (recognizer.acceptWaveform(audioData, audioData.size)) {
            val result = recognizer.result

            // Check if wake word is in result
            WAKE_WORDS.forEach { wakeWord ->
                if (result.contains(wakeWord, ignoreCase = true)) {
                    onWakeWordDetected()
                    return true
                }
            }
        }

        return false
    }

    fun reset() {
        recognizer?.reset()
    }

    fun release() {
        recognizer?.close()
        model?.close()
    }
}
```

**Download Vosk Model:**

1. Download `vosk-model-small-en-us-0.15.zip` from https://alphacephei.com/vosk/models
2. Extract to `app/src/main/assets/vosk-model-small-en-us/`
3. Model files should be in `assets/vosk-model-small-en-us/am/`, `assets/vosk-model-small-en-us/conf/`, etc.

### Step 4: Audio Player

**File:** `app/src/main/java/com/vca/assistant/audio/AudioPlayer.kt`

```kotlin
package com.vca.assistant.audio

import android.media.MediaPlayer
import java.io.File
import java.io.FileOutputStream

class AudioPlayer {
    private var mediaPlayer: MediaPlayer? = null

    fun play(audioData: ByteArray, onComplete: () -> Unit = {}) {
        stop() // Stop any currently playing audio

        // Save audio bytes to temp file
        val tempFile = File.createTempFile("vca_audio", ".mp3")
        FileOutputStream(tempFile).use { it.write(audioData) }

        mediaPlayer = MediaPlayer().apply {
            setDataSource(tempFile.absolutePath)
            setOnCompletionListener {
                onComplete()
                tempFile.delete()
            }
            prepare()
            start()
        }
    }

    fun stop() {
        mediaPlayer?.apply {
            if (isPlaying) stop()
            release()
        }
        mediaPlayer = null
    }
}
```

### Step 5: Foreground Service

**File:** `app/src/main/java/com/vca/assistant/service/VoiceAssistantService.kt`

```kotlin
package com.vca.assistant.service

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Context
import android.content.Intent
import android.os.IBinder
import android.os.PowerManager
import androidx.core.app.NotificationCompat
import com.vca.assistant.MainActivity
import com.vca.assistant.R
import com.vca.assistant.audio.AudioPlayer
import com.vca.assistant.audio.AudioRecorder
import com.vca.assistant.wakeword.WakeWordDetector
import com.vca.assistant.websocket.ConnectionState
import com.vca.assistant.websocket.Message
import com.vca.assistant.websocket.WebSocketClient
import kotlinx.coroutines.*

class VoiceAssistantService : Service() {
    companion object {
        const val CHANNEL_ID = "vca_assistant_channel"
        const val NOTIFICATION_ID = 1
        const val SERVER_URL = "ws://192.168.1.100:5000/audio-stream" // Update with your PC IP
    }

    private lateinit var wakeWordDetector: WakeWordDetector
    private lateinit var audioRecorder: AudioRecorder
    private lateinit var webSocketClient: WebSocketClient
    private lateinit var audioPlayer: AudioPlayer
    private lateinit var wakeLock: PowerManager.WakeLock

    private val serviceScope = CoroutineScope(Dispatchers.Main + SupervisorJob())
    private var isSessionActive = false

    override fun onCreate() {
        super.onCreate()
        createNotificationChannel()

        // Initialize components
        wakeWordDetector = WakeWordDetector(this) { onWakeWordDetected() }
        audioPlayer = AudioPlayer()
        webSocketClient = WebSocketClient(SERVER_URL, serviceScope)

        audioRecorder = AudioRecorder { audioData ->
            if (isSessionActive) {
                // Send to Session Manager
                webSocketClient.sendAudio(audioData)
            } else {
                // Check for wake word
                wakeWordDetector.processAudio(audioData)
            }
        }

        // Initialize Vosk model
        val modelPath = copyModelToStorage()
        wakeWordDetector.initialize(modelPath)

        // Observe WebSocket messages
        serviceScope.launch {
            webSocketClient.messages.collect { message ->
                when (message) {
                    is Message.Binary -> {
                        // Audio response from Session Manager
                        audioPlayer.play(message.data) {
                            // Audio playback complete
                        }
                    }
                    is Message.Text -> {
                        // JSON message (transcript, status, etc.)
                        // Handle UI updates
                    }
                    null -> {}
                }
            }
        }

        // Wake lock
        val powerManager = getSystemService(Context.POWER_SERVICE) as PowerManager
        wakeLock = powerManager.newWakeLock(
            PowerManager.PARTIAL_WAKE_LOCK,
            "VCAAssistant::WakeLock"
        )
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val notification = createNotification("Listening for wake word...")
        startForeground(NOTIFICATION_ID, notification)

        // Start wake-word listening
        audioRecorder.start()

        return START_STICKY
    }

    private fun onWakeWordDetected() {
        if (isSessionActive) return

        isSessionActive = true
        wakeLock.acquire(10 * 60 * 1000L) // 10 minutes max

        // Connect to Session Manager
        webSocketClient.connect()

        // Update notification
        updateNotification("Session active - speak now...")
    }

    private fun endSession() {
        isSessionActive = false

        webSocketClient.disconnect()

        if (wakeLock.isHeld) {
            wakeLock.release()
        }

        wakeWordDetector.reset()

        updateNotification("Listening for wake word...")
    }

    private fun createNotificationChannel() {
        val channel = NotificationChannel(
            CHANNEL_ID,
            "Voice Assistant",
            NotificationManager.IMPORTANCE_LOW
        ).apply {
            description = "VCA Assistant background service"
        }

        val manager = getSystemService(NotificationManager::class.java)
        manager.createNotificationChannel(channel)
    }

    private fun createNotification(text: String): Notification {
        val intent = Intent(this, MainActivity::class.java)
        val pendingIntent = PendingIntent.getActivity(
            this, 0, intent, PendingIntent.FLAG_IMMUTABLE
        )

        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("VCA Assistant")
            .setContentText(text)
            .setSmallIcon(R.drawable.ic_mic)
            .setContentIntent(pendingIntent)
            .build()
    }

    private fun updateNotification(text: String) {
        val notification = createNotification(text)
        val manager = getSystemService(NotificationManager::class.java)
        manager.notify(NOTIFICATION_ID, notification)
    }

    private fun copyModelToStorage(): String {
        // Copy Vosk model from assets to internal storage
        val modelDir = File(filesDir, "vosk-model")
        if (!modelDir.exists()) {
            modelDir.mkdirs()
            assets.list("vosk-model-small-en-us")?.forEach { file ->
                // Copy files recursively
                // (Implementation details omitted for brevity)
            }
        }
        return modelDir.absolutePath
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onDestroy() {
        super.onDestroy()
        audioRecorder.stop()
        wakeWordDetector.release()
        webSocketClient.disconnect()
        audioPlayer.stop()
        if (wakeLock.isHeld) wakeLock.release()
        serviceScope.cancel()
    }
}
```

### Step 6: Main Activity (UI)

**File:** `app/src/main/java/com/vca/assistant/MainActivity.kt`

```kotlin
package com.vca.assistant

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.result.contract.ActivityResultContracts
import androidx.core.content.ContextCompat
import com.vca.assistant.service.VoiceAssistantService

class MainActivity : ComponentActivity() {

    private val requestPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { permissions ->
        if (permissions.all { it.value }) {
            startVoiceService()
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        checkPermissionsAndStart()
    }

    private fun checkPermissionsAndStart() {
        val permissions = arrayOf(
            Manifest.permission.RECORD_AUDIO,
            Manifest.permission.POST_NOTIFICATIONS
        )

        if (permissions.all {
                ContextCompat.checkSelfPermission(this, it) == PackageManager.PERMISSION_GRANTED
            }) {
            startVoiceService()
        } else {
            requestPermissionLauncher.launch(permissions)
        }
    }

    private fun startVoiceService() {
        val intent = Intent(this, VoiceAssistantService::class.java)
        startForegroundService(intent)
    }
}
```

---

## Configuration

### Update Server URL

**File:** `VoiceAssistantService.kt`

```kotlin
companion object {
    // IMPORTANT: Update with your PC's IP address
    const val SERVER_URL = "ws://192.168.1.100:5000/audio-stream"
}
```

**Find your PC's IP:**
```bash
# On WSL2
ip addr show eth0 | grep inet

# Or use the Windows IP (from Phase 0)
```

---

## Testing

### 1. Install on Samsung A05

**Android Studio:**
1. Connect Samsung A05 via USB
2. Enable Developer Options on phone
3. Enable USB Debugging
4. Click Run (▶) in Android Studio
5. Select Samsung A05 as target device

### 2. Test Wake-Word Detection

1. Open app → Grant permissions
2. App should show "Listening for wake word..."
3. Say **"OK Nabu"** or **"Hey Assistant"**
4. App should respond (when Session Manager is running)

### 3. Monitor Logs

**Android Studio Logcat:**
```
Filter: VCA
```

---

## Optimization

### Battery Usage

**Expected:**
- Idle (wake-word listening): 3-5% per hour
- Active session: 8-12% per hour

**Optimizations:**
- Use `PARTIAL_WAKE_LOCK` only during sessions
- Release wake lock immediately after session
- Use efficient audio buffer sizes (30ms frames)
- Minimize background processing

---

## Troubleshooting

### Wake Word Not Detecting

1. Check Vosk model is correctly installed in assets
2. Verify microphone permission granted
3. Test with louder, clearer speech
4. Check Logcat for recognition results

### WebSocket Connection Fails

1. Verify PC IP address is correct
2. Check Session Manager is running (port 5000)
3. Ensure phone and PC on same network
4. Check firewall rules on PC

### Audio Quality Issues

1. Verify sample rate is 16kHz
2. Check audio format is PCM16
3. Ensure buffer size is correct (960 bytes/30ms)
4. Test network bandwidth

---

## Next Steps

After app is working:
1. Test end-to-end with Session Manager
2. Tune wake-word sensitivity
3. Optimize battery usage
4. Add UI improvements (transcript display, status)
5. Test with Dad's voice

---

**Development Time Estimate:** 16-24 hours
**Status:** Ready to implement
**Next:** Create Android Studio project and begin development
