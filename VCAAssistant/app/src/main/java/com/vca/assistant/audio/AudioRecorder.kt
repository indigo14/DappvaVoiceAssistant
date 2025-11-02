package com.vca.assistant.audio

import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
import android.util.Log
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

class AudioRecorder(
    private val onAudioData: (ByteArray) -> Unit
) {
    companion object {
        const val TAG = "AudioRecorder"
        const val SAMPLE_RATE = 16000 // Hz
        const val CHANNEL_CONFIG = AudioFormat.CHANNEL_IN_MONO
        const val AUDIO_FORMAT = AudioFormat.ENCODING_PCM_16BIT
        const val FRAME_DURATION_MS = 30 // milliseconds
        const val FRAME_SIZE = (SAMPLE_RATE * FRAME_DURATION_MS / 1000) * 2 // 960 bytes
    }

    private var audioRecord: AudioRecord? = null
    private var isRecording = false
    private var totalBytesRead = 0L

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

        Log.i(TAG, "Starting audio recording - FRAME_SIZE: $FRAME_SIZE bytes, SAMPLE_RATE: $SAMPLE_RATE Hz")

        CoroutineScope(Dispatchers.IO).launch {
            val buffer = ByteArray(FRAME_SIZE)
            var chunksRead = 0

            while (isRecording) {
                val read = audioRecord?.read(buffer, 0, buffer.size) ?: 0

                if (read > 0) {
                    totalBytesRead += read
                    chunksRead++

                    if (chunksRead % 100 == 0) {
                        Log.d(TAG, "Audio chunks read: $chunksRead, total bytes: $totalBytesRead, last chunk: $read bytes")
                    }

                    onAudioData(buffer.copyOf(read))
                } else if (read < 0) {
                    Log.e(TAG, "AudioRecord.read() error: $read")
                }
            }

            Log.i(TAG, "Audio recording stopped. Total chunks: $chunksRead, total bytes: $totalBytesRead")
        }
    }

    fun stop() {
        isRecording = false
        audioRecord?.stop()
        audioRecord?.release()
        audioRecord = null
    }
}
