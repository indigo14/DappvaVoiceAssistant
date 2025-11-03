"""
Latency tracking and measurement for VCA Session Manager.

Provides detailed timing for each component of the audio processing pipeline:
- VAD (Voice Activity Detection)
- Silence Detection
- STT (Speech-to-Text)
- LLM (Language Model)
- TTS (Text-to-Speech)
- Network transmission

Usage:
    metrics = LatencyMetrics()

    start = time.time()
    # ... do STT processing ...
    metrics.stt_processing = time.time() - start

    print(metrics.get_breakdown())
"""

import time
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class LatencyMetrics:
    """Tracks latency for each component of the audio pipeline."""

    # Timing for each component (in seconds)
    vad_processing: float = 0.0
    silence_detection: float = 0.0  # Time waiting for silence
    stt_network_upload: float = 0.0
    stt_processing: float = 0.0
    stt_total: float = 0.0
    llm_network: float = 0.0
    llm_processing: float = 0.0
    llm_total: float = 0.0
    llm_model_variant: str = "none"
    tts_network: float = 0.0
    tts_processing: float = 0.0
    tts_total: float = 0.0
    websocket_transmission: float = 0.0
    total_pipeline: float = 0.0

    # Provider tracking (NEW - for experimentation)
    stt_provider: str = "unknown"
    tts_provider: str = "unknown"

    # Metadata
    timestamp: float = field(default_factory=time.time)
    session_id: str = ""
    transcript_length: int = 0
    response_length: int = 0

    def get_breakdown(self) -> str:
        """Return formatted breakdown for logging."""
        return f"""
╔══════════════════════════════════════════════════════════════╗
║               LATENCY BREAKDOWN - Session {self.session_id[:8]}
╠══════════════════════════════════════════════════════════════╣
║ VAD Processing:           {self.vad_processing:>6.3f}s
║ Silence Detection:        {self.silence_detection:>6.3f}s (waiting)
║ ───────────────────────────────────────────────────────────
║ STT Provider: {self.stt_provider:<15}
║ STT Network Upload:       {self.stt_network_upload:>6.3f}s
║ STT Processing:           {self.stt_processing:>6.3f}s
║ STT TOTAL:                {self.stt_total:>6.3f}s
║ ───────────────────────────────────────────────────────────
║ LLM Network:              {self.llm_network:>6.3f}s
║ LLM Processing ({self.llm_model_variant:>10}): {self.llm_processing:>6.3f}s
║ LLM TOTAL:                {self.llm_total:>6.3f}s
║ ───────────────────────────────────────────────────────────
║ TTS Provider: {self.tts_provider:<15}
║ TTS Network:              {self.tts_network:>6.3f}s
║ TTS Processing:           {self.tts_processing:>6.3f}s
║ TTS TOTAL:                {self.tts_total:>6.3f}s
║ ───────────────────────────────────────────────────────────
║ WebSocket Transmission:   {self.websocket_transmission:>6.3f}s
╠══════════════════════════════════════════════════════════════╣
║ TOTAL PIPELINE:           {self.total_pipeline:>6.3f}s
╚══════════════════════════════════════════════════════════════╝
        """

    def get_summary(self) -> str:
        """Return concise one-line summary."""
        return (f"Total: {self.total_pipeline:.2f}s "
                f"(STT: {self.stt_total:.2f}s, "
                f"LLM: {self.llm_total:.2f}s [{self.llm_model_variant}], "
                f"TTS: {self.tts_total:.2f}s)")

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    def is_over_target(self, target: float) -> bool:
        """Check if total latency exceeds target."""
        return self.total_pipeline > target

    def get_slowest_component(self) -> str:
        """Identify the slowest component."""
        components = {
            'VAD': self.vad_processing,
            'Silence Detection': self.silence_detection,
            'STT': self.stt_total,
            'LLM': self.llm_total,
            'TTS': self.tts_total,
            'WebSocket': self.websocket_transmission
        }
        return max(components, key=components.get)


