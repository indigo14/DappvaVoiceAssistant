"""
Quick test script for Coqui TTS (XTTS-v2) provider
Tests speech synthesis with GTX 970 GPU and measures latency
VCA 1.0 - Session 11
"""

import asyncio
import time
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from tts.factory import TTSProviderFactory
from config.settings import get_settings


async def test_coqui_tts():
    """Test Coqui TTS provider with GTX 970 GPU"""

    print("="*70)
    print("COQUI TTS (XTTS-v2) PROVIDER TEST (GTX 970 GPU)")
    print("="*70)

    # Load settings
    settings = get_settings()

    # Create coqui_tts provider
    tts_config = {
        'model_name': settings.get('coqui_tts.model_name', 'tts_models/multilingual/multi-dataset/xtts_v2'),
        'use_gpu': settings.get('coqui_tts.use_gpu', True),
        'language': settings.get('coqui_tts.language', 'en'),
        'speed': settings.get('coqui_tts.speed', 1.0),
        'sample_rate': settings.get('coqui_tts.sample_rate', 16000),
        'reference_audio': settings.get('coqui_tts.reference_audio', None)
    }

    print(f"\n📋 Configuration:")
    for key, value in tts_config.items():
        print(f"   {key}: {value}")

    print(f"\n🔄 Initializing CoquiTTSProvider (loading ~2GB XTTS-v2 model)...")
    print("   ⏳ This may take 30-60s on first run (model download + GPU load)...")
    start_init = time.time()
    provider = TTSProviderFactory.create('coqui_tts', tts_config)
    init_time = time.time() - start_init
    print(f"✓ Provider initialized in {init_time:.2f}s")
    print(f"   {provider}")

    # Test texts (short, medium, long)
    test_texts = [
        ("Short", "Hello, this is a test."),
        ("Medium", "Hello Warren, I'm your voice assistant Nabu. How can I help you today?"),
        ("Long", "Hello Warren, I'm your voice assistant Nabu. I'm running locally on your computer using the XTTS-v2 neural text-to-speech model with GPU acceleration on your GTX 970 graphics card. This should be much faster than the cloud-based OpenAI TTS service.")
    ]

    results = []

    for label, text in test_texts:
        print(f"\n{'='*70}")
        print(f"TEST: {label} ({len(text)} characters)")
        print(f"{'='*70}")
        print(f"📝 Text: \"{text}\"")

        # Synthesize
        print(f"\n🔊 Synthesizing with XTTS-v2 (GTX 970 GPU, FP32 mode)...")
        start = time.time()
        result = await provider.synthesize(text)
        latency = time.time() - start

        # Display results
        audio_size_kb = len(result.audio_bytes) / 1024
        print(f"\n✓ Synthesis complete:")
        print(f"   Format: {result.format.upper()}")
        print(f"   Sample Rate: {result.sample_rate}Hz")
        print(f"   Audio Size: {audio_size_kb:.1f} KB")
        print(f"   Duration: {result.duration:.2f}s" if result.duration else "   Duration: N/A")
        print(f"   ⚡ Latency: {latency:.2f}s")

        if result.duration:
            realtime_factor = latency / result.duration
            chars_per_sec = len(text) / latency
            print(f"   📊 Realtime Factor: {realtime_factor:.2f}x (lower is better)")
            print(f"   📊 Speed: {chars_per_sec:.1f} chars/sec")

            if realtime_factor < 0.5:
                print(f"   💚 EXCELLENT: Much faster than realtime!")
            elif realtime_factor < 1.0:
                print(f"   ✅ GOOD: Faster than realtime")
            elif realtime_factor < 2.0:
                print(f"   ⚠️  OK: Slower than realtime but acceptable")
            else:
                print(f"   ❌ SLOW: Much slower than realtime")

        results.append({
            'label': label,
            'text': text,
            'chars': len(text),
            'latency': latency,
            'duration': result.duration,
            'realtime_factor': latency / result.duration if result.duration else None
        })

        # Save audio file for listening test
        output_path = Path(__file__).parent / f"test_output_coqui_{label.lower()}.wav"
        with open(output_path, 'wb') as f:
            f.write(result.audio_bytes)
        print(f"   💾 Saved: {output_path.name}")

    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")

    print(f"\n📊 LATENCY RESULTS:")
    for r in results:
        print(f"   {r['label']:8s}: {r['latency']:.2f}s ({r['chars']} chars, "
              f"{r['realtime_factor']:.2f}x realtime)")

    avg_latency = sum(r['latency'] for r in results) / len(results)
    avg_realtime_factor = sum(r['realtime_factor'] for r in results if r['realtime_factor']) / len(results)
    print(f"\n   Average:  {avg_latency:.2f}s ({avg_realtime_factor:.2f}x realtime)")

    # Compare to targets and baselines
    target_tts_latency = 3.0  # Current OpenAI TTS baseline
    target_local_tts = 0.5  # Target for local TTS

    print(f"\n📊 COMPARISON:")
    print(f"   OpenAI TTS (current): {target_tts_latency:.2f}s")
    print(f"   Target (local TTS): {target_local_tts:.2f}s")
    print(f"   Coqui XTTS-v2 (GPU): {avg_latency:.2f}s")
    print()

    if avg_latency < target_tts_latency:
        savings = target_tts_latency - avg_latency
        reduction_pct = (savings / target_tts_latency) * 100
        print(f"✅ IMPROVEMENT: {avg_latency:.2f}s < {target_tts_latency:.2f}s "
              f"(saved {savings:.2f}s, {reduction_pct:.1f}% reduction)")
    else:
        overage = avg_latency - target_tts_latency
        print(f"⚠️  SLOWER: {avg_latency:.2f}s > {target_tts_latency:.2f}s (increased by {overage:.2f}s)")

    if avg_latency < target_local_tts:
        print(f"✅ UNDER TARGET: {avg_latency:.2f}s < {target_local_tts:.2f}s")
    elif avg_latency < target_local_tts * 1.5:
        print(f"⚠️  NEAR TARGET: {avg_latency:.2f}s (within 50% of {target_local_tts:.2f}s target)")
    else:
        print(f"❌ OVER TARGET: {avg_latency:.2f}s > {target_local_tts:.2f}s")

    print()
    print("🎧 Listen to the generated audio files:")
    for r in results:
        print(f"   - test_output_coqui_{r['label'].lower()}.wav")
    print()


if __name__ == "__main__":
    asyncio.run(test_coqui_tts())
