"""
Simple WebSocket test client for Session Manager
Tests audio streaming without wake-word
"""

import asyncio
import json
import wave
import sys
from pathlib import Path
import websockets

async def test_session_manager(audio_file_path: str):
    """
    Test the Session Manager with an audio file.

    Args:
        audio_file_path: Path to WAV file (16kHz, mono, PCM16)
    """
    uri = "ws://localhost:5000/audio-stream"

    print(f"Connecting to {uri}...")

    async with websockets.connect(uri) as websocket:
        print("Connected!")

        # Send session_start message
        session_start_msg = {
            "type": "session_start",
            "device_id": "test_client"
        }
        await websocket.send(json.dumps(session_start_msg))
        print(f"Sent: {session_start_msg}")

        # Wait for session_started response
        response = await websocket.recv()
        print(f"Received: {response}")

        # Read audio file
        print(f"\nReading audio file: {audio_file_path}")
        with wave.open(audio_file_path, 'rb') as wf:
            # Verify format
            channels = wf.getnchannels()
            sample_width = wf.getsampwidth()
            framerate = wf.getframerate()

            print(f"Audio format: {channels} channel(s), {sample_width} bytes/sample, {framerate} Hz")

            if framerate != 16000:
                print(f"WARNING: Expected 16kHz, got {framerate} Hz")
            if channels != 1:
                print(f"WARNING: Expected mono, got {channels} channels")
            if sample_width != 2:
                print(f"WARNING: Expected PCM16 (2 bytes), got {sample_width} bytes")

            # Calculate frame size for 30ms chunks (960 bytes @ 16kHz PCM16)
            frame_size = int(16000 * 0.030 * 2)  # 960 bytes
            print(f"Sending audio in {frame_size}-byte chunks (30ms frames)...\n")

            # Stream audio in 30ms chunks
            chunk_num = 0
            while True:
                audio_chunk = wf.readframes(int(16000 * 0.030))  # 30ms of audio
                if len(audio_chunk) == 0:
                    break

                # Send audio chunk
                await websocket.send(audio_chunk)
                chunk_num += 1

                # Small delay to simulate real-time streaming
                await asyncio.sleep(0.030)  # 30ms

            print(f"Sent {chunk_num} audio chunks ({chunk_num * 30}ms total)")

        # Send 2.5 seconds of silence to trigger end-of-speech detection
        print("Sending 2.5 seconds of silence to trigger VAD...")
        silence_frames = int(2.5 / 0.030)  # Number of 30ms frames in 2.5 seconds
        silence_chunk = b'\x00' * frame_size  # Silent audio (all zeros)

        for i in range(silence_frames):
            await websocket.send(silence_chunk)
            await asyncio.sleep(0.030)

        print(f"Sent {silence_frames} silence frames")

        # Wait for transcript and response
        print("\nWaiting for responses...")
        timeout_seconds = 30

        try:
            while True:
                response = await asyncio.wait_for(websocket.recv(), timeout=timeout_seconds)

                # Check if binary (audio response) or text (JSON)
                if isinstance(response, bytes):
                    print(f"\n[AUDIO RESPONSE] Received {len(response)} bytes")

                    # Save audio response to file
                    output_file = "test_response.mp3"
                    with open(output_file, "wb") as f:
                        f.write(response)
                    print(f"Saved to: {output_file}")

                else:
                    # JSON message
                    msg = json.loads(response)
                    msg_type = msg.get("type")

                    if msg_type == "transcript":
                        print(f"\n[TRANSCRIPT] {msg.get('text')}")

                    elif msg_type == "response_text":
                        print(f"[RESPONSE] {msg.get('text')}")

                    elif msg_type == "status":
                        state = msg.get("state")
                        print(f"[STATUS] {state}")

                        # If back to listening, we're done
                        if state == "listening":
                            print("\nSession back to listening state. Test complete!")
                            break

                    elif msg_type == "session_ending":
                        reason = msg.get("reason")
                        matched = msg.get("matched_phrase", "")
                        print(f"\n[SESSION ENDING] Reason: {reason}, Matched: '{matched}'")
                        break

                    elif msg_type == "error":
                        print(f"\n[ERROR] {msg.get('message')}")
                        break

                    else:
                        print(f"[{msg_type.upper()}] {msg}")

        except asyncio.TimeoutError:
            print(f"\nTimeout after {timeout_seconds} seconds")

        # Send session_end message
        session_end_msg = {
            "type": "session_end",
            "reason": "test_complete"
        }
        await websocket.send(json.dumps(session_end_msg))
        print(f"\nSent: {session_end_msg}")
        print("Connection closed.")


async def test_simple_connection():
    """Test simple connection without audio"""
    uri = "ws://localhost:5000/audio-stream"

    print(f"Testing simple connection to {uri}...")

    try:
        async with websockets.connect(uri) as websocket:
            print("✓ WebSocket connection successful!")

            # Send session_start
            await websocket.send(json.dumps({
                "type": "session_start",
                "device_id": "test"
            }))

            # Wait for response
            response = await asyncio.wait_for(websocket.recv(), timeout=5)
            print(f"✓ Received: {response}")

            # Send session_end
            await websocket.send(json.dumps({
                "type": "session_end",
                "reason": "test"
            }))

            print("✓ Connection test passed!")
            return True

    except Exception as e:
        print(f"✗ Connection test failed: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python test_client.py test              - Test connection only")
        print("  python test_client.py <audio_file.wav>  - Test with audio file")
        print("\nAudio file requirements:")
        print("  - Format: WAV")
        print("  - Sample rate: 16kHz")
        print("  - Channels: Mono (1 channel)")
        print("  - Bit depth: 16-bit PCM (PCM16)")
        sys.exit(1)

    arg = sys.argv[1]

    if arg == "test":
        # Simple connection test
        asyncio.run(test_simple_connection())
    else:
        # Full audio test
        audio_file = Path(arg)

        if not audio_file.exists():
            print(f"Error: Audio file not found: {audio_file}")
            sys.exit(1)

        asyncio.run(test_session_manager(str(audio_file)))
