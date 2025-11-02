package com.vca.assistant.websocket

import android.util.Log
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
    companion object {
        private const val TAG = "WebSocketClient"
    }
    private var webSocket: WebSocket? = null
    private val client = OkHttpClient.Builder()
        .pingInterval(30, TimeUnit.SECONDS)
        .build()

    private val _connectionState = MutableStateFlow(ConnectionState.DISCONNECTED)
    val connectionState: StateFlow<ConnectionState> = _connectionState

    private val _messages = MutableStateFlow<Message?>(null)
    val messages: StateFlow<Message?> = _messages

    fun connect() {
        if (_connectionState.value == ConnectionState.CONNECTED) {
            Log.i(TAG, "Already connected, skipping")
            return
        }

        Log.i(TAG, "Connecting to WebSocket: $serverUrl")
        _connectionState.value = ConnectionState.CONNECTING

        val request = Request.Builder()
            .url(serverUrl)
            .build()

        webSocket = client.newWebSocket(request, object : WebSocketListener() {
            override fun onOpen(webSocket: WebSocket, response: Response) {
                Log.i(TAG, "WebSocket connected successfully!")
                _connectionState.value = ConnectionState.CONNECTED
                // Send session_start immediately
                scope.launch {
                    sendSessionStart()
                }
            }

            override fun onMessage(webSocket: WebSocket, text: String) {
                Log.d(TAG, "Received text message: $text")
                scope.launch {
                    _messages.emit(Message.Text(text))
                }
            }

            override fun onMessage(webSocket: WebSocket, bytes: ByteString) {
                Log.d(TAG, "Received binary message: ${bytes.size} bytes")
                scope.launch {
                    _messages.emit(Message.Binary(bytes.toByteArray()))
                }
            }

            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                Log.e(TAG, "WebSocket connection failed: ${t.message}", t)
                Log.e(TAG, "Response: ${response?.code} - ${response?.message}")
                _connectionState.value = ConnectionState.ERROR
            }

            override fun onClosed(webSocket: WebSocket, code: Int, reason: String) {
                Log.i(TAG, "WebSocket closed: code=$code, reason=$reason")
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
        Log.i(TAG, "Sending session_start: $json")
        sendMessage(json)
    }

    fun disconnect() {
        Log.i(TAG, "Disconnecting WebSocket")
        val json = """
            {
                "type": "session_end",
                "reason": "user_ended",
                "timestamp": "${System.currentTimeMillis()}"
            }
        """.trimIndent()
        Log.i(TAG, "Sending session_end: $json")
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
