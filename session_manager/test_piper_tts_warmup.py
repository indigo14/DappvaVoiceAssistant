"""
Warmed-up latency test for Piper TTS provider
Tests cold-start vs warmed-up performance (5 iterations per test)
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


async def test_piper_tts_warmup():
    """Test Piper TTS with warmup (5 iterations per test)"""

    print("="*70)
    print("PIPER TTS WARMUP TEST (CPU-OPTIMIZED ONNX RUNTIME)")
    print("="*70)

    # Load settings
    settings = get_settings()

    # Create piper_tts provider
    tts_config = {
        'model_path': settings.get('piper_tts.model_path', 'models/piper/en_US-lessac-medium.onnx'),
        'config_path': settings.get('piper_tts.config_path', None),
        'speaker_id': settings.get('piper_tts.speaker_id', None),
        'length_scale': settings.get('piper_tts.length_scale', 1.0),
        'noise_scale': settings.get('piper_tts.noise_scale', 0.667),
        'noise_w': settings.get('piper_tts.noise_w', 0.8),
        'sample_rate': settings.get('piper_tts.sample_rate', 16000)
    }

    print(f"\n📋 Configuration:")
    for key, value in tts_config.items():
        if key == 'model_path':
            print(f"   {key}: {Path(value).name}")
        else:
            print(f"   {key}: {value}")

    print(f"\n🔄 Initializing PiperTTSProvider (loading ONNX model)...")
    start_init = time.time()
    provider = TTSProviderFactory.create('piper_tts', tts_config)
    init_time = time.time() - start_init
    print(f"✓ Provider initialized in {init_time:.2f}s")
    print(f"   {provider}")

    # Test texts (short, medium, long)
    test_texts = [
        ("Short", "Hello, this is a test."),
        ("Medium", "Hello Warren, I'm your voice assistant Nabu. How can I help you today?"),
        ("Long", "Hello Warren, I'm your voice assistant Nabu. I'm running locally on your computer using the Piper text-to-speech model with CPU-optimized ONNX Runtime. This should be much faster than both the cloud-based OpenAI TTS service and the GPU-based XTTS-v2 model.")
    ]

    ITERATIONS = 5
    all_results = []

    for label, text in test_texts:
        print(f"\n{'='*70}")
        print(f"TEST: {label} ({len(text)} characters) - {ITERATIONS} iterations")
        print(f"{'='*70}")
        print(f"📝 Text: \"{text}\"")

        iteration_results = []

        for i in range(ITERATIONS):
            print(f"\n🔊 Iteration {i+1}/{ITERATIONS}...")
            start = time.time()
            result = await provider.synthesize(text)
            latency = time.time() - start

            iteration_results.append({
                'iteration': i + 1,
                'latency': latency,
                'duration': result.duration,
                'realtime_factor': latency / result.duration if result.duration else None
            })

            print(f"   ⚡ Latency: {latency:.3f}s ({latency/result.duration:.2f}x realtime)")

        # Calculate statistics
        latencies = [r['latency'] for r in iteration_results]
        cold_start = latencies[0]
        warmed_up = latencies[1:]
        avg_warmed = sum(warmed_up) / len(warmed_up)
        min_warmed = min(warmed_up)
        max_warmed = max(warmed_up)

        print(f"\n📊 STATISTICS:")
        print(f"   Cold start (1st):      {cold_start:.3f}s")
        print(f"   Warmed up (avg 2-5):   {avg_warmed:.3f}s")
        print(f"   Best (warmed):         {min_warmed:.3f}s")
        print(f"   Worst (warmed):        {max_warmed:.3f}s")
        print(f"   Speedup after warmup:  {cold_start/avg_warmed:.2f}x faster")

        all_results.append({
            'label': label,
            'text': text,
            'chars': len(text),
            'cold_start': cold_start,
            'avg_warmed': avg_warmed,
            'min_warmed': min_warmed,
            'max_warmed': max_warmed,
            'iterations': iteration_results
        })

        # Save audio file from last iteration
        output_path = Path(__file__).parent / f"test_output_piper_warmup_{label.lower()}.wav"
        with open(output_path, 'wb') as f:
            f.write(result.audio_bytes)
        print(f"   💾 Saved: {output_path.name}")

    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY - COLD START vs WARMED UP")
    print(f"{'='*70}")

    print(f"\n📊 LATENCY COMPARISON:")
    print(f"   {'Test':<10} {'Cold Start':<15} {'Warmed Avg':<15} {'Best':<15} {'Speedup'}")
    print(f"   {'-'*70}")
    for r in all_results:
        speedup = r['cold_start'] / r['avg_warmed']
        print(f"   {r['label']:<10} {r['cold_start']:.3f}s{' ':<8} "
              f"{r['avg_warmed']:.3f}s{' ':<8} "
              f"{r['min_warmed']:.3f}s{' ':<8} "
              f"{speedup:.2f}x")

    # Overall averages
    avg_cold = sum(r['cold_start'] for r in all_results) / len(all_results)
    avg_warmed = sum(r['avg_warmed'] for r in all_results) / len(all_results)
    avg_best = sum(r['min_warmed'] for r in all_results) / len(all_results)

    print(f"\n   {'AVERAGE':<10} {avg_cold:.3f}s{' ':<8} "
          f"{avg_warmed:.3f}s{' ':<8} "
          f"{avg_best:.3f}s{' ':<8} "
          f"{avg_cold/avg_warmed:.2f}x")

    # Compare to baselines
    openai_tts = 3.0
    xtts_v2 = 9.0
    target = 0.5

    print(f"\n📊 COMPARISON TO BASELINES:")
    print(f"   OpenAI TTS (current):        {openai_tts:.2f}s")
    print(f"   XTTS-v2 (GPU):               {xtts_v2:.2f}s")
    print(f"   Target (local TTS):          {target:.2f}s")
    print(f"   Piper (cold start):          {avg_cold:.3f}s")
    print(f"   Piper (warmed up avg):       {avg_warmed:.3f}s")
    print(f"   Piper (warmed up best):      {avg_best:.3f}s")

    if avg_warmed < openai_tts:
        savings = openai_tts - avg_warmed
        reduction = (savings / openai_tts) * 100
        print(f"\n✅ WARMED UP vs OpenAI: {avg_warmed:.3f}s < {openai_tts:.2f}s "
              f"(saved {savings:.3f}s, {reduction:.1f}% reduction)")

    if avg_best < target:
        print(f"✅ BEST CASE UNDER TARGET: {avg_best:.3f}s < {target:.2f}s")
    elif avg_warmed < target * 1.5:
        print(f"⚠️  WARMED AVG NEAR TARGET: {avg_warmed:.3f}s (within 50% of {target:.2f}s)")

    # Pipeline projection with warmed-up TTS
    print(f"\n📊 PIPELINE LATENCY PROJECTION (WARMED UP):")
    print(f"   STT (PyTorch Whisper warmed): 0.71s  ⬅ From Session 10")
    print(f"   LLM (GPT-5-mini):             2.5s")
    print(f"   TTS (Piper warmed avg):       {avg_warmed:.3f}s")
    print(f"   Overhead (VAD+WS):            0.6s")
    print(f"   {'─'*40}")
    total_warmed = 0.71 + 2.5 + avg_warmed + 0.6
    print(f"   TOTAL (WARMED):               {total_warmed:.2f}s")

    target_total = 10.0
    if total_warmed < target_total:
        print(f"   ✅ Under {target_total}s target! ({target_total - total_warmed:.2f}s headroom)")

    # Best case scenario
    print(f"\n📊 PIPELINE LATENCY PROJECTION (BEST CASE):")
    print(f"   STT (PyTorch Whisper best):   0.62s  ⬅ From Session 10")
    print(f"   LLM (GPT-5-mini):             2.5s")
    print(f"   TTS (Piper best):             {avg_best:.3f}s")
    print(f"   Overhead (VAD+WS):            0.6s")
    print(f"   {'─'*40}")
    total_best = 0.62 + 2.5 + avg_best + 0.6
    print(f"   TOTAL (BEST):                 {total_best:.2f}s")

    if total_best < target_total:
        print(f"   ✅ Under {target_total}s target! ({target_total - total_best:.2f}s headroom)")

    print()


if __name__ == "__main__":
    asyncio.run(test_piper_tts_warmup())
