"""
Tests for Mock Crowd Simulator
"""

import pytest
import time
from src.sensors.mock import MockCrowdSimulator


def test_simulator_initialization():
    """Test that simulator initializes correctly"""
    simulator = MockCrowdSimulator()
    assert simulator is not None
    assert simulator.base_energy == 50.0


def test_get_current_state():
    """Test that current state returns all expected fields"""
    simulator = MockCrowdSimulator()
    state = simulator.get_current_state()

    # Check all required fields are present
    assert "energy" in state
    assert "energy_trend" in state
    assert "mood" in state
    assert "noise_db" in state
    assert "movement" in state
    assert "crowd_size" in state
    assert "set_duration_minutes" in state
    assert "timestamp" in state


def test_energy_range():
    """Test that energy stays within valid range"""
    simulator = MockCrowdSimulator()

    for _ in range(100):
        state = simulator.get_current_state()
        assert 0 <= state["energy"] <= 100, f"Energy {state['energy']} out of range"
        time.sleep(0.01)  # Small delay


def test_mood_distribution():
    """Test that mood distribution sums to approximately 1.0"""
    simulator = MockCrowdSimulator()
    state = simulator.get_current_state()

    mood = state["mood"]
    total = sum(mood.values())

    assert 0.95 <= total <= 1.05, f"Mood distribution sums to {total}"


def test_noise_level_range():
    """Test that noise level is realistic"""
    simulator = MockCrowdSimulator()
    state = simulator.get_current_state()

    noise = state["noise_db"]
    assert 50 <= noise <= 110, f"Noise level {noise} dB seems unrealistic"


def test_crowd_size_range():
    """Test that crowd size is within venue capacity"""
    simulator = MockCrowdSimulator()
    state = simulator.get_current_state()

    crowd = state["crowd_size"]
    assert 0 <= crowd <= 250, f"Crowd size {crowd} out of expected range"


def test_energy_trends():
    """Test that energy trend is one of valid values"""
    simulator = MockCrowdSimulator()
    state = simulator.get_current_state()

    trend = state["energy_trend"]
    assert trend in ["rising", "falling", "stable"]


def test_simulator_progression():
    """Test that simulator progresses over time"""
    simulator = MockCrowdSimulator()

    state1 = simulator.get_current_state()
    time.sleep(0.1)
    state2 = simulator.get_current_state()

    # Time should progress
    assert state2["set_duration_minutes"] >= state1["set_duration_minutes"]


def test_mood_keys():
    """Test that mood contains expected emotions"""
    simulator = MockCrowdSimulator()
    state = simulator.get_current_state()

    mood = state["mood"]
    expected_emotions = ["happy", "excited", "neutral", "bored", "confused"]

    for emotion in expected_emotions:
        assert emotion in mood, f"Missing emotion: {emotion}"


def test_reset_functionality():
    """Test that reset works correctly"""
    simulator = MockCrowdSimulator()

    # Let some time pass
    time.sleep(0.2)
    state1 = simulator.get_current_state()

    # Reset
    simulator.reset()
    state2 = simulator.get_current_state()

    # Duration should be close to zero after reset
    assert state2["set_duration_minutes"] < state1["set_duration_minutes"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
