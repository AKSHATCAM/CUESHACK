"""
Live Microphone Audio Capture and Processing

This module provides real-time microphone input capture and processing using the existing
AudioClipProcessor infrastructure. It captures audio continuously, processes 1-second clips,
and extracts sound level (RMS) and frequency metrics for LLM interpretation.

Key Features:
- Real-time microphone capture using sounddevice
- Integration with AudioClipBuffer for continuous processing
- Extraction of RMS energy and frequency metrics
- Non-blocking audio processing with callback mechanism
- Configurable sample rate and buffer settings

Usage:
    from src.sensors.live_microphone import LiveMicrophoneProcessor

    # Create processor
    processor = LiveMicrophoneProcessor(sample_rate=22050, people_count=50)

    # Start capturing
    processor.start()

    # Get latest metrics
    metrics = processor.get_latest_metrics()
    print(f"Sound Level (RMS): {metrics['rms_energy']:.4f}")
    print(f"Frequency (Spectral Centroid): {metrics['spectral_centroid']:.2f} Hz")

    # Stop when done
    processor.stop()
"""

import sounddevice as sd
import numpy as np
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass
from datetime import datetime
import threading
import queue
import time

from .audio_clip_processor import AudioClipBuffer, AudioClipProcessor


@dataclass
class LiveAudioMetrics:
    """Simplified metrics for real-time monitoring focused on sound level and frequency"""

    timestamp: datetime

    # Sound Level Metrics
    rms_energy: float  # Root Mean Square energy (overall loudness)
    peak_amplitude: float  # Maximum amplitude
    dynamic_range: float  # Range in dB

    # Frequency Metrics
    spectral_centroid: float  # Center of mass of spectrum (brightness)
    spectral_bandwidth: float  # Width of spectrum
    spectral_rolloff: float  # Frequency below which 85% of energy is contained

    # Quality Indicators
    clipping_detected: bool
    silence_ratio: float
    quality_score: int

    # Context
    people_count: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for easy serialization"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'sound_level': {
                'rms_energy': self.rms_energy,
                'peak_amplitude': self.peak_amplitude,
                'dynamic_range_db': self.dynamic_range
            },
            'frequency': {
                'spectral_centroid_hz': self.spectral_centroid,
                'spectral_bandwidth_hz': self.spectral_bandwidth,
                'spectral_rolloff_hz': self.spectral_rolloff
            },
            'quality': {
                'clipping_detected': self.clipping_detected,
                'silence_ratio': self.silence_ratio,
                'quality_score': self.quality_score
            },
            'context': {
                'people_count': self.people_count
            }
        }

    def summary(self) -> str:
        """Human-readable summary of metrics"""
        return (
            f"Sound Level: RMS={self.rms_energy:.4f}, Peak={self.peak_amplitude:.4f}\n"
            f"Frequency: Center={self.spectral_centroid:.1f}Hz, Bandwidth={self.spectral_bandwidth:.1f}Hz\n"
            f"Quality: Score={self.quality_score}/100, Clipping={'Yes' if self.clipping_detected else 'No'}"
        )


