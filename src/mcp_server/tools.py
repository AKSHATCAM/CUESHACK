"""
MCP Tools Implementation
Provides real-time crowd data to Claude
"""

import asyncio
import random
import numpy as np
from datetime import datetime
from typing import Dict, Any, Optional

# Import sensor modules (will use mock data initially)
from ..sensors.mock import MockCrowdSimulator
from ..sensors.audio_clip_processor import AudioClipBuffer, AudioClipProcessor

# Global simulator instance
simulator = MockCrowdSimulator()

# Global audio clip buffer for real-time processing
audio_buffer = AudioClipBuffer(sample_rate=22050)


async def get_crowd_energy(time_window: int = 5) -> Dict[str, Any]:
    """
    Get current crowd energy level

    Args:
        time_window: Time window in seconds to average over

    Returns:
        Dict with energy level, trend, and metadata
    """
    data = simulator.get_current_state()

    return {
        "energy": data["energy"],
        "trend": data["energy_trend"],
        "time_window_seconds": time_window,
        "timestamp": datetime.now().isoformat(),
        "interpretation": _interpret_energy(data["energy"]),
    }


async def get_crowd_mood() -> Dict[str, Any]:
    """
    Analyze current crowd mood/emotions

    Returns:
        Dict with mood distribution and dominant emotion
    """
    data = simulator.get_current_state()
    mood = data["mood"]

    # Find dominant emotion
    dominant = max(mood.items(), key=lambda x: x[1])

    return {
        "mood_distribution": mood,
        "dominant_emotion": dominant[0],
        "dominant_percentage": round(dominant[1] * 100, 1),
        "timestamp": datetime.now().isoformat(),
        "interpretation": _interpret_mood(dominant[0]),
    }


async def get_noise_level() -> Dict[str, Any]:
    """
    Get current noise level in decibels

    Returns:
        Dict with noise level and interpretation
    """
    data = simulator.get_current_state()

    return {
        "decibels": data["noise_db"],
        "normalized": data["noise_db"] / 100,  # 0-1 scale
        "timestamp": datetime.now().isoformat(),
        "interpretation": _interpret_noise(data["noise_db"]),
    }


async def get_movement_intensity() -> Dict[str, Any]:
    """
    Get crowd movement/dancing intensity

    Returns:
        Dict with movement intensity and people dancing
    """
    data = simulator.get_current_state()

    return {
        "intensity": data["movement"],
        "people_dancing_estimate": int(data["crowd_size"] * (data["movement"] / 100)),
        "timestamp": datetime.now().isoformat(),
        "interpretation": _interpret_movement(data["movement"]),
    }


async def get_crowd_density() -> Dict[str, Any]:
    """
    Get crowd size and density information

    Returns:
        Dict with people count and density rating
    """
    data = simulator.get_current_state()
    crowd_size = data["crowd_size"]
    capacity = 200  # TODO: Get from venue config

    density_pct = (crowd_size / capacity) * 100

    if density_pct < 30:
        density_rating = "sparse"
    elif density_pct < 70:
        density_rating = "moderate"
    else:
        density_rating = "packed"

    return {
        "people_count": crowd_size,
        "venue_capacity": capacity,
        "density_percentage": round(density_pct, 1),
        "density_rating": density_rating,
        "timestamp": datetime.now().isoformat(),
    }


async def get_time_context() -> Dict[str, Any]:
    """
    Get temporal context information

    Returns:
        Dict with time of day, event duration, etc.
    """
    data = simulator.get_current_state()

    now = datetime.now()
    set_duration_minutes = data.get("set_duration_minutes", 0)

    # Determine set phase
    if set_duration_minutes < 15:
        phase = "opening"
    elif set_duration_minutes < 45:
        phase = "building"
    elif set_duration_minutes < 90:
        phase = "peak"
    else:
        phase = "closing"

    return {
        "current_time": now.strftime("%H:%M:%S"),
        "time_of_day": "evening" if 18 <= now.hour < 24 else "night",
        "set_duration_minutes": set_duration_minutes,
        "set_phase": phase,
        "timestamp": now.isoformat(),
    }


async def get_full_context() -> Dict[str, Any]:
    """
    Get complete context snapshot with all metrics

    Returns:
        Dict with all crowd metrics
    """
    # Get all individual metrics
    energy = await get_crowd_energy()
    mood = await get_crowd_mood()
    noise = await get_noise_level()
    movement = await get_movement_intensity()
    density = await get_crowd_density()
    time_ctx = await get_time_context()

    return {
        "energy": energy,
        "mood": mood,
        "noise": noise,
        "movement": movement,
        "crowd_density": density,
        "time_context": time_ctx,
        "summary": _generate_context_summary(energy, mood, movement),
        "timestamp": datetime.now().isoformat(),
    }


# Helper functions for interpretation

