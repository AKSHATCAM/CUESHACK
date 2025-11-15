#!/usr/bin/env python3
"""
Test script for real-time audio clip analysis
Demonstrates the audio preprocessing pipeline for MCP
"""

import asyncio
import json
import numpy as np
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.sensors.audio_clip_processor import AudioClipProcessor, AudioClipBuffer
from src.mcp_server.tools import analyze_audio_clip, get_audio_acceptability_check
from src.sensors.mock import MockCrowdSimulator


async def test_basic_audio_processing():
    """Test basic audio clip processing"""
    print("=" * 80)
    print("TEST 1: Basic Audio Clip Processing")
    print("=" * 80)

    processor = AudioClipProcessor(sample_rate=22050)

    # Generate a 1-second test audio clip
    sample_rate = 22050
    duration = 1.0
    t = np.linspace(0, duration, int(sample_rate * duration))

    # Create a simple sine wave (440 Hz - A note)
    audio = 0.5 * np.sin(2 * np.pi * 440 * t)

    # Process with 10 people in the system
    people_count = 10
    metrics = processor.process_clip(audio, people_count)

    print(f"\nProcessed 1-second audio clip")
    print(f"People count: {people_count}")
    print(f"RMS Energy: {metrics.rms_energy:.4f}")
    print(f"Peak Amplitude: {metrics.peak_amplitude:.4f}")
    print(f"Spectral Centroid: {metrics.spectral_centroid:.2f} Hz")
    print(f"Harmonic Ratio: {metrics.harmonic_ratio:.2f}")
    print(f"Percussive Ratio: {metrics.percussive_ratio:.2f}")
    print(f"Energy per Person: {metrics.energy_per_person:.6f}")
    print(f"Clipping Detected: {metrics.clipping_detected}")

    # Convert to dict for JSON serialization
    result_dict = processor.metrics_to_dict(metrics)
    print("\nAcceptability Indicators:")
    print(json.dumps(result_dict["acceptability_indicators"], indent=2))


async def test_mcp_audio_tool():
    """Test the MCP audio analysis tool"""
    print("\n" + "=" * 80)
    print("TEST 2: MCP Audio Analysis Tool (with mock data)")
    print("=" * 80)

    # This simulates what the LLM would receive via MCP
    result = await analyze_audio_clip(use_mock_data=True)

    print("\nAudio Analysis Result:")
    print(f"Timestamp: {result['timestamp']}")
    print(f"\nAmplitude Metrics:")
    print(f"  RMS Energy: {result['amplitude']['rms_energy']:.4f}")
    print(f"  Peak Amplitude: {result['amplitude']['peak_amplitude']:.4f}")
    print(f"  Dynamic Range: {result['amplitude']['dynamic_range_db']:.2f} dB")

    print(f"\nFrequency Metrics:")
    print(f"  Spectral Centroid: {result['frequency']['spectral_centroid_hz']:.2f} Hz")
    print(f"  Spectral Bandwidth: {result['frequency']['spectral_bandwidth_hz']:.2f} Hz")
    print(f"  Zero Crossing Rate: {result['frequency']['zero_crossing_rate']:.4f}")

    print(f"\nRhythm Metrics:")
    print(f"  Estimated Tempo: {result['rhythm']['estimated_tempo_bpm']} BPM")
    print(f"  Beat Strength: {result['rhythm']['beat_strength']:.4f}")

    print(f"\nQuality Indicators:")
    print(f"  Clipping: {result['quality']['clipping_detected']}")
    print(f"  Silence Ratio: {result['quality']['silence_ratio']:.2%}")
    print(f"  Noise Floor: {result['quality']['noise_floor']:.4f}")

    print(f"\nContent Analysis:")
    print(f"  Harmonic Ratio: {result['content']['harmonic_ratio']:.2f}")
    print(f"  Percussive Ratio: {result['content']['percussive_ratio']:.2f}")

    print(f"\nContext:")
    print(f"  People Count: {result['context']['people_count']}")
    print(f"  Energy per Person: {result['context']['energy_per_person']:.6f}")

    print(f"\nCrowd Context:")
    print(f"  Crowd Energy Level: {result['crowd_context']['energy_level']}/100")
    print(f"  Dominant Mood: {result['crowd_context']['dominant_mood']}")
    print(f"  Noise: {result['crowd_context']['noise_db']} dB")
    print(f"  Movement Intensity: {result['crowd_context']['movement_intensity']}/100")

    print(f"\nCorrelation Analysis:")
    print(f"  Energy Correlation: {result['correlation_analysis']['energy_correlation']}")
    print(f"  Beat-Movement Sync: {result['correlation_analysis']['beat_movement_sync']}")
    print(f"  Mood-Music Alignment: {result['correlation_analysis']['mood_music_alignment']}")
    print(f"  Overall Match: {result['correlation_analysis']['overall_match']}")
    print(f"\n  Observations:")
    for obs in result['correlation_analysis']['observations']:
        print(f"    - {obs}")

    print(f"\nAcceptability Indicators:")
    acc = result['acceptability_indicators']
    print(f"  Acceptable: {acc['acceptable']}")
    print(f"  Quality Score: {acc['quality_score']}/100")
    print(f"  Recommendation: {acc['recommendation']}")
    if acc['issues']:
        print(f"  Issues:")
        for issue in acc['issues']:
            print(f"    - {issue}")
    if acc['warnings']:
        print(f"  Warnings:")
        for warning in acc['warnings']:
            print(f"    - {warning}")


