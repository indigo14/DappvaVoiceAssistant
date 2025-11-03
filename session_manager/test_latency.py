#!/usr/bin/env python3
"""
Test script for latency monitoring system.

This script simulates audio processing latency to verify the tracking system works correctly.
"""

import time
import asyncio
from monitoring.latency_tracker import LatencyMetrics, LatencyTracker
from monitoring.optimization_advisor import OptimizationAdvisor


def simulate_audio_pipeline():
    """Simulate a complete audio processing pipeline with realistic latencies."""
    metrics = LatencyMetrics()
    metrics.session_id = "test-session-123"

    # Simulate VAD processing
    metrics.vad_processing = 0.03

    # Simulate silence detection wait
    metrics.silence_detection = 1.5

    # Simulate STT (Speech-to-Text)
    print("Simulating STT...")
    time.sleep(0.5)  # Simulate some work
    metrics.stt_network_upload = 0.2
    metrics.stt_processing = 3.1
    metrics.stt_total = 3.3

    # Simulate LLM processing
    print("Simulating LLM...")
    time.sleep(0.3)  # Simulate some work
    metrics.llm_network = 0.1
    metrics.llm_processing = 2.5
    metrics.llm_total = 2.6
    metrics.llm_model_variant = "gpt-5-mini"

    # Simulate TTS (Text-to-Speech)
    print("Simulating TTS...")
    time.sleep(0.3)  # Simulate some work
    metrics.tts_network = 0.1
    metrics.tts_processing = 2.3
    metrics.tts_total = 2.4

    # WebSocket transmission
    metrics.websocket_transmission = 0.15

    # Calculate total
    metrics.total_pipeline = (
        metrics.vad_processing +
        metrics.silence_detection +
        metrics.stt_total +
        metrics.llm_total +
        metrics.tts_total +
        metrics.websocket_transmission
    )

    metrics.transcript_length = 25
    metrics.response_length = 45

    return metrics


def test_latency_tracking():
    """Test the latency tracking system."""
    print("\n" + "="*70)
    print("TESTING LATENCY TRACKING SYSTEM")
    print("="*70)

    # Create tracker and advisor
    tracker = LatencyTracker(max_history=100)
    advisor = OptimizationAdvisor(target_latency=10.0)

    # Simulate multiple requests
    print("\nSimulating 5 audio processing requests...")
    print()

    for i in range(5):
        print(f"\n--- Request {i+1} ---")
        metrics = simulate_audio_pipeline()

        # Record metrics
        tracker.record(metrics)

        # Show summary
        print(metrics.get_summary())

        # Get optimization suggestions
        suggestions = advisor.analyze(metrics)
        if suggestions:
            print("\n" + advisor.format_suggestions(suggestions))

    # Show overall statistics
    print("\n" + "="*70)
    print("OVERALL STATISTICS")
    print("="*70)
    tracker.print_statistics()

    # Test different model latencies
    print("\n" + "="*70)
    print("TESTING DIFFERENT MODELS")
    print("="*70)

    models = ["gpt-5", "gpt-5-mini", "gpt-5-nano"]
    model_latencies = {
        "gpt-5": 4.5,
        "gpt-5-mini": 2.5,
        "gpt-5-nano": 1.0
    }

    for model in models:
        metrics = LatencyMetrics()
        metrics.session_id = f"test-{model}"
        metrics.stt_total = 3.5
        metrics.llm_total = model_latencies[model]
        metrics.llm_model_variant = model
        metrics.tts_total = 2.5
        metrics.silence_detection = 1.5
        metrics.total_pipeline = metrics.stt_total + metrics.llm_total + metrics.tts_total + metrics.silence_detection

        tracker.record(metrics)
        print(f"\n{model}: Total {metrics.total_pipeline:.2f}s (LLM: {metrics.llm_total:.2f}s)")

    # Show model comparison
    print("\n" + "="*70)
    print("MODEL COMPARISON")
    print("="*70)
    comparison = tracker.get_model_comparison()
    for model, stats in comparison.items():
        print(f"\n{model}:")
        print(f"  Mean: {stats['mean']:.2f}s")
        print(f"  Range: {stats['min']:.2f}s - {stats['max']:.2f}s")
        print(f"  Samples: {stats['sample_count']}")

    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70 + "\n")


if __name__ == "__main__":
    test_latency_tracking()
