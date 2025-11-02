package com.vca.assistant.service

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Context
import android.content.Intent
import android.os.Environment
import android.os.IBinder
import android.os.PowerManager
import android.util.Log
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
import java.io.File

class VoiceAssistantService : Service() {
    companion object {
        const val TAG = "VCAService"
        const val CHANNEL_ID = "vca_assistant_channel"
        const val NOTIFICATION_ID = 1
        const val SERVER_URL = "ws://192.168.1.61:5000/audio-stream" // Windows host IP on home network
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

        // MUST call startForeground() within 5 seconds of service start
        // Do this BEFORE any blocking initialization
        val notification = createNotification("Starting Voice Assistant...")
        startForeground(NOTIFICATION_ID, notification)

        // Initialize components
        wakeWordDetector = WakeWordDetector(this) { onWakeWordDetected() }
        audioPlayer = AudioPlayer()
        webSocketClient = WebSocketClient(SERVER_URL, serviceScope)

        audioRecorder = AudioRecorder { audioData ->
            if (isSessionActive && webSocketClient.connectionState.value == ConnectionState.CONNECTED) {
                // Send to Session Manager only when WebSocket is connected
                webSocketClient.sendAudio(audioData)
            } else if (!isSessionActive) {
                // Check for wake word
                wakeWordDetector.processAudio(audioData)
            }
            // else: session active but not connected yet, drop audio
        }

        // Initialize Vosk model asynchronously (can take time)
        serviceScope.launch(Dispatchers.IO) {
            try {
                Log.i(TAG, "Starting Vosk model initialization...")
                val modelPath = copyModelToStorage()
                Log.i(TAG, "Model path: $modelPath")

                wakeWordDetector.initialize(modelPath)
                Log.i(TAG, "Vosk model initialized successfully!")

                // Update notification when ready
                updateNotification("Listening for wake word...")
                Log.i(TAG, "Notification updated: Listening for wake word")

                // Start audio recording
                audioRecorder.start()
                Log.i(TAG, "Audio recorder started")
            } catch (e: Exception) {
                Log.e(TAG, "Error initializing Vosk model", e)
                updateNotification("Error: ${e.message}")
                // Don't start recording if model initialization failed
            }
        }

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
        // Handle tap-to-talk actions
        when (intent?.action) {
            "START_SESSION" -> {
                Log.i(TAG, "Manual session start requested (tap-to-talk)")
                onWakeWordDetected() // Reuse existing wake-word logic
            }
            "STOP_SESSION" -> {
                Log.i(TAG, "Manual session stop requested")
                endSession()
            }
        }
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
        // Use model from phone's external storage
        // Model should be downloaded separately to /sdcard/Documents/VCA/models/
        val modelDir = File(
            Environment.getExternalStorageDirectory(),
            "Documents/VCA/models/vosk-model-small-en-us"
        )

        if (!modelDir.exists()) {
            throw IllegalStateException(
                "Vosk model not found at ${modelDir.absolutePath}. " +
                "Please download vosk-model-small-en-us-0.15.zip and extract it to this location."
            )
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
