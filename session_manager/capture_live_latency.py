#!/usr/bin/env python3
"""
Live Latency Capture Script
Monitors Session Manager logs in real-time and extracts latency metrics
"""

import sys
import re
import json
from datetime import datetime

def parse_latency_breakdown(log_line):
    """Extract latency breakdown from log line"""
    # Look for the latency breakdown table
    if "Latency Breakdown:" in log_line or "Component" in log_line:
        return log_line
    return None

def parse_optimization_suggestion(log_line):
    """Extract optimization suggestions from log line"""
    if "OPTIMIZATION SUGGESTION" in log_line:
        return log_line
    return None

def parse_metrics_dict(log_line):
    """Extract metrics dictionary if sent to client"""
    if "Sending latency metrics to client:" in log_line:
        # Extract JSON from log line
        try:
            json_start = log_line.index('{')
            json_str = log_line[json_start:]
            return json.loads(json_str)
        except (ValueError, json.JSONDecodeError):
            return None
    return None

def main():
    print("=" * 80)
    print("LIVE LATENCY MONITORING - SESSION 8")
    print("=" * 80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nWaiting for requests... (Make recordings in the Android app)\n")
    print("Press Ctrl+C to stop monitoring\n")

    request_count = 0
    latency_data = []
    in_breakdown = False
    current_breakdown = []

    try:
        # Read from stdin (will be piped from tail -f)
        for line in sys.stdin:
            line = line.strip()

            # Check for new request start
            if "WebSocket connection established" in line or "Session created" in line:
                print("\n" + "─" * 80)
                print(f"🎤 NEW REQUEST DETECTED")
                print("─" * 80)

            # Check for transcript
            if "Transcript:" in line:
                print(f"📝 {line}")

            # Check for latency breakdown start
            if "Latency Breakdown:" in line:
                in_breakdown = True
                current_breakdown = [line]
                request_count += 1
                print(f"\n⏱️  REQUEST #{request_count} LATENCY BREAKDOWN:")
                continue

            # Collect breakdown lines
            if in_breakdown:
                if "───" in line or "Component" in line or "|" in line:
                    current_breakdown.append(line)
                    print(line)
                elif "OPTIMIZATION SUGGESTION" in line:
                    in_breakdown = False
                    print(f"\n💡 {line}")
                elif "Total Pipeline" in line:
                    current_breakdown.append(line)
                    print(line)
                elif len(current_breakdown) > 0 and line == "":
                    in_breakdown = False

            # Check for optimization suggestions
            if "OPTIMIZATION" in line and "SUGGESTION" in line:
                print(f"💡 {line}")

            # Check for metrics sent to client
            metrics = parse_metrics_dict(line)
            if metrics:
                latency_data.append(metrics)
                total = metrics.get('total_pipeline', 0)
                print(f"\n📊 TOTAL PIPELINE TIME: {total:.2f}s")

                # Show key components
                stt_total = metrics.get('stt_total', 0)
                tts_total = metrics.get('tts_total', 0)
                print(f"   └─ STT: {stt_total:.2f}s | TTS: {tts_total:.2f}s")

            # Check for errors
            if "ERROR" in line or "Exception" in line:
                print(f"❌ {line}")

    except KeyboardInterrupt:
        print("\n\n" + "=" * 80)
        print("MONITORING STOPPED")
        print("=" * 80)
        print(f"\nTotal requests captured: {request_count}")

        if latency_data:
            print("\n📈 SUMMARY STATISTICS:")
            print("─" * 80)

            # Calculate statistics
            total_times = [m.get('total_pipeline', 0) for m in latency_data]
            stt_times = [m.get('stt_total', 0) for m in latency_data]
            tts_times = [m.get('tts_total', 0) for m in latency_data]

            if total_times:
                print(f"Total Pipeline: min={min(total_times):.2f}s, "
                      f"max={max(total_times):.2f}s, "
                      f"avg={sum(total_times)/len(total_times):.2f}s")
            if stt_times:
                print(f"STT:           min={min(stt_times):.2f}s, "
                      f"max={max(stt_times):.2f}s, "
                      f"avg={sum(stt_times)/len(stt_times):.2f}s")
            if tts_times:
                print(f"TTS:           min={min(tts_times):.2f}s, "
                      f"max={max(tts_times):.2f}s, "
                      f"avg={sum(tts_times)/len(tts_times):.2f}s")

            # Save to file
            output_file = f"live_latency_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w') as f:
                json.dump({
                    'test_date': datetime.now().isoformat(),
                    'request_count': request_count,
                    'latency_data': latency_data,
                    'statistics': {
                        'total_pipeline': {
                            'min': min(total_times) if total_times else 0,
                            'max': max(total_times) if total_times else 0,
                            'avg': sum(total_times)/len(total_times) if total_times else 0
                        },
                        'stt': {
                            'min': min(stt_times) if stt_times else 0,
                            'max': max(stt_times) if stt_times else 0,
                            'avg': sum(stt_times)/len(stt_times) if stt_times else 0
                        },
                        'tts': {
                            'min': min(tts_times) if tts_times else 0,
                            'max': max(tts_times) if tts_times else 0,
                            'avg': sum(tts_times)/len(tts_times) if tts_times else 0
                        }
                    }
                }, f, indent=2)
            print(f"\n💾 Results saved to: {output_file}")

        sys.exit(0)

if __name__ == "__main__":
    main()