def _interpret_energy(energy: float) -> str:
    """Interpret energy level"""
    if energy < 30:
        return "Very low - crowd needs energizing"
    elif energy < 50:
        return "Low - gradual energy increase recommended"
    elif energy < 70:
        return "Moderate - good baseline energy"
    elif energy < 85:
        return "High - crowd is engaged and dancing"
    else:
        return "Very high - peak energy, maintain or build to climax"


def _interpret_mood(dominant_mood: str) -> str:
    """Interpret dominant mood"""
    interpretations = {
        "happy": "Crowd is enjoying themselves, positive vibes",
        "excited": "High excitement, ready for energy",
        "neutral": "Crowd is present but not fully engaged",
        "bored": "WARNING: Crowd losing interest, change needed",
        "confused": "Crowd seems uncertain, consider more familiar music",
    }
    return interpretations.get(dominant_mood, "Unknown mood")


def _interpret_noise(decibels: float) -> str:
    """Interpret noise level"""
    if decibels < 65:
        return "Quiet - minimal crowd engagement"
    elif decibels < 75:
        return "Moderate - normal conversation/background noise"
    elif decibels < 85:
        return "Loud - active engagement, some singing along"
    else:
        return "Very loud - high engagement, cheering, singing"


def _interpret_movement(movement: float) -> str:
    """Interpret movement intensity"""
    if movement < 30:
        return "Minimal movement - mostly standing/sitting"
    elif movement < 50:
        return "Light movement - some swaying, head nodding"
    elif movement < 70:
        return "Moderate dancing - good portion of crowd moving"
    else:
        return "Heavy dancing - most of crowd actively dancing"


def _generate_context_summary(energy: Dict, mood: Dict, movement: Dict) -> str:
    """Generate human-readable context summary"""
    return (
        f"Energy at {energy['energy']}/100 ({energy['trend']}), "
        f"crowd is mostly {mood['dominant_emotion']} "
        f"with {movement['interpretation'].lower()}"
    )


async def analyze_audio_clip(
    audio_data: Optional[np.ndarray] = None,
    use_mock_data: bool = True
) -> Dict[str, Any]:
    """
    Analyze a 1-second audio clip with people count context

    This tool processes real-time audio and provides comprehensive metrics
    for the LLM to determine if the audio is acceptable.

    Args:
        audio_data: 1-second audio clip as numpy array (if None, generates mock data)
        use_mock_data: Whether to use simulated audio data

    Returns:
        Dict with audio metrics, people context, and acceptability indicators
    """
    # Get current crowd size from simulator
    crowd_data = simulator.get_current_state()
    people_count = crowd_data["crowd_size"]

    if use_mock_data or audio_data is None:
        # Generate mock 1-second audio clip
        sample_rate = 22050
        duration = 1.0

        # Create synthetic audio based on current crowd energy
        energy_level = crowd_data["energy"] / 100.0
        noise_level = crowd_data["noise_db"] / 100.0

        # Generate base sine wave (music)
        t = np.linspace(0, duration, int(sample_rate * duration))
        frequency = 440 * (1 + 0.5 * np.random.random())  # Varying pitch
        audio = 0.3 * energy_level * np.sin(2 * np.pi * frequency * t)

        # Add harmonic overtones
        audio += 0.15 * energy_level * np.sin(2 * np.pi * frequency * 2 * t)
        audio += 0.1 * energy_level * np.sin(2 * np.pi * frequency * 3 * t)

        # Add crowd noise
        crowd_noise = noise_level * 0.2 * np.random.randn(len(t))
        audio += crowd_noise

        # Add percussive elements (beats)
        beat_positions = np.random.choice(len(t), size=int(2 * energy_level), replace=False)
        for pos in beat_positions:
            if pos + 100 < len(audio):
                audio[pos:pos+100] += 0.4 * energy_level * np.exp(-np.arange(100) / 50)

        # Normalize
        if np.max(np.abs(audio)) > 0:
            audio = audio / np.max(np.abs(audio)) * 0.7

        audio_data = audio.astype(np.float32)

    # Process the audio clip
    processor = AudioClipProcessor(sample_rate=22050)
    metrics = processor.process_clip(audio_data, people_count)
    result = processor.metrics_to_dict(metrics)

    # Add crowd context for correlation
    result["crowd_context"] = {
        "energy_level": crowd_data["energy"],
        "dominant_mood": max(crowd_data["mood"].items(), key=lambda x: x[1])[0],
        "noise_db": crowd_data["noise_db"],
        "movement_intensity": crowd_data["movement"],
    }

    # Add correlation analysis
    result["correlation_analysis"] = _analyze_audio_crowd_correlation(result, crowd_data)

    return result


