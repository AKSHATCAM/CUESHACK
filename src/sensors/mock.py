"""
Mock Crowd Simulator
Generates realistic crowd data for testing without real sensors
"""

import random
import time
import math
from typing import Dict, Any


class MockCrowdSimulator:
    """
    Simulates realistic crowd behavior patterns

    Simulates:
    - Energy levels that build and drop over time
    - Mood variations
    - Noise levels correlated with energy
    - Movement/dancing intensity
    - Crowd size changes
    """

    def __init__(self):
        self.start_time = time.time()
        self.base_energy = 50.0
        self.energy_trend = "stable"

        # Simulation parameters
        self.time_scale = 1.0  # Simulation speed multiplier
        self.event_probability = 0.05  # Probability of random events

    def get_current_state(self) -> Dict[str, Any]:
        """
        Get current simulated crowd state

        Returns:
            Dict with all crowd metrics
        """
        elapsed_minutes = (time.time() - self.start_time) / 60 * self.time_scale

        # Calculate energy based on typical event curve
        energy = self._calculate_energy(elapsed_minutes)

        # Generate correlated metrics
        mood = self._generate_mood(energy)
        noise_db = self._calculate_noise(energy)
        movement = self._calculate_movement(energy)
        crowd_size = self._calculate_crowd_size(elapsed_minutes)

        return {
            "energy": round(energy, 1),
            "energy_trend": self._determine_trend(energy),
            "mood": mood,
            "noise_db": round(noise_db, 1),
            "movement": round(movement, 1),
            "crowd_size": crowd_size,
            "set_duration_minutes": round(elapsed_minutes, 1),
            "timestamp": time.time(),
        }

    def _calculate_energy(self, minutes: float) -> float:
        """
        Calculate energy level based on typical DJ set curve

        Pattern:
        - 0-15 min: Opening (30-50 energy)
        - 15-45 min: Building (50-75 energy)
        - 45-90 min: Peak (75-95 energy)
        - 90+ min: Closing (declining from peak)
        """
        # Base curve using sine wave
        period = 120  # 2-hour cycle
        base = 50 + 30 * math.sin(2 * math.pi * minutes / period)

        # Add event phases
        if minutes < 15:
            # Opening - gradual increase
            phase_factor = 0.6 + (minutes / 15) * 0.4
        elif minutes < 45:
            # Building
            phase_factor = 1.0 + (minutes - 15) / 30 * 0.3
        elif minutes < 90:
            # Peak time
            phase_factor = 1.3 + 0.2 * math.sin(minutes / 10)
        else:
            # Closing - gradual decrease
            phase_factor = 1.3 - (minutes - 90) / 30 * 0.5

        energy = base * phase_factor

        # Add random fluctuations
        noise = random.uniform(-5, 5)
        energy += noise

        # Random events (energy spikes/drops)
        if random.random() < self.event_probability:
            energy += random.uniform(-15, 20)

        # Clamp to valid range
        return max(0, min(100, energy))

    def _generate_mood(self, energy: float) -> Dict[str, float]:
        """
        Generate mood distribution based on energy level

        Higher energy = more happy/excited
        Lower energy = more neutral/bored
        """
        # Base probabilities
        if energy > 70:
            # High energy - mostly happy and excited
            mood_probs = {
                "happy": 0.45,
                "excited": 0.35,
                "neutral": 0.15,
                "bored": 0.03,
                "confused": 0.02,
            }
        elif energy > 50:
            # Moderate energy - balanced positive
            mood_probs = {
                "happy": 0.40,
                "excited": 0.20,
                "neutral": 0.30,
                "bored": 0.07,
                "confused": 0.03,
            }
        elif energy > 30:
            # Low energy - more neutral
            mood_probs = {
                "happy": 0.20,
                "excited": 0.10,
                "neutral": 0.50,
                "bored": 0.15,
                "confused": 0.05,
            }
        else:
            # Very low energy - problematic
            mood_probs = {
                "happy": 0.10,
                "excited": 0.05,
                "neutral": 0.40,
                "bored": 0.35,
                "confused": 0.10,
            }

        # Add small random variations
        for mood in mood_probs:
            mood_probs[mood] += random.uniform(-0.05, 0.05)

        # Normalize to sum to 1.0
        total = sum(mood_probs.values())
        return {k: v / total for k, v in mood_probs.items()}

    def _calculate_noise(self, energy: float) -> float:
        """
        Calculate noise level in dB based on energy

        Range: 60-95 dB
        Higher energy = more noise (cheering, singing)
        """
        # Base noise level
        base_noise = 65

        # Energy contribution (0-30 dB)
        energy_noise = (energy / 100) * 30

        # Random fluctuation
        fluctuation = random.uniform(-3, 3)

        return base_noise + energy_noise + fluctuation

    def _calculate_movement(self, energy: float) -> float:
        """
        Calculate movement intensity based on energy

        Movement typically correlates with energy but with some lag
        """
        # Movement follows energy with slight randomness
        base_movement = energy * 0.9  # Slightly lower than energy

        # Add variation
        variation = random.uniform(-10, 10)

        movement = base_movement + variation

        return max(0, min(100, movement))

    def _calculate_crowd_size(self, minutes: float) -> int:
        """
        Calculate crowd size based on time

        Pattern:
        - Early: crowd building
        - Middle: peak attendance
        - Late: some people leaving
        """
        max_capacity = 200

        if minutes < 20:
            # Arriving
            size_factor = 0.3 + (minutes / 20) * 0.5
        elif minutes < 100:
            # Peak attendance
            size_factor = 0.8 + random.uniform(-0.1, 0.15)
        else:
            # Some leaving
            size_factor = 0.8 - (minutes - 100) / 40 * 0.4

        crowd_size = int(max_capacity * size_factor)

        # Add randomness
        crowd_size += random.randint(-10, 10)

        return max(0, min(max_capacity, crowd_size))

    def _determine_trend(self, current_energy: float) -> str:
        """
        Determine energy trend (rising, falling, stable)
        """
        # Store and compare with previous energy
        diff = current_energy - self.base_energy
        self.base_energy = current_energy  # Update for next call

        if diff > 3:
            return "rising"
        elif diff < -3:
            return "falling"
        else:
            return "stable"

    def trigger_event(self, event_type: str):
        """
        Manually trigger specific events for testing

        Args:
            event_type: 'energy_spike', 'energy_drop', 'crowd_surge', etc.
        """
        # TODO: Implement manual event triggering
        pass

    def reset(self):
        """Reset simulator to initial state"""
        self.start_time = time.time()
        self.base_energy = 50.0
        self.energy_trend = "stable"


# Convenience function for quick testing
def get_mock_crowd_data() -> Dict[str, Any]:
    """Get a single snapshot of mock crowd data"""
    simulator = MockCrowdSimulator()
    return simulator.get_current_state()


if __name__ == "__main__":
    # Test the simulator
    simulator = MockCrowdSimulator()

    print("Mock Crowd Simulator Test")
    print("=" * 50)

    for i in range(10):
        state = simulator.get_current_state()
        print(f"\nMinute {state['set_duration_minutes']:.1f}:")
        print(f"  Energy: {state['energy']:.1f} ({state['energy_trend']})")
        print(f"  Mood: {max(state['mood'].items(), key=lambda x: x[1])[0]}")
        print(f"  Noise: {state['noise_db']:.1f} dB")
        print(f"  Movement: {state['movement']:.1f}")
        print(f"  Crowd: {state['crowd_size']} people")

        time.sleep(0.5)  # Simulate passage of time
