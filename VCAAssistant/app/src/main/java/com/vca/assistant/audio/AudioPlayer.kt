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
