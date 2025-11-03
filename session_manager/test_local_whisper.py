"""
Quick test script for local Whisper STT provider
Tests transcription and measures latency
"""

import asyncio
import time
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from stt.factory import STTProviderFactory
from config.settings import get_settings


async def test_local_whisper():
    """Test local Whisper provider with test audio file"""

    print("="*70)
    print("LOCAL WHISPER STT PROVIDER TEST")
    print("="*70)

    # Load settings
    settings = get_settings()

    # Create local_whisper provider
    stt_config = {
        'model_size': settings.get('local_whisper.model_size', 'small'),
        'device': settings.get('local_whisper.device', 'cpu'),
        'compute_type': settings.get('local_whisper.compute_type', 'int8'),
        'language': settings.get('local_whisper.language', 'en'),
        'beam_size': settings.get('local_whisper.beam_size', 5),
        'vad_filter': settings.get('local_whisper.vad_filter', True)
    }

    print(f"\n📋 Configuration:")
    for key, value in stt_config.items():
        print(f"   {key}: {value}")

    print(f"\n🔄 Initializing LocalWhisperProvider...")
    start_init = time.time()
    provider = STTProviderFactory.create('local_whisper', stt_config)
    init_time = time.time() - start_init
    print(f"✓ Provider initialized in {init_time:.2f}s")
    print(f"   {provider}")

    # Test with audio file
    test_audio_path = Path(__file__).parent / 'test_audio_16k.wav'

    if not test_audio_path.exists():
        print(f"\n❌ Test audio file not found: {test_audio_path}")
        print("   Please ensure test_audio_16k.wav exists")
        return

    print(f"\n🎵 Loading test audio: {test_audio_path.name}")
    with open(test_audio_path, 'rb') as f:
        audio_bytes = f.read()

    audio_size_kb = len(audio_bytes) / 1024
    print(f"   Audio size: {audio_size_kb:.1f} KB")

    # Transcribe
    print(f"\n🎙️  Transcribing...")
    start = time.time()
    result = await provider.transcribe(audio_bytes)
    latency = time.time() - start

    # Display results
    print(f"\n" + "="*70)
    print("RESULTS")
    print("="*70)
    print(f"📝 Transcription: \"{result.text}\"")
    print(f"🎯 Confidence: {result.confidence:.2f}" if result.confidence else "🎯 Confidence: N/A")
    print(f"🌍 Language: {result.language}")
    print(f"⏱️  Duration: {result.duration:.2f}s" if result.duration else "⏱️  Duration: N/A")
    print(f"⚡ Latency: {latency:.2f}s")

    if result.duration:
        realtime_factor = latency / result.duration
        print(f"📊 Realtime Factor: {realtime_factor:.2f}x (lower is better)")

        if realtime_factor < 0.5:
            print(f"   💚 EXCELLENT: Much faster than realtime!")
        elif realtime_factor < 1.0:
            print(f"   ✅ GOOD: Faster than realtime")
        elif realtime_factor < 2.0:
            print(f"   ⚠️  OK: Slower than realtime but acceptable")
        else:
            print(f"   ❌ SLOW: Much slower than realtime")

    print("="*70)

    # Compare to target
    target_stt_latency = 4.0  # From config
    if latency < target_stt_latency:
        savings = target_stt_latency - latency
        print(f"\n✅ UNDER TARGET: {latency:.2f}s < {target_stt_latency:.2f}s (saved {savings:.2f}s)")
    else:
        overage = latency - target_stt_latency
        print(f"\n⚠️  OVER TARGET: {latency:.2f}s > {target_stt_latency:.2f}s (exceeded by {overage:.2f}s)")

    print()


if __name__ == "__main__":
    asyncio.run(test_local_whisper())
