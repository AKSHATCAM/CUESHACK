"""
Real-time Audio Clip Processor
Processes 1-second audio clips with people context for LLM analysis
"""

import numpy as np
import librosa
from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass
import json


@dataclass
class AudioClipMetrics:
    """Metrics extracted from 1-second audio clip"""

    # Temporal features
    timestamp: str
    duration: float

    # Amplitude features
    rms_energy: float  # Root mean square energy
    peak_amplitude: float
    dynamic_range: float

    # Frequency features
    spectral_centroid: float  # Brightness of sound
    spectral_bandwidth: float  # Width of frequency spectrum
    spectral_rolloff: float  # Frequency below which 85% of energy is contained
    zero_crossing_rate: float  # Measure of noisiness

    # Rhythm features
    tempo: Optional[float]  # Estimated BPM
    beat_strength: float

    # Audio quality indicators
    clipping_detected: bool  # Audio distortion
    silence_ratio: float  # Percentage of silence
    noise_floor: float  # Background noise level

    # Harmonic/percussive separation
    harmonic_ratio: float  # Musical content vs noise
    percussive_ratio: float  # Beat/rhythm content

    # Context
    people_count: int
    energy_per_person: float  # Audio energy normalized by people


class AudioClipProcessor:
    """
    Processes 1-second audio clips in real-time for MCP data feed
    """

    def __init__(self, sample_rate: int = 22050):
        """
        Initialize audio clip processor

        Args:
            sample_rate: Audio sample rate in Hz (default 22050 for efficiency)
        """
        self.sample_rate = sample_rate
        self.clip_duration = 1.0  # seconds
        self.expected_samples = int(sample_rate * self.clip_duration)

    def process_clip(
        self,
        audio_data: np.ndarray,
        people_count: int,
        timestamp: Optional[str] = None
    ) -> AudioClipMetrics:
        """
        Process a 1-second audio clip and extract comprehensive metrics

        Args:
            audio_data: 1D numpy array of audio samples (mono)
            people_count: Number of people currently in the system
            timestamp: Optional timestamp, will use current time if not provided

        Returns:
            AudioClipMetrics object with all extracted features
        """
        if timestamp is None:
            timestamp = datetime.now().isoformat()

        # Ensure correct shape and duration
        if len(audio_data.shape) > 1:
            # Convert stereo to mono if needed
            audio_data = librosa.to_mono(audio_data)

        duration = len(audio_data) / self.sample_rate

        # Extract features
        metrics = AudioClipMetrics(
            timestamp=timestamp,
            duration=duration,

            # Amplitude features
            rms_energy=self._calculate_rms(audio_data),
            peak_amplitude=self._calculate_peak(audio_data),
            dynamic_range=self._calculate_dynamic_range(audio_data),

            # Frequency features
            spectral_centroid=self._calculate_spectral_centroid(audio_data),
            spectral_bandwidth=self._calculate_spectral_bandwidth(audio_data),
            spectral_rolloff=self._calculate_spectral_rolloff(audio_data),
            zero_crossing_rate=self._calculate_zero_crossing_rate(audio_data),

            # Rhythm features
            tempo=self._estimate_tempo(audio_data),
            beat_strength=self._calculate_beat_strength(audio_data),

            # Quality indicators
            clipping_detected=self._detect_clipping(audio_data),
            silence_ratio=self._calculate_silence_ratio(audio_data),
            noise_floor=self._calculate_noise_floor(audio_data),

            # Harmonic/percussive
            harmonic_ratio=self._calculate_harmonic_ratio(audio_data),
            percussive_ratio=self._calculate_percussive_ratio(audio_data),

            # Context
            people_count=people_count,
            energy_per_person=self._calculate_energy_per_person(audio_data, people_count)
        )

        return metrics

    def _calculate_rms(self, audio: np.ndarray) -> float:
        """Calculate root mean square energy (overall loudness)"""
        rms = librosa.feature.rms(y=audio)[0]
        return float(np.mean(rms))

    def _calculate_peak(self, audio: np.ndarray) -> float:
        """Calculate peak amplitude"""
        return float(np.max(np.abs(audio)))

    def _calculate_dynamic_range(self, audio: np.ndarray) -> float:
        """Calculate dynamic range (dB)"""
        peak = np.max(np.abs(audio))
        rms = np.sqrt(np.mean(audio**2))
        if rms > 0:
            return float(20 * np.log10(peak / rms))
        return 0.0

    def _calculate_spectral_centroid(self, audio: np.ndarray) -> float:
        """Calculate spectral centroid (brightness of sound)"""
        centroid = librosa.feature.spectral_centroid(y=audio, sr=self.sample_rate)[0]
        return float(np.mean(centroid))

    def _calculate_spectral_bandwidth(self, audio: np.ndarray) -> float:
        """Calculate spectral bandwidth"""
        bandwidth = librosa.feature.spectral_bandwidth(y=audio, sr=self.sample_rate)[0]
        return float(np.mean(bandwidth))

    def _calculate_spectral_rolloff(self, audio: np.ndarray) -> float:
        """Calculate spectral rolloff"""
        rolloff = librosa.feature.spectral_rolloff(y=audio, sr=self.sample_rate)[0]
        return float(np.mean(rolloff))

    def _calculate_zero_crossing_rate(self, audio: np.ndarray) -> float:
        """Calculate zero crossing rate (noisiness indicator)"""
        zcr = librosa.feature.zero_crossing_rate(audio)[0]
        return float(np.mean(zcr))

    def _estimate_tempo(self, audio: np.ndarray) -> Optional[float]:
        """Estimate tempo (BPM) - may be unreliable for 1-second clips"""
        try:
            onset_env = librosa.onset.onset_strength(y=audio, sr=self.sample_rate)
            # Use updated librosa API
            try:
                from librosa.feature.rhythm import tempo as tempo_func
                tempo = tempo_func(onset_envelope=onset_env, sr=self.sample_rate)
            except ImportError:
                # Fallback for older librosa versions
                tempo = librosa.beat.tempo(onset_envelope=onset_env, sr=self.sample_rate)
            return float(tempo[0]) if len(tempo) > 0 else None
        except:
            return None

    def _calculate_beat_strength(self, audio: np.ndarray) -> float:
        """Calculate beat/rhythm strength"""
        onset_env = librosa.onset.onset_strength(y=audio, sr=self.sample_rate)
        return float(np.mean(onset_env))

    def _detect_clipping(self, audio: np.ndarray, threshold: float = 0.99) -> bool:
        """Detect if audio is clipping (distortion)"""
        max_val = np.max(np.abs(audio))
        return bool(max_val >= threshold)

    def _calculate_silence_ratio(self, audio: np.ndarray, threshold: float = 0.01) -> float:
        """Calculate percentage of silence in clip"""
        silent_samples = np.sum(np.abs(audio) < threshold)
        return float(silent_samples / len(audio))

    def _calculate_noise_floor(self, audio: np.ndarray) -> float:
        """Calculate background noise floor level"""
        # Use bottom 10th percentile as noise floor estimate
        return float(np.percentile(np.abs(audio), 10))

    def _calculate_harmonic_ratio(self, audio: np.ndarray) -> float:
        """Calculate ratio of harmonic (musical) content"""
        harmonic, percussive = librosa.effects.hpss(audio)
        total_energy = np.sum(audio**2)
        harmonic_energy = np.sum(harmonic**2)
        if total_energy > 0:
            return float(harmonic_energy / total_energy)
        return 0.0

    def _calculate_percussive_ratio(self, audio: np.ndarray) -> float:
        """Calculate ratio of percussive (beat/rhythm) content"""
        harmonic, percussive = librosa.effects.hpss(audio)
        total_energy = np.sum(audio**2)
        percussive_energy = np.sum(percussive**2)
        if total_energy > 0:
            return float(percussive_energy / total_energy)
        return 0.0

    def _calculate_energy_per_person(self, audio: np.ndarray, people_count: int) -> float:
        """Calculate audio energy normalized by number of people"""
        rms = self._calculate_rms(audio)
        if people_count > 0:
            return float(rms / people_count)
        return float(rms)

    def metrics_to_dict(self, metrics: AudioClipMetrics) -> Dict[str, Any]:
        """Convert metrics to dictionary for MCP/JSON serialization"""
        return {
            "timestamp": metrics.timestamp,
            "duration": metrics.duration,
            "amplitude": {
                "rms_energy": metrics.rms_energy,
                "peak_amplitude": metrics.peak_amplitude,
                "dynamic_range_db": metrics.dynamic_range,
            },
            "frequency": {
                "spectral_centroid_hz": metrics.spectral_centroid,
                "spectral_bandwidth_hz": metrics.spectral_bandwidth,
                "spectral_rolloff_hz": metrics.spectral_rolloff,
                "zero_crossing_rate": metrics.zero_crossing_rate,
            },
            "rhythm": {
                "estimated_tempo_bpm": metrics.tempo,
                "beat_strength": metrics.beat_strength,
            },
            "quality": {
                "clipping_detected": metrics.clipping_detected,
                "silence_ratio": metrics.silence_ratio,
                "noise_floor": metrics.noise_floor,
            },
            "content": {
                "harmonic_ratio": metrics.harmonic_ratio,
                "percussive_ratio": metrics.percussive_ratio,
            },
            "context": {
                "people_count": metrics.people_count,
                "energy_per_person": metrics.energy_per_person,
            },
            "acceptability_indicators": self._generate_acceptability_indicators(metrics)
        }

    def _generate_acceptability_indicators(self, metrics: AudioClipMetrics) -> Dict[str, Any]:
        """
        Generate acceptability indicators for LLM to evaluate
        These help the LLM determine if the audio clip is acceptable
        """
        issues = []
        warnings = []
        quality_score = 100.0

        # Check for clipping
        if metrics.clipping_detected:
            issues.append("Audio clipping detected - possible distortion")
            quality_score -= 30

        # Check for excessive silence
        if metrics.silence_ratio > 0.8:
            warnings.append("Clip is mostly silent")
            quality_score -= 15

        # Check if too quiet
        if metrics.rms_energy < 0.01:
            warnings.append("Audio level very low")
            quality_score -= 10

        # Check if too loud
        if metrics.rms_energy > 0.9:
            warnings.append("Audio level very high")
            quality_score -= 10

        # Check dynamic range
        if metrics.dynamic_range < 6:
            warnings.append("Low dynamic range - possible compression/distortion")
            quality_score -= 15

        # Check for excessive noise
        if metrics.zero_crossing_rate > 0.3:
            warnings.append("High noise level detected")
            quality_score -= 10

        # Check harmonic content
        if metrics.harmonic_ratio < 0.2 and metrics.percussive_ratio < 0.2:
            warnings.append("Unclear musical content")
            quality_score -= 10

        # People context checks
        if metrics.people_count == 0:
            warnings.append("No people detected but audio is playing")
        elif metrics.energy_per_person > 0.1:
            issues.append("Audio level may be too loud for crowd size")
            quality_score -= 10
        elif metrics.energy_per_person < 0.001 and metrics.people_count > 10:
            warnings.append("Audio level may be too quiet for crowd size")
            quality_score -= 5

        return {
            "quality_score": max(0, quality_score),
            "issues": issues,
            "warnings": warnings,
            "acceptable": len(issues) == 0 and quality_score > 50,
            "recommendation": self._generate_recommendation(issues, warnings, quality_score)
        }

    def _generate_recommendation(
        self,
        issues: list,
        warnings: list,
        quality_score: float
    ) -> str:
        """Generate human-readable recommendation"""
        if len(issues) > 0:
            return f"NOT ACCEPTABLE: {'; '.join(issues)}"
        elif quality_score < 50:
            return f"MARGINAL: Quality score {quality_score:.1f}/100"
        elif len(warnings) > 0:
            return f"ACCEPTABLE with warnings: {'; '.join(warnings)}"
        else:
            return f"ACCEPTABLE: Good audio quality (score: {quality_score:.1f}/100)"


# Real-time buffer for continuous processing
class AudioClipBuffer:
    """
    Manages real-time buffering of audio for 1-second clip processing
    """

    def __init__(self, sample_rate: int = 22050):
        self.sample_rate = sample_rate
        self.clip_duration = 1.0
        self.buffer_size = int(sample_rate * self.clip_duration)
        self.buffer = np.zeros(self.buffer_size, dtype=np.float32)
        self.processor = AudioClipProcessor(sample_rate)

    def add_samples(self, samples: np.ndarray):
        """Add new samples to buffer (FIFO queue)"""
        # Roll buffer and add new samples
        samples_to_add = len(samples)
        self.buffer = np.roll(self.buffer, -samples_to_add)
        self.buffer[-samples_to_add:] = samples

    def get_current_clip(self) -> np.ndarray:
        """Get current 1-second clip from buffer"""
        return self.buffer.copy()

    def process_current_clip(self, people_count: int) -> Dict[str, Any]:
        """Process current clip and return metrics as dict"""
        clip = self.get_current_clip()
        metrics = self.processor.process_clip(clip, people_count)
        return self.processor.metrics_to_dict(metrics)
