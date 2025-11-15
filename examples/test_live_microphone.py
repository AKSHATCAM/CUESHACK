"""
Live Microphone Processing Example

This script demonstrates how to capture live audio from your microphone
and extract sound level (RMS) and frequency metrics in real-time.

The metrics are processed every second and can be fed into an LLM via MCP
to interpret the mood/vibe of the crowd.

Usage:
    python examples/test_live_microphone.py

Features demonstrated:
1. Basic microphone capture with real-time metrics
2. JSON output format (ready for MCP integration)
3. Continuous monitoring with statistics
4. CSV logging for historical analysis
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime
from collections import deque
from typing import Deque

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.sensors.live_microphone import LiveMicrophoneProcessor, LiveAudioMetrics, list_audio_devices


def example_1_basic_monitoring():
    """
    Example 1: Basic real-time monitoring with console output
    """
    print("=" * 80)
    print("EXAMPLE 1: Basic Real-time Monitoring")
    print("=" * 80)
    print("Capturing live audio and displaying metrics every second.")
    print("Press Ctrl+C to stop.\n")

    def on_metrics(metrics: LiveAudioMetrics):
        print(f"\n[{metrics.timestamp.strftime('%H:%M:%S')}]")
        print(metrics.summary())

    processor = LiveMicrophoneProcessor(
        sample_rate=22050,
        people_count=50,
        callback=on_metrics
    )

    try:
        processor.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        processor.stop()
        print("\nStopped.")


def example_2_json_output():
    """
    Example 2: JSON output format (ready for MCP/LLM integration)
    """
    print("=" * 80)
    print("EXAMPLE 2: JSON Output for MCP/LLM Integration")
    print("=" * 80)
    print("Capturing live audio and outputting structured JSON.")
    print("Press Ctrl+C to stop.\n")

    def on_metrics(metrics: LiveAudioMetrics):
        # Convert to JSON format suitable for LLM consumption
        json_output = {
            'timestamp': metrics.timestamp.isoformat(),
            'sound_level': {
                'rms_energy': round(metrics.rms_energy, 4),
                'description': get_sound_level_description(metrics.rms_energy)
            },
            'frequency': {
                'spectral_centroid_hz': round(metrics.spectral_centroid, 2),
                'description': get_frequency_description(metrics.spectral_centroid)
            },
            'quality': {
                'score': metrics.quality_score,
                'issues': get_quality_issues(metrics)
            },
            'interpretation': interpret_metrics(metrics)
        }

        print(json.dumps(json_output, indent=2))
        print()

    processor = LiveMicrophoneProcessor(
        sample_rate=22050,
        people_count=50,
        callback=on_metrics
    )

    try:
        processor.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        processor.stop()
        print("\nStopped.")


def example_3_statistics_tracking():
    """
    Example 3: Track statistics over time
    """
    print("=" * 80)
    print("EXAMPLE 3: Statistics Tracking")
    print("=" * 80)
    print("Tracking audio metrics and computing statistics.")
    print("Press Ctrl+C to stop and see summary.\n")

    # Track metrics over time
    rms_history: Deque[float] = deque(maxlen=60)  # Last 60 seconds
    frequency_history: Deque[float] = deque(maxlen=60)

    def on_metrics(metrics: LiveAudioMetrics):
        rms_history.append(metrics.rms_energy)
        frequency_history.append(metrics.spectral_centroid)

        # Print current with simple bar chart
        rms_bar = '█' * int(metrics.rms_energy * 100)
        print(f"[{metrics.timestamp.strftime('%H:%M:%S')}] "
              f"RMS: {rms_bar[:50]:<50} {metrics.rms_energy:.4f}")

    processor = LiveMicrophoneProcessor(
        sample_rate=22050,
        people_count=50,
        callback=on_metrics
    )

    try:
        processor.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        processor.stop()

        # Print statistics
        if rms_history:
            import numpy as np
            print("\n" + "=" * 80)
            print("STATISTICS SUMMARY")
            print("=" * 80)

            rms_array = np.array(list(rms_history))
            freq_array = np.array(list(frequency_history))

            print(f"\nSound Level (RMS Energy):")
            print(f"  Mean:   {np.mean(rms_array):.4f}")
            print(f"  Median: {np.median(rms_array):.4f}")
            print(f"  Std:    {np.std(rms_array):.4f}")
            print(f"  Min:    {np.min(rms_array):.4f}")
            print(f"  Max:    {np.max(rms_array):.4f}")

            print(f"\nFrequency (Spectral Centroid):")
            print(f"  Mean:   {np.mean(freq_array):.1f} Hz")
            print(f"  Median: {np.median(freq_array):.1f} Hz")
            print(f"  Std:    {np.std(freq_array):.1f} Hz")
            print(f"  Min:    {np.min(freq_array):.1f} Hz")
            print(f"  Max:    {np.max(freq_array):.1f} Hz")


def example_4_csv_logging():
    """
    Example 4: Log metrics to CSV file for later analysis
    """
    print("=" * 80)
    print("EXAMPLE 4: CSV Logging")
    print("=" * 80)
    print("Logging metrics to CSV file.")
    print("Press Ctrl+C to stop.\n")

    # Create output file
    output_file = Path(__file__).parent / f"audio_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    print(f"Logging to: {output_file}\n")

    # Write header
    with open(output_file, 'w') as f:
        f.write("timestamp,rms_energy,peak_amplitude,spectral_centroid,spectral_bandwidth,"
                "spectral_rolloff,clipping,silence_ratio,quality_score\n")

    def on_metrics(metrics: LiveAudioMetrics):
        # Log to CSV
        with open(output_file, 'a') as f:
            f.write(f"{metrics.timestamp.isoformat()},"
                    f"{metrics.rms_energy},"
                    f"{metrics.peak_amplitude},"
                    f"{metrics.spectral_centroid},"
                    f"{metrics.spectral_bandwidth},"
                    f"{metrics.spectral_rolloff},"
                    f"{int(metrics.clipping_detected)},"
                    f"{metrics.silence_ratio},"
                    f"{metrics.quality_score}\n")

        # Print status
        print(f"[{metrics.timestamp.strftime('%H:%M:%S')}] "
              f"Logged (RMS: {metrics.rms_energy:.4f}, Freq: {metrics.spectral_centroid:.1f}Hz)")

    processor = LiveMicrophoneProcessor(
        sample_rate=22050,
        people_count=50,
        callback=on_metrics
    )

    try:
        processor.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        processor.stop()
        print(f"\nStopped. Data saved to: {output_file}")


# Helper functions for interpretation

def get_sound_level_description(rms: float) -> str:
    """Convert RMS to human-readable description"""
    if rms < 0.01:
        return "very quiet / silence"
    elif rms < 0.05:
        return "quiet"
    elif rms < 0.15:
        return "moderate"
    elif rms < 0.30:
        return "loud"
    else:
        return "very loud"


def get_frequency_description(centroid: float) -> str:
    """Convert spectral centroid to description"""
    if centroid < 500:
        return "very deep / bass-heavy"
    elif centroid < 1000:
        return "deep / warm"
    elif centroid < 2000:
        return "balanced / mid-range"
    elif centroid < 4000:
        return "bright / clear"
    else:
        return "very bright / high-pitched"


def get_quality_issues(metrics: LiveAudioMetrics) -> list:
    """Extract quality issues"""
    issues = []
    if metrics.clipping_detected:
        issues.append("audio clipping detected")
    if metrics.silence_ratio > 0.8:
        issues.append("mostly silent")
    if metrics.quality_score < 70:
        issues.append("low quality signal")
    return issues if issues else ["none"]


def interpret_metrics(metrics: LiveAudioMetrics) -> str:
    """Provide high-level interpretation for LLM"""
    rms = metrics.rms_energy
    centroid = metrics.spectral_centroid

    # Energy level
    if rms > 0.2:
        energy = "high energy"
    elif rms > 0.1:
        energy = "moderate energy"
    else:
        energy = "low energy"

    # Frequency character
    if centroid > 3000:
        character = "bright, energetic sound"
    elif centroid > 1500:
        character = "balanced, clear sound"
    else:
        character = "warm, bass-heavy sound"

    # Combine
    interpretation = f"{energy}, {character}"

    # Add quality note
    if metrics.quality_score < 70:
        interpretation += " (poor quality signal)"

    return interpretation


def main():
    """Main menu"""
    print("\n" + "=" * 80)
    print("LIVE MICROPHONE PROCESSING EXAMPLES")
    print("=" * 80)

    # List audio devices
    print("\nStep 1: Audio Devices")
    print("-" * 80)
    list_audio_devices()

    print("\nStep 2: Choose Example")
    print("-" * 80)
    print("1. Basic monitoring (console output)")
    print("2. JSON output (for MCP/LLM integration)")
    print("3. Statistics tracking (with summary)")
    print("4. CSV logging (for analysis)")
    print()

    try:
        choice = input("Enter choice (1-4): ").strip()

        if choice == "1":
            example_1_basic_monitoring()
        elif choice == "2":
            example_2_json_output()
        elif choice == "3":
            example_3_statistics_tracking()
        elif choice == "4":
            example_4_csv_logging()
        else:
            print("Invalid choice")

    except KeyboardInterrupt:
        print("\nExiting...")


if __name__ == "__main__":
    main()