def _analyze_audio_crowd_correlation(audio_result: Dict, crowd_data: Dict) -> Dict[str, Any]:
    """
    Analyze correlation between audio metrics and crowd behavior
    Helps LLM understand if audio is appropriate for current crowd state
    """
    correlations = []

    # Check if audio energy matches crowd energy
    audio_energy = audio_result["amplitude"]["rms_energy"]
    crowd_energy = crowd_data["energy"] / 100.0

    energy_match = abs(audio_energy - crowd_energy * 0.7)  # Expected scaling
    if energy_match < 0.2:
        correlations.append("Audio energy matches crowd energy well")
    elif audio_energy > crowd_energy * 0.7:
        correlations.append("Audio may be too loud for current crowd energy")
    else:
        correlations.append("Audio may be too quiet for current crowd energy")

    # Check if beat strength matches movement
    beat_strength = audio_result["rhythm"]["beat_strength"]
    movement = crowd_data["movement"] / 100.0

    if beat_strength > 0.5 and movement > 0.6:
        correlations.append("Strong beat matches high crowd movement - good sync")
    elif beat_strength > 0.5 and movement < 0.3:
        correlations.append("Strong beat but low movement - crowd may not be responding")

    # Check harmonic content vs mood
    harmonic_ratio = audio_result["content"]["harmonic_ratio"]
    dominant_mood = max(crowd_data["mood"].items(), key=lambda x: x[1])[0]

    if harmonic_ratio > 0.5 and dominant_mood in ["happy", "excited"]:
        correlations.append("Musical content aligns with positive crowd mood")
    elif harmonic_ratio < 0.3 and dominant_mood == "confused":
        correlations.append("Low musical content may be confusing the crowd")

    return {
        "energy_correlation": "good" if energy_match < 0.2 else "needs_adjustment",
        "beat_movement_sync": "synchronized" if beat_strength > 0.5 and movement > 0.5 else "unsynchronized",
        "mood_music_alignment": "aligned" if harmonic_ratio > 0.4 else "misaligned",
        "observations": correlations,
        "overall_match": "good" if len([c for c in correlations if "good" in c or "matches" in c or "aligns" in c]) >= 2 else "needs_review"
    }


async def get_audio_acceptability_check() -> Dict[str, Any]:
    """
    Get a complete audio acceptability check with LLM-ready analysis

    This is a convenience tool that combines audio analysis with
    structured recommendations for the LLM to make decisions

    Returns:
        Dict with audio analysis and decision-making guidance
    """
    # Get audio analysis
    audio_analysis = await analyze_audio_clip(use_mock_data=True)

    # Extract key decision points
    acceptability = audio_analysis["acceptability_indicators"]
    correlation = audio_analysis["correlation_analysis"]

    return {
        "audio_analysis": audio_analysis,
        "decision_framework": {
            "is_acceptable": acceptability["acceptable"],
            "quality_score": acceptability["quality_score"],
            "critical_issues": acceptability["issues"],
            "warnings": acceptability["warnings"],
            "crowd_match": correlation["overall_match"],
            "recommendation": acceptability["recommendation"],
        },
        "llm_guidance": {
            "should_keep_playing": acceptability["acceptable"] and correlation["overall_match"] == "good",
            "suggested_actions": _generate_suggested_actions(acceptability, correlation),
            "reasoning_points": _generate_reasoning_points(audio_analysis),
        },
        "timestamp": datetime.now().isoformat(),
    }


def _generate_suggested_actions(acceptability: Dict, correlation: Dict) -> list:
    """Generate action suggestions for the LLM"""
    actions = []

    if not acceptability["acceptable"]:
        actions.append("STOP: Audio quality issues detected - switch track")

    if correlation["energy_correlation"] == "needs_adjustment":
        actions.append("Adjust volume to match crowd energy")

    if correlation["beat_movement_sync"] == "unsynchronized":
        actions.append("Consider changing to track with different tempo")

    if correlation["mood_music_alignment"] == "misaligned":
        actions.append("Music style may not match crowd mood")

    if len(actions) == 0:
        actions.append("CONTINUE: Audio is acceptable and matches crowd")

    return actions


def _generate_reasoning_points(audio_analysis: Dict) -> list:
    """Generate reasoning points for LLM explanation"""
    points = []

    # Audio quality
    quality = audio_analysis["quality"]
    if quality["clipping_detected"]:
        points.append("Audio clipping indicates distortion or overdriving")
    if quality["silence_ratio"] > 0.5:
        points.append(f"Audio is {quality['silence_ratio']*100:.1f}% silent")

    # Content analysis
    content = audio_analysis["content"]
    points.append(f"Harmonic ratio: {content['harmonic_ratio']:.2f} (musical content)")
    points.append(f"Percussive ratio: {content['percussive_ratio']:.2f} (rhythm/beats)")

    # People context
    context = audio_analysis["context"]
    points.append(f"Audio energy per person: {context['energy_per_person']:.4f}")
    points.append(f"Current crowd: {context['people_count']} people")

    return points
