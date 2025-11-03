"""
Optimization advisor for VCA Session Manager.

Provides real-time suggestions for improving latency based on measured metrics.
Analyzes bottlenecks and recommends model switches, configuration changes, etc.

Usage:
    advisor = OptimizationAdvisor(target_latency=10.0)
    suggestions = advisor.analyze(metrics)
    for suggestion in suggestions:
        print(suggestion)
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
import logging

from .latency_tracker import LatencyMetrics

logger = logging.getLogger(__name__)


@dataclass
class OptimizationSuggestion:
    """Represents a single optimization suggestion."""

    priority: str  # "high", "medium", "low"
    component: str  # Which component (STT, LLM, TTS, etc.)
    issue: str  # Description of the issue
    suggestion: str  # Recommended action
    potential_savings: float  # Estimated time savings in seconds

    def __str__(self) -> str:
        return (f"[{self.priority.upper()}] {self.component}: {self.issue}\n"
                f"  → {self.suggestion} (save ~{self.potential_savings:.1f}s)")


class OptimizationAdvisor:
    """Analyzes latency metrics and provides optimization suggestions."""

    def __init__(self, target_latency: float = 10.0, config: Optional[Dict] = None):
        """
        Initialize optimization advisor.

        Args:
            target_latency: Target total pipeline latency in seconds
            config: Configuration dict with component targets and model specs
        """
        self.target_latency = target_latency
        self.logger = logging.getLogger(__name__)

        # Default component targets (can be overridden by config)
        self.component_targets = {
            'vad': 0.1,
            'silence_detection': 1.5,
            'stt': 4.0,
            'llm': 3.0,
            'tts': 3.0,
            'websocket': 0.5
        }

        # Model latency expectations (from GPT-5 documentation)
        self.model_latencies = {
            'gpt-5': {'min': 3.0, 'avg': 4.5, 'max': 6.0},
            'gpt-5-mini': {'min': 2.0, 'avg': 2.5, 'max': 3.5},
            'gpt-5-nano': {'min': 0.5, 'avg': 1.0, 'max': 1.5},
            'gpt-4o': {'min': 2.5, 'avg': 3.5, 'max': 4.5},
        }

        # Override with config if provided
        if config:
            if 'component_targets' in config:
                self.component_targets.update(config['component_targets'])
            if 'model_latencies' in config:
                self.model_latencies.update(config['model_latencies'])

    def analyze(self, metrics: LatencyMetrics) -> List[OptimizationSuggestion]:
        """
        Analyze metrics and generate optimization suggestions.

        Args:
            metrics: LatencyMetrics object to analyze

        Returns:
            List of OptimizationSuggestion objects, sorted by priority
        """
        suggestions = []

        # Check if we're over target
        if metrics.total_pipeline <= self.target_latency:
            self.logger.info(
                f"Performance is within target "
                f"({metrics.total_pipeline:.2f}s <= {self.target_latency:.2f}s)"
            )
            return suggestions

        # Calculate how much we're over
        overhead = metrics.total_pipeline - self.target_latency

        self.logger.warning(
            f"Latency exceeds target by {overhead:.2f}s "
            f"({metrics.total_pipeline:.2f}s > {self.target_latency:.2f}s)"
        )

        # Analyze each component
        suggestions.extend(self._analyze_llm(metrics, overhead))
        suggestions.extend(self._analyze_stt(metrics, overhead))
        suggestions.extend(self._analyze_tts(metrics, overhead))
        suggestions.extend(self._analyze_vad(metrics, overhead))

        # Sort by priority (high, medium, low) and potential savings
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        suggestions.sort(
            key=lambda s: (priority_order[s.priority], -s.potential_savings)
        )

        return suggestions

    def _analyze_llm(self, metrics: LatencyMetrics, overhead: float) -> List[OptimizationSuggestion]:
        """Analyze LLM component for optimizations."""
        suggestions = []

        current_model = metrics.llm_model_variant
        llm_time = metrics.llm_total

        # Skip if no LLM was used (echo mode)
        if current_model == "none" or llm_time == 0:
            return suggestions

        # Check if LLM is over target
        target = self.component_targets['llm']

        if llm_time > target:
            # Suggest switching to faster model
            if current_model == 'gpt-5':
                # Suggest gpt-5-mini
                expected_mini = self.model_latencies['gpt-5-mini']['avg']
                savings = llm_time - expected_mini

                suggestions.append(OptimizationSuggestion(
                    priority='high' if savings >= 1.5 else 'medium',
                    component='LLM',
                    issue=f'GPT-5 taking {llm_time:.2f}s (target: {target:.2f}s)',
                    suggestion='Switch to gpt-5-mini for balanced performance',
                    potential_savings=savings
                ))

                # Also suggest gpt-5-nano for maximum speed
                expected_nano = self.model_latencies['gpt-5-nano']['avg']
                savings_nano = llm_time - expected_nano

                suggestions.append(OptimizationSuggestion(
                    priority='high' if overhead > 3.0 else 'medium',
                    component='LLM',
                    issue=f'GPT-5 taking {llm_time:.2f}s (target: {target:.2f}s)',
                    suggestion='Switch to gpt-5-nano for maximum speed (lower quality)',
                    potential_savings=savings_nano
                ))

            elif current_model == 'gpt-5-mini':
                # Suggest gpt-5-nano
                expected_nano = self.model_latencies['gpt-5-nano']['avg']
                savings = llm_time - expected_nano

                if savings > 0.5:
                    suggestions.append(OptimizationSuggestion(
                        priority='medium',
                        component='LLM',
                        issue=f'gpt-5-mini taking {llm_time:.2f}s (target: {target:.2f}s)',
                        suggestion='Switch to gpt-5-nano for faster responses',
                        potential_savings=savings
                    ))

            # Suggest using low reasoning effort
            suggestions.append(OptimizationSuggestion(
                priority='medium',
                component='LLM',
                issue=f'LLM latency at {llm_time:.2f}s',
                suggestion='Set reasoning_effort="low" and text_verbosity="low" for faster responses',
                potential_savings=0.5  # Estimated
            ))

        return suggestions

    def _analyze_stt(self, metrics: LatencyMetrics, overhead: float) -> List[OptimizationSuggestion]:
        """Analyze STT component for optimizations."""
        suggestions = []

        stt_time = metrics.stt_total
        target = self.component_targets['stt']

        if stt_time > target:
            # Check network vs processing
            if metrics.stt_network_upload > 1.0:
                suggestions.append(OptimizationSuggestion(
                    priority='medium',
                    component='STT',
                    issue=f'Network upload taking {metrics.stt_network_upload:.2f}s',
                    suggestion='Consider audio compression or local Whisper implementation',
                    potential_savings=metrics.stt_network_upload - 0.5
                ))

            # General STT optimization
            if stt_time > 5.0:
                suggestions.append(OptimizationSuggestion(
                    priority='high' if overhead > 3.0 else 'medium',
                    component='STT',
                    issue=f'STT taking {stt_time:.2f}s (target: {target:.2f}s)',
                    suggestion='Implement local Whisper model to save 2-3 seconds',
                    potential_savings=2.5
                ))

        return suggestions

    def _analyze_tts(self, metrics: LatencyMetrics, overhead: float) -> List[OptimizationSuggestion]:
        """Analyze TTS component for optimizations."""
        suggestions = []

        tts_time = metrics.tts_total
        target = self.component_targets['tts']

        if tts_time > target:
            if tts_time > 4.0:
                suggestions.append(OptimizationSuggestion(
                    priority='medium',
                    component='TTS',
                    issue=f'TTS taking {tts_time:.2f}s (target: {target:.2f}s)',
                    suggestion='Consider local Piper TTS or enable streaming playback',
                    potential_savings=1.5
                ))
            else:
                suggestions.append(OptimizationSuggestion(
                    priority='low',
                    component='TTS',
                    issue=f'TTS taking {tts_time:.2f}s (target: {target:.2f}s)',
                    suggestion='Enable TTS response streaming to reduce perceived latency',
                    potential_savings=0.5
                ))

        return suggestions

    def _analyze_vad(self, metrics: LatencyMetrics, overhead: float) -> List[OptimizationSuggestion]:
        """Analyze VAD component for optimizations."""
        suggestions = []

        silence_time = metrics.silence_detection
        target = self.component_targets['silence_detection']

        if silence_time > target:
            savings = silence_time - 1.0  # Target 1.0s for aggressive VAD

            suggestions.append(OptimizationSuggestion(
                priority='low',  # Low priority because it affects accuracy
                component='VAD',
                issue=f'Silence detection waiting {silence_time:.2f}s',
                suggestion='Reduce VAD silence threshold to 1.0s (may reduce accuracy)',
                potential_savings=savings
            ))

        return suggestions

    def get_quick_wins(self, suggestions: List[OptimizationSuggestion]) -> List[OptimizationSuggestion]:
        """
        Filter suggestions to show only quick wins.

        Quick wins are high-priority suggestions with >1s potential savings.
        """
        return [
            s for s in suggestions
            if s.priority == 'high' and s.potential_savings >= 1.0
        ]

    def suggest_model_for_query(self, query_type: str, current_latency: float) -> str:
        """
        Suggest optimal model based on query type and current latency.

        Args:
            query_type: Type of query (e.g., "simple", "tech_support", "complex")
            current_latency: Current total pipeline latency

        Returns:
            Recommended model name
        """
        if current_latency > self.target_latency + 2.0:
            # Way over target, use fastest model
            return 'gpt-5-nano'

        if query_type == 'simple':
            return 'gpt-5-nano'
        elif query_type == 'tech_support':
            return 'gpt-5-mini'  # Balanced
        elif query_type == 'complex' or query_type == 'development':
            return 'gpt-5'  # Full reasoning

        # Default to balanced
        return 'gpt-5-mini'

    def format_suggestions(self, suggestions: List[OptimizationSuggestion]) -> str:
        """Format suggestions for display."""
        if not suggestions:
            return "✅ Performance is within target. No optimizations needed."

        output = "\n🔧 OPTIMIZATION SUGGESTIONS\n"
        output += "=" * 70 + "\n"

        for i, suggestion in enumerate(suggestions, 1):
            output += f"\n{i}. {suggestion}\n"

        total_savings = sum(s.potential_savings for s in suggestions)
        output += "\n" + "=" * 70
        output += f"\n💡 Potential total savings: ~{total_savings:.1f}s"
        output += "\n"

        return output