class LiveMicrophoneProcessor:
    """
    Real-time microphone capture and audio processing.

    This class captures live audio from the system's default microphone,
    processes it in 1-second clips, and extracts sound level and frequency metrics.
    """

    def __init__(
        self,
        sample_rate: int = 22050,
        people_count: int = 0,
        clip_duration: float = 1.0,
        device: Optional[int] = None,
        callback: Optional[Callable[[LiveAudioMetrics], None]] = None
    ):
        """
        Initialize the live microphone processor.

        Args:
            sample_rate: Audio sample rate in Hz (default: 22050)
            people_count: Current crowd size for context (default: 0)
            clip_duration: Duration of each analysis clip in seconds (default: 1.0)
            device: Sounddevice input device ID (None for default)
            callback: Optional callback function called with each new metric result
        """
        self.sample_rate = sample_rate
        self.people_count = people_count
        self.clip_duration = clip_duration
        self.device = device
        self.callback = callback

        # Audio processing components
        self.buffer = AudioClipBuffer(
            sample_rate=sample_rate,
            clip_duration=clip_duration
        )
        self.processor = AudioClipProcessor(sample_rate=sample_rate)

        # Streaming state
        self.stream: Optional[sd.InputStream] = None
        self.is_running = False
        self._latest_metrics: Optional[LiveAudioMetrics] = None
        self._metrics_lock = threading.Lock()

        # Processing thread
        self._processing_queue: queue.Queue = queue.Queue()
        self._processing_thread: Optional[threading.Thread] = None

    def _audio_callback(self, indata: np.ndarray, frames: int, time_info, status):
        """
        Callback function called by sounddevice for each audio block.

        This runs in a separate thread managed by sounddevice.
        """
        if status:
            print(f"Audio callback status: {status}")

        # Convert to mono if stereo
        if indata.shape[1] > 1:
            audio_data = np.mean(indata, axis=1)
        else:
            audio_data = indata[:, 0]

        # Add to buffer
        self.buffer.add_samples(audio_data)

        # Check if we have a complete clip to process
        if self.buffer.is_ready():
            # Queue for processing in separate thread
            self._processing_queue.put(time.time())

    def _processing_worker(self):
        """Worker thread that processes complete audio clips"""
        while self.is_running:
            try:
                # Wait for a clip to be ready (with timeout to allow clean shutdown)
                timestamp = self._processing_queue.get(timeout=0.1)

                # Process the current clip
                clip_metrics = self.buffer.process_current_clip(self.people_count)

                if clip_metrics:
                    # Extract simplified metrics
                    live_metrics = LiveAudioMetrics(
                        timestamp=clip_metrics.timestamp,
                        rms_energy=clip_metrics.rms_energy,
                        peak_amplitude=clip_metrics.peak_amplitude,
                        dynamic_range=clip_metrics.dynamic_range,
                        spectral_centroid=clip_metrics.spectral_centroid,
                        spectral_bandwidth=clip_metrics.spectral_bandwidth,
                        spectral_rolloff=clip_metrics.spectral_rolloff,
                        clipping_detected=clip_metrics.clipping_detected,
                        silence_ratio=clip_metrics.silence_ratio,
                        quality_score=self.processor.metrics_to_dict(clip_metrics)['acceptability_indicators']['quality_score'],
                        people_count=clip_metrics.people_count
                    )

                    # Update latest metrics
                    with self._metrics_lock:
                        self._latest_metrics = live_metrics

                    # Call user callback if provided
                    if self.callback:
                        try:
                            self.callback(live_metrics)
                        except Exception as e:
                            print(f"Error in user callback: {e}")

            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error processing audio clip: {e}")

    def start(self):
        """Start capturing audio from the microphone"""
        if self.is_running:
            print("Microphone processor is already running")
            return

        print(f"Starting microphone capture (sample_rate={self.sample_rate}Hz, device={self.device})")
        print(f"Available audio devices:")
        print(sd.query_devices())

        self.is_running = True

        # Start processing thread
        self._processing_thread = threading.Thread(target=self._processing_worker, daemon=True)
        self._processing_thread.start()

        # Start audio stream
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            device=self.device,
            callback=self._audio_callback,
            blocksize=2048
        )
        self.stream.start()

        print("Microphone capture started successfully")

    def stop(self):
        """Stop capturing audio"""
        if not self.is_running:
            return

        print("Stopping microphone capture...")
        self.is_running = False

        # Stop audio stream
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

        # Wait for processing thread to finish
        if self._processing_thread:
            self._processing_thread.join(timeout=2.0)

        print("Microphone capture stopped")

    def get_latest_metrics(self) -> Optional[LiveAudioMetrics]:
        """Get the most recent metrics computed"""
        with self._metrics_lock:
            return self._latest_metrics

    def update_people_count(self, count: int):
        """Update the people count for context in future analyses"""
        self.people_count = count

    def __enter__(self):
        """Context manager support"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager support"""
        self.stop()


def list_audio_devices():
    """Helper function to list all available audio input devices"""
    print("Available Audio Devices:")
    print("=" * 80)
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        if device['max_input_channels'] > 0:
            print(f"[{i}] {device['name']}")
            print(f"    Sample Rate: {device['default_samplerate']} Hz")
            print(f"    Input Channels: {device['max_input_channels']}")
            print()


if __name__ == "__main__":
    """Example usage"""

    # List available devices
    list_audio_devices()

    print("\n" + "=" * 80)
    print("Starting live microphone processing...")
    print("Speak into your microphone. Press Ctrl+C to stop.")
    print("=" * 80 + "\n")

    # Create processor with callback
    def on_new_metrics(metrics: LiveAudioMetrics):
        """Called every second with new metrics"""
        print(f"\n[{metrics.timestamp.strftime('%H:%M:%S')}]")
        print(metrics.summary())

    processor = LiveMicrophoneProcessor(
        sample_rate=22050,
        people_count=50,  # Example: assume 50 people in venue
        callback=on_new_metrics
    )

    try:
        # Start processing
        processor.start()

        # Keep running until interrupted
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\nStopping...")
        processor.stop()
        print("Done!")