class LatencyTracker:
    """Tracks and analyzes latency metrics over time."""

    def __init__(self, max_history: int = 1000):
        """
        Initialize latency tracker.

        Args:
            max_history: Maximum number of metrics to keep in history
        """
        self.history: List[LatencyMetrics] = []
        self.max_history = max_history
        self.logger = logging.getLogger(__name__)

    def record(self, metrics: LatencyMetrics) -> None:
        """
        Record a latency measurement.

        Args:
            metrics: LatencyMetrics object to record
        """
        self.history.append(metrics)

        # Trim history if needed
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]

        # Log the measurement
        self.logger.info(f"Latency recorded: {metrics.get_summary()}")

    def get_recent(self, count: int = 10) -> List[LatencyMetrics]:
        """Get the most recent N metrics."""
        return self.history[-count:]

    def get_statistics(self) -> Dict:
        """
        Calculate statistics across all recorded metrics.

        Returns:
            Dictionary with mean, median, p50, p90, p99 for each component
        """
        if not self.history:
            return {}

        import numpy as np

        totals = [m.total_pipeline for m in self.history]
        stt_times = [m.stt_total for m in self.history]
        llm_times = [m.llm_total for m in self.history]
        tts_times = [m.tts_total for m in self.history]

        return {
            'total': {
                'mean': float(np.mean(totals)),
                'median': float(np.median(totals)),
                'p50': float(np.percentile(totals, 50)),
                'p90': float(np.percentile(totals, 90)),
                'p99': float(np.percentile(totals, 99)),
                'min': float(np.min(totals)),
                'max': float(np.max(totals)),
            },
            'stt': {
                'mean': float(np.mean(stt_times)),
                'p90': float(np.percentile(stt_times, 90)),
            },
            'llm': {
                'mean': float(np.mean(llm_times)),
                'p90': float(np.percentile(llm_times, 90)),
            },
            'tts': {
                'mean': float(np.mean(tts_times)),
                'p90': float(np.percentile(tts_times, 90)),
            },
            'sample_count': len(self.history)
        }

    def get_bottlenecks(self, threshold_multiplier: float = 1.5) -> List[str]:
        """
        Identify consistent bottlenecks in the pipeline.

        Args:
            threshold_multiplier: Components taking > mean * this value are flagged

        Returns:
            List of bottleneck descriptions
        """
        if len(self.history) < 5:
            return ["Not enough data to identify bottlenecks"]

        import numpy as np

        recent = self.history[-100:]  # Last 100 requests

        avg_stt = np.mean([m.stt_total for m in recent])
        avg_llm = np.mean([m.llm_total for m in recent])
        avg_tts = np.mean([m.tts_total for m in recent])
        avg_total = np.mean([m.total_pipeline for m in recent])

        bottlenecks = []

        # Define expected targets (configurable)
        targets = {
            'STT': 4.0,
            'LLM': 3.0,
            'TTS': 3.0,
            'Total': 10.0
        }

        if avg_stt > targets['STT']:
            bottlenecks.append(
                f"STT averaging {avg_stt:.1f}s (target: {targets['STT']:.1f}s) "
                f"- Consider local Whisper implementation"
            )

        if avg_llm > targets['LLM']:
            bottlenecks.append(
                f"LLM averaging {avg_llm:.1f}s (target: {targets['LLM']:.1f}s) "
                f"- Consider switching to faster model variant"
            )

        if avg_tts > targets['TTS']:
            bottlenecks.append(
                f"TTS averaging {avg_tts:.1f}s (target: {targets['TTS']:.1f}s) "
                f"- Consider local TTS or streaming"
            )

        if avg_total > targets['Total']:
            bottlenecks.append(
                f"Total pipeline averaging {avg_total:.1f}s (target: {targets['Total']:.1f}s)"
            )

        if not bottlenecks:
            bottlenecks.append(f"Performance is within targets (avg: {avg_total:.1f}s)")

        return bottlenecks

    def get_model_comparison(self) -> Dict[str, Dict]:
        """
        Compare latencies across different LLM models used.

        Returns:
            Dictionary mapping model names to their statistics
        """
        if not self.history:
            return {}

        import numpy as np
        from collections import defaultdict

        model_times = defaultdict(list)

        for metrics in self.history:
            if metrics.llm_model_variant and metrics.llm_model_variant != "none":
                model_times[metrics.llm_model_variant].append(metrics.llm_total)

        comparison = {}
        for model, times in model_times.items():
            if times:
                comparison[model] = {
                    'mean': float(np.mean(times)),
                    'median': float(np.median(times)),
                    'min': float(np.min(times)),
                    'max': float(np.max(times)),
                    'sample_count': len(times)
                }

        return comparison

    def print_statistics(self) -> None:
        """Print formatted statistics to console."""
        stats = self.get_statistics()

        if not stats:
            print("No latency data recorded yet.")
            return

        print("\n" + "="*70)
        print("LATENCY STATISTICS")
        print("="*70)
        print(f"Sample count: {stats['sample_count']}")
        print("\nTotal Pipeline Latency:")
        print(f"  Mean:   {stats['total']['mean']:.2f}s")
        print(f"  Median: {stats['total']['median']:.2f}s")
        print(f"  P90:    {stats['total']['p90']:.2f}s")
        print(f"  P99:    {stats['total']['p99']:.2f}s")
        print(f"  Range:  {stats['total']['min']:.2f}s - {stats['total']['max']:.2f}s")

        print("\nComponent Averages:")
        print(f"  STT: {stats['stt']['mean']:.2f}s (P90: {stats['stt']['p90']:.2f}s)")
        print(f"  LLM: {stats['llm']['mean']:.2f}s (P90: {stats['llm']['p90']:.2f}s)")
        print(f"  TTS: {stats['tts']['mean']:.2f}s (P90: {stats['tts']['p90']:.2f}s)")

        print("\nBottlenecks:")
        for bottleneck in self.get_bottlenecks():
            print(f"  • {bottleneck}")

        # Model comparison if available
        model_comparison = self.get_model_comparison()
        if model_comparison:
            print("\nModel Comparison:")
            for model, stats in model_comparison.items():
                print(f"  {model}:")
                print(f"    Mean: {stats['mean']:.2f}s (n={stats['sample_count']})")
                print(f"    Range: {stats['min']:.2f}s - {stats['max']:.2f}s")

        print("="*70 + "\n")
