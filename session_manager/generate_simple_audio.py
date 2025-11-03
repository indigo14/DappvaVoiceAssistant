#!/usr/bin/env python3
"""
Generate a simple test audio file for latency testing.
Creates a pure tone for a few seconds - won't trigger stop phrases.
"""

import wave
import numpy as np

# Parameters
duration = 2.0  # seconds
sample_rate = 16000
frequency = 440  # A4 note

# Generate tone
t = np.linspace(0, duration, int(sample_rate * duration))
audio = (np.sin(2 * np.pi * frequency * t) * 32767 * 0.3).astype(np.int16)

# Write WAV file
with wave.open('test_tone.wav', 'wb') as wf:
    wf.setnchannels(1)  # Mono
    wf.setsampwidth(2)  # 16-bit
    wf.setframerate(sample_rate)
    wf.writeframes(audio.tobytes())

print(f"Generated test_tone.wav: {duration}s, {sample_rate}Hz, mono")
print("This will transcribe as something unintelligible, avoiding stop phrases")
