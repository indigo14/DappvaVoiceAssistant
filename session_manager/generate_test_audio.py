"""
Generate a test audio file using OpenAI TTS API
This creates a 16kHz mono PCM16 WAV file for testing
"""

import asyncio
import wave
from openai import AsyncOpenAI
from dotenv import load_dotenv
import os

async def generate_test_audio():
    """Generate test audio file"""

    # Load environment variables
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("Error: OPENAI_API_KEY not found in .env")
        return

    # Initialize OpenAI client
    client = AsyncOpenAI(api_key=api_key)

    # Text to synthesize
    import sys
    if len(sys.argv) > 1:
        test_text = sys.argv[1]
    else:
        test_text = "Hello, this is a test of the voice assistant. How are you today?"

    print(f"Generating audio for: '{test_text}'")
    print("Using OpenAI TTS API...")

    # Generate audio
    response = await client.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=test_text,
        response_format="pcm"  # Raw PCM format
    )

    # Save as PCM data
    pcm_data = response.content

    # Convert to WAV format (16kHz, mono, PCM16)
    output_file = "test_audio.wav"

    with wave.open(output_file, 'wb') as wf:
        wf.setnchannels(1)  # Mono
        wf.setsampwidth(2)  # 16-bit = 2 bytes
        wf.setframerate(24000)  # OpenAI returns 24kHz
        wf.writeframes(pcm_data)

    print(f"✓ Created: {output_file}")
    print(f"  Format: 16-bit PCM, Mono, 24kHz")
    print(f"  Size: {len(pcm_data)} bytes ({len(pcm_data) / (24000 * 2):.2f} seconds)")

    # Also create a 16kHz version for testing VAD
    print("\nConverting to 16kHz for VAD compatibility...")

    try:
        import numpy as np
        from scipy import signal

        # Read 24kHz audio
        with wave.open(output_file, 'rb') as wf:
            framerate = wf.getframerate()
            frames = wf.readframes(wf.getnframes())

        # Convert bytes to numpy array
        audio_data = np.frombuffer(frames, dtype=np.int16)

        # Resample to 16kHz
        num_samples = int(len(audio_data) * 16000 / framerate)
        resampled = signal.resample(audio_data, num_samples)

        # Convert back to int16
        resampled = resampled.astype(np.int16)

        # Save 16kHz version
        output_file_16k = "test_audio_16k.wav"
        with wave.open(output_file_16k, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes(resampled.tobytes())

        print(f"✓ Created: {output_file_16k}")
        print(f"  Format: 16-bit PCM, Mono, 16kHz")
        print(f"  Size: {len(resampled.tobytes())} bytes ({len(resampled) / 16000:.2f} seconds)")
        print(f"\nUse this file for testing: python test_client.py {output_file_16k}")

    except ImportError:
        print("\nNote: numpy/scipy not available for resampling")
        print(f"You can still use {output_file} but VAD expects 16kHz")


if __name__ == "__main__":
    asyncio.run(generate_test_audio())
