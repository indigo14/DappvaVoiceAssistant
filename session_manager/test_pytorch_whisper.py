"""
Quick test script for PyTorch Whisper STT provider
Tests transcription with GTX 970 GPU and measures latency
"""

import asyncio
import time
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from stt.factory import STTProviderFactory
from config.settings import get_settings


async def test_pytorch_whisper():
    """Test PyTorch Whisper provider with test audio file"""

    print("="*70)
    print("PYTORCH WHISPER STT PROVIDER TEST (GTX 970 GPU)")
    print("="*70)

    # Load settings
    settings = get_settings()

    # Create pytorch_whisper provider
    stt_config = {
        'model_size': settings.get('pytorch_whisper.model_size', 'small'),
        'device': settings.get('pytorch_whisper.device', 'cuda'),
        'fp16': settings.get('pytorch_whisper.fp16', False),
        'language': settings.get('pytorch_whisper.language', 'en'),
        'temperature': settings.get('pytorch_whisper.temperature', 0.0),
        'beam_size': settings.get('pytorch_whisper.beam_size', 5),
        'initial_prompt': settings.get('pytorch_whisper.initial_prompt', None),
        'condition_on_previous_text': settings.get('pytorch_whisper.condition_on_previous_text', True)
    }

    print(f"\n📋 Configuration:")
    for key, value in stt_config.items():
        print(f"   {key}: {value}")

    print(f"\n🔄 Initializing PyTorchWhisperProvider...")
    start_init = time.time()
    provider = STTProviderFactory.create('pytorch_whisper', stt_config)
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
    print(f"\n🎙️  Transcribing with GTX 970 GPU (FP32 mode)...")
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

    # Compare to targets and baselines
    target_stt_latency = 4.0  # From config
    baseline_openai = 8.5  # OpenAI API baseline
    baseline_cpu = 4.64  # Local Whisper CPU baseline

    print(f"\n📊 COMPARISON:")
    print(f"   Target STT Latency: {target_stt_latency:.2f}s")
    print(f"   OpenAI API Baseline: {baseline_openai:.2f}s")
    print(f"   Local Whisper (CPU): {baseline_cpu:.2f}s")
    print(f"   PyTorch Whisper (GPU): {latency:.2f}s")
    print()

    if latency < target_stt_latency:
        savings = target_stt_latency - latency
        print(f"✅ UNDER TARGET: {latency:.2f}s < {target_stt_latency:.2f}s (saved {savings:.2f}s)")
    else:
        overage = latency - target_stt_latency
        print(f"⚠️  OVER TARGET: {latency:.2f}s > {target_stt_latency:.2f}s (exceeded by {overage:.2f}s)")

    vs_openai = baseline_openai - latency
    vs_cpu = baseline_cpu - latency
    print(f"\n🚀 IMPROVEMENTS:")
    print(f"   vs OpenAI API: {vs_openai:.2f}s faster ({vs_openai/baseline_openai*100:.1f}% reduction)")
    print(f"   vs CPU mode: {vs_cpu:.2f}s {'faster' if vs_cpu > 0 else 'slower'} "
          f"({abs(vs_cpu)/baseline_cpu*100:.1f}% {'improvement' if vs_cpu > 0 else 'regression'})")
    print()


if __name__ == "__main__":
    asyncio.run(test_pytorch_whisper())
