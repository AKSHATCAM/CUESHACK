"""
MCP Tools Implementation
Provides real-time crowd data to Claude
"""

import asyncio
import random
from datetime import datetime
from typing import Dict, Any

# Import sensor modules (will use mock data initially)
from ..sensors.mock import MockCrowdSimulator

# Global simulator instance
simulator = MockCrowdSimulator()


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