async def test_acceptability_check():
    """Test the LLM-ready acceptability check"""
    print("\n" + "=" * 80)
    print("TEST 3: LLM-Ready Acceptability Check")
    print("=" * 80)

    result = await get_audio_acceptability_check()

    print("\nDecision Framework (What the LLM sees):")
    df = result['decision_framework']
    print(f"  Is Acceptable: {df['is_acceptable']}")
    print(f"  Quality Score: {df['quality_score']}/100")
    print(f"  Crowd Match: {df['crowd_match']}")
    print(f"  Recommendation: {df['recommendation']}")

    if df['critical_issues']:
        print(f"\n  Critical Issues:")
        for issue in df['critical_issues']:
            print(f"    ❌ {issue}")

    if df['warnings']:
        print(f"\n  Warnings:")
        for warning in df['warnings']:
            print(f"    ⚠️  {warning}")

    print("\nLLM Guidance:")
    guidance = result['llm_guidance']
    print(f"  Should Keep Playing: {guidance['should_keep_playing']}")
    print(f"\n  Suggested Actions:")
    for action in guidance['suggested_actions']:
        print(f"    → {action}")

    print(f"\n  Reasoning Points:")
    for point in guidance['reasoning_points']:
        print(f"    • {point}")


async def test_realtime_buffer():
    """Test real-time buffering simulation"""
    print("\n" + "=" * 80)
    print("TEST 4: Real-time Audio Buffer Simulation")
    print("=" * 80)

    buffer = AudioClipBuffer(sample_rate=22050)
    simulator = MockCrowdSimulator()

    print("\nSimulating 5 seconds of real-time audio...")
    print("Processing 1-second clips every second:\n")

    chunk_size = 2048  # Simulate incoming audio chunks
    sample_rate = 22050

    for second in range(5):
        # Simulate receiving audio chunks for 1 second
        chunks_per_second = sample_rate // chunk_size

        for i in range(chunks_per_second):
            # Generate audio chunk
            t = np.linspace(
                i * chunk_size / sample_rate,
                (i + 1) * chunk_size / sample_rate,
                chunk_size
            )
            # Varying frequency and amplitude
            freq = 440 * (1 + 0.1 * np.sin(2 * np.pi * 0.5 * second))
            amplitude = 0.5 + 0.3 * np.sin(2 * np.pi * 0.3 * second)
            chunk = amplitude * np.sin(2 * np.pi * freq * t)

            buffer.add_samples(chunk.astype(np.float32))

        # Process current 1-second clip
        crowd_state = simulator.get_current_state()
        people_count = crowd_state["crowd_size"]

        result = buffer.process_current_clip(people_count)

        print(f"Second {second + 1}:")
        print(f"  People: {people_count}")
        print(f"  RMS Energy: {result['amplitude']['rms_energy']:.4f}")
        print(f"  Quality Score: {result['acceptability_indicators']['quality_score']:.1f}/100")
        print(f"  Acceptable: {result['acceptability_indicators']['acceptable']}")
        print(f"  Recommendation: {result['acceptability_indicators']['recommendation']}")

        # Simulate the crowd changing (manually update the simulator state)
        # Note: MockCrowdSimulator doesn't have simulate_time_step, so we'll just
        # get a new state on each iteration

        await asyncio.sleep(0.1)  # Small delay for readability


async def main():
    """Run all tests"""
    print("\n")
    print("🎵" * 40)
    print("  REAL-TIME AUDIO CLIP ANALYSIS SYSTEM")
    print("  Preprocessing Pipeline for MCP + LLM")
    print("🎵" * 40)
    print()

    try:
        await test_basic_audio_processing()
        await test_mcp_audio_tool()
        await test_acceptability_check()
        await test_realtime_buffer()

        print("\n" + "=" * 80)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
        print("=" * 80)
        print("\nThe audio clip processing system is ready for:")
        print("  1. Real-time 1-second audio clip analysis")
        print("  2. Integration with people count from crowd system")
        print("  3. MCP data feed to LLM for acceptability decisions")
        print("  4. Automatic quality and correlation checks")
        print("\nNext steps:")
        print("  - Connect real audio input (microphone/line-in)")
        print("  - Integrate with live crowd detection")
        print("  - Use MCP tools in Claude for decision-making")
        print()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
