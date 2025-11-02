package com.vca.assistant.wakeword

import android.content.Context
import android.util.Log
import org.vosk.Model
import org.vosk.Recognizer
import java.io.File

class WakeWordDetector(
    context: Context,
    private val onWakeWordDetected: () -> Unit
) {
    private var model: Model? = null
    private var recognizer: Recognizer? = null
    private var audioChunksProcessed = 0

    companion object {
        const val TAG = "WakeWordDetector"
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

        audioChunksProcessed++
        if (audioChunksProcessed % 100 == 0) {
            Log.d(TAG, "Processed $audioChunksProcessed audio chunks")
        }

        // Feed audio to recognizer
        val isFinal = recognizer.acceptWaveForm(audioData, audioData.size)

        // Check both partial and final results
        val textToCheck = if (isFinal) {
            val result = recognizer.result
            Log.d(TAG, "Vosk final result: $result")
            result
        } else {
            val partialResult = recognizer.partialResult
            if (audioChunksProcessed % 50 == 0) {
                Log.v(TAG, "Vosk partial: $partialResult")
            }
            partialResult
        }

        // Check if wake word is in result
        WAKE_WORDS.forEach { wakeWord ->
            if (textToCheck.contains(wakeWord, ignoreCase = true)) {
                Log.i(TAG, "WAKE WORD DETECTED: $wakeWord in: $textToCheck")
                onWakeWordDetected()
                return true
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
