package com.vca.assistant

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.material3.Button
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.ui.res.painterResource
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import com.vca.assistant.service.VoiceAssistantService
import com.vca.assistant.ui.theme.VCAAssistantTheme

class MainActivity : ComponentActivity() {
    private var displayText by mutableStateOf("Starting Voice Assistant...")
    private var serviceRunning by mutableStateOf(false)
    private var isListening by mutableStateOf(false)

    private val requestPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { permissions ->
        if (permissions.all { it.value }) {
            startVoiceService()
        } else {
            displayText = "Permissions required to run Voice Assistant"
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        setContent {
            VCAAssistantTheme {
                Scaffold(modifier = Modifier.fillMaxSize()) { innerPadding ->
                    VoiceAssistantScreen(
                        text = displayText,
                        serviceRunning = serviceRunning,
                        isListening = isListening,
                        onStartService = { checkPermissionsAndStart() },
                        onStopService = { stopVoiceService() },
                        onMicTapped = { toggleListening() },
                        modifier = Modifier.padding(innerPadding)
                    )
                }
            }
        }

        checkPermissionsAndStart()
    }

    private fun checkPermissionsAndStart() {
        val permissions = mutableListOf(
            Manifest.permission.RECORD_AUDIO,
            Manifest.permission.INTERNET
        )

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            permissions.add(Manifest.permission.POST_NOTIFICATIONS)
        }

        if (permissions.all {
                ContextCompat.checkSelfPermission(this, it) == PackageManager.PERMISSION_GRANTED
            }) {
            startVoiceService()
        } else {
            requestPermissionLauncher.launch(permissions.toTypedArray())
        }
    }

    private fun startVoiceService() {
        val intent = Intent(this, VoiceAssistantService::class.java)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            startForegroundService(intent)
        } else {
            startService(intent)
        }
        serviceRunning = true
        displayText = "Voice Assistant is running\n\nSay 'OK Nabu' or 'Hey Assistant' to activate"
    }

    private fun stopVoiceService() {
        val intent = Intent(this, VoiceAssistantService::class.java)
        stopService(intent)
        serviceRunning = false
        isListening = false
        displayText = "Voice Assistant stopped"
    }

    private fun toggleListening() {
        if (!serviceRunning) {
            checkPermissionsAndStart()
            return
        }

        if (isListening) {
            // Stop listening
            val intent = Intent(this, VoiceAssistantService::class.java).apply {
                action = "STOP_SESSION"
            }
            startService(intent)
            isListening = false
            displayText = "Tap microphone to start listening"
        } else {
            // Start listening
            val intent = Intent(this, VoiceAssistantService::class.java).apply {
                action = "START_SESSION"
            }
            startService(intent)
            isListening = true
            displayText = "Listening... Speak now!"
        }
    }
}

@Composable
fun VoiceAssistantScreen(
    text: String,
    serviceRunning: Boolean,
    isListening: Boolean,
    onStartService: () -> Unit,
    onStopService: () -> Unit,
    onMicTapped: () -> Unit,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier.fillMaxSize(),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        // Large clickable microphone icon
        Icon(
            painter = painterResource(id = R.drawable.ic_mic),
            contentDescription = "Tap to talk",
            modifier = Modifier
                .size(120.dp)
                .clickable(enabled = serviceRunning) { onMicTapped() },
            tint = if (isListening) {
                MaterialTheme.colorScheme.error // Red when actively listening
            } else if (serviceRunning) {
                MaterialTheme.colorScheme.primary // Blue when ready
            } else {
                MaterialTheme.colorScheme.onSurface.copy(alpha = 0.3f) // Gray when stopped
            }
        )

        Spacer(modifier = Modifier.height(32.dp))

        Text(
            text = text,
            style = MaterialTheme.typography.bodyLarge,
            modifier = Modifier.padding(horizontal = 32.dp)
        )

        Spacer(modifier = Modifier.height(32.dp))

        Button(
            onClick = if (serviceRunning) onStopService else onStartService,
            modifier = Modifier.padding(16.dp)
        ) {
            Text(if (serviceRunning) "Stop Voice Assistant" else "Start Voice Assistant")
        }
    }
}