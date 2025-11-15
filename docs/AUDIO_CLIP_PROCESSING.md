# Real-Time Audio Clip Processing System

## Overview

This system processes **1-second audio clips** in real-time, correlates them with **crowd data** (number of people), and provides a **structured data feed via MCP** for LLM-based acceptability decisions.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Real-Time Audio Pipeline                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Audio Input (1-second clips)                                   │
│         │                                                         │
│         ↓                                                         │
│  ┌──────────────────┐                                           │
│  │  AudioClipBuffer │  ← Continuous buffering (FIFO)            │
│  └──────────────────┘                                           │
│         │                                                         │
│         ↓                                                         │
│  ┌───────────────────────┐                                      │
│  │ AudioClipProcessor    │  ← Feature extraction                │
│  └───────────────────────┘                                      │
│         │                                                         │
│         ↓                                                         │
│  ┌─────────────────────────────────────────┐                   │
│  │  Audio Metrics:                          │                   │
│  │  • Amplitude (RMS, peak, dynamic range) │                   │
│  │  • Frequency (spectral analysis)        │                   │
│  │  • Rhythm (tempo, beat strength)        │                   │
│  │  • Quality (clipping, noise, silence)   │                   │
│  │  • Content (harmonic, percussive)       │                   │
│  └─────────────────────────────────────────┘                   │
│         │                                                         │
│         ↓                                                         │
│  ┌─────────────────────────────────────────┐                   │
│  │  People Count Context                   │                   │
│  │  • Current crowd size                   │                   │
│  │  • Energy per person                    │                   │
│  └─────────────────────────────────────────┘                   │
│         │                                                         │
│         ↓                                                         │
│  ┌─────────────────────────────────────────┐                   │
│  │  Correlation Analysis                   │                   │
│  │  • Audio vs crowd energy match          │                   │
│  │  • Beat vs movement sync                │                   │
│  │  • Music vs mood alignment              │                   │
│  └─────────────────────────────────────────┘                   │
│         │                                                         │
│         ↓                                                         │
│  ┌─────────────────────────────────────────┐                   │
│  │  MCP Data Feed                          │                   │
│  │  JSON structure for LLM consumption     │                   │
│  └─────────────────────────────────────────┘                   │
│         │                                                         │
│         ↓                                                         │
│  ┌─────────────────────────────────────────┐                   │
│  │  LLM (Claude via MCP)                   │                   │
│  │  Determines: Is this acceptable?        │                   │
│  │  • Quality score                        │                   │
│  │  • Issues & warnings                    │                   │
│  │  • Recommended actions                  │                   │
│  └─────────────────────────────────────────┘                   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Features Extracted from 1-Second Audio Clips

### 1. Amplitude Features
- **RMS Energy**: Overall loudness/energy level
- **Peak Amplitude**: Maximum sample value
- **Dynamic Range**: Difference between loudest and quietest parts (dB)

### 2. Frequency Features
- **Spectral Centroid**: "Brightness" of sound (center of mass of spectrum)
- **Spectral Bandwidth**: Width of frequency spectrum
- **Spectral Rolloff**: Frequency below which 85% of energy is contained
- **Zero Crossing Rate**: Measure of noisiness/percussiveness

### 3. Rhythm Features
- **Tempo Estimation**: Estimated BPM (limited accuracy for 1-second clips)
- **Beat Strength**: Strength of rhythmic content

### 4. Quality Indicators
- **Clipping Detection**: Audio distortion from over-amplification
- **Silence Ratio**: Percentage of clip that is silent
- **Noise Floor**: Background noise level

### 5. Content Analysis
- **Harmonic Ratio**: Musical/tonal content vs noise
- **Percussive Ratio**: Beat/rhythm content

### 6. People Context
- **People Count**: Number of people in the system
- **Energy per Person**: Audio energy normalized by crowd size

## MCP Tools

### 1. `analyze_audio_clip`

Analyzes a 1-second audio clip with full metrics.

**Input:**
```json
{
  "use_mock_data": true  // Use simulated audio for testing
}
```

**Output:**
```json
{
  "timestamp": "2025-11-15T10:30:45.123456",
  "duration": 1.0,
  "amplitude": {
    "rms_energy": 0.234,
    "peak_amplitude": 0.678,
    "dynamic_range_db": 12.5
  },
  "frequency": {
    "spectral_centroid_hz": 1250.5,
    "spectral_bandwidth_hz": 850.3,
    "spectral_rolloff_hz": 3200.8,
    "zero_crossing_rate": 0.145
  },
  "rhythm": {
    "estimated_tempo_bpm": 128.0,
    "beat_strength": 0.456
  },
  "quality": {
    "clipping_detected": false,
    "silence_ratio": 0.02,
    "noise_floor": 0.015
  },
  "content": {
    "harmonic_ratio": 0.65,
    "percussive_ratio": 0.35
  },
  "context": {
    "people_count": 42,
    "energy_per_person": 0.005571
  },
  "crowd_context": {
    "energy_level": 75,
    "dominant_mood": "excited",
    "noise_db": 85,
    "movement_intensity": 70
  },
  "correlation_analysis": {
    "energy_correlation": "good",
    "beat_movement_sync": "synchronized",
    "mood_music_alignment": "aligned",
    "observations": [
      "Audio energy matches crowd energy well",
      "Strong beat matches high crowd movement - good sync"
    ],
    "overall_match": "good"
  },
  "acceptability_indicators": {
    "quality_score": 95.0,
    "issues": [],
    "warnings": [],
    "acceptable": true,
    "recommendation": "ACCEPTABLE: Good audio quality (score: 95.0/100)"
  }
}
```

### 2. `get_audio_acceptability_check`

Returns LLM-ready decision framework.

**Output:**
```json
{
  "audio_analysis": { /* full analysis from above */ },
  "decision_framework": {
    "is_acceptable": true,
    "quality_score": 95.0,
    "critical_issues": [],
    "warnings": [],
    "crowd_match": "good",
    "recommendation": "ACCEPTABLE: Good audio quality (score: 95.0/100)"
  },
  "llm_guidance": {
    "should_keep_playing": true,
    "suggested_actions": [
      "CONTINUE: Audio is acceptable and matches crowd"
    ],
    "reasoning_points": [
      "Harmonic ratio: 0.65 (musical content)",
      "Percussive ratio: 0.35 (rhythm/beats)",
      "Audio energy per person: 0.0056",
      "Current crowd: 42 people"
    ]
  },
  "timestamp": "2025-11-15T10:30:45.123456"
}
```

## Usage Examples

### Python API

```python
from src.sensors.audio_clip_processor import AudioClipProcessor
import numpy as np

# Create processor
processor = AudioClipProcessor(sample_rate=22050)

# Process a 1-second audio clip
audio_data = np.random.randn(22050)  # Your audio data
people_count = 42

metrics = processor.process_clip(audio_data, people_count)

# Convert to dict for JSON/MCP
result = processor.metrics_to_dict(metrics)

# Check if acceptable
if result['acceptability_indicators']['acceptable']:
    print("Audio is acceptable!")
else:
    print("Issues:", result['acceptability_indicators']['issues'])
```

### Real-time Buffering

```python
from src.sensors.audio_clip_processor import AudioClipBuffer

# Create buffer for continuous audio
buffer = AudioClipBuffer(sample_rate=22050)

# As audio comes in (e.g., from microphone)
while True:
    chunk = get_audio_chunk()  # Your audio input
    buffer.add_samples(chunk)

    # Process current 1-second window
    result = buffer.process_current_clip(people_count=42)

    # Send to MCP/LLM for decision
    if not result['acceptability_indicators']['acceptable']:
        take_action()
```

### MCP Integration (via Claude)

```python
# In your Claude prompt/conversation:
"""
You are monitoring a live event. Use the audio analysis tools to ensure
audio quality is acceptable.

Check the current audio and tell me if we should continue playing or
if there are any issues.
"""

# Claude will call:
result = await get_audio_acceptability_check()

# And respond based on:
# - result['decision_framework']['is_acceptable']
# - result['llm_guidance']['suggested_actions']
# - result['llm_guidance']['reasoning_points']
```

## Acceptability Criteria

The system automatically evaluates audio acceptability based on:

### Critical Issues (score -30 points)
- ❌ **Clipping detected**: Audio distortion

### Major Warnings (score -15 points)
- ⚠️ **Mostly silent**: >80% silence in clip
- ⚠️ **Low dynamic range**: <6 dB (possible compression issues)

### Minor Warnings (score -10 points)
- ⚠️ **Very quiet**: RMS < 0.01
- ⚠️ **Very loud**: RMS > 0.9
- ⚠️ **High noise**: Zero crossing rate > 0.3
- ⚠️ **Unclear content**: Low harmonic and percussive ratios

### People Context Issues
- ⚠️ **Too loud for crowd**: Energy per person > 0.1
- ⚠️ **Too quiet for crowd**: Energy per person < 0.001 (with >10 people)
- ⚠️ **No people**: Audio playing but crowd is empty

### Correlation Checks
- Audio energy vs crowd energy
- Beat strength vs crowd movement
- Musical content vs crowd mood

## Testing

Run the test suite:

```bash
python examples/test_audio_clip_analysis.py
```

This will demonstrate:
1. Basic audio clip processing
2. MCP tool integration
3. LLM-ready acceptability checks
4. Real-time buffer simulation

## Integration Points

### 1. Real Audio Input
Replace mock data with actual audio:

```python
import pyaudio

# Set up audio stream
p = pyaudio.PyAudio()
stream = p.open(
    format=pyaudio.paFloat32,
    channels=1,
    rate=22050,
    input=True,
    frames_per_buffer=2048
)

# Read and process
while True:
    audio_chunk = np.frombuffer(
        stream.read(2048),
        dtype=np.float32
    )
    buffer.add_samples(audio_chunk)
```

### 2. Live Crowd Detection
Connect to your crowd detection system:

```python
from src.sensors.crowd import get_people_count

people_count = get_people_count()  # Your implementation
result = buffer.process_current_clip(people_count)
```

### 3. MCP Server
The tools are already registered in `src/mcp_server/server.py`:
- `analyze_audio_clip`
- `get_audio_acceptability_check`

Start the MCP server:
```bash
python src/mcp_server/server.py
```

### 4. Claude Integration
Claude can now call these tools via MCP to make decisions about audio acceptability.

## Performance Considerations

- **Processing time**: ~50-100ms per 1-second clip
- **Memory**: ~200KB per clip
- **CPU**: Moderate (FFT operations)
- **Recommended**: Process every 0.5-1 seconds for real-time monitoring

## Dependencies

- `numpy`: Array operations
- `librosa`: Audio feature extraction
- `scipy`: Signal processing (via librosa)

## Future Enhancements

- [ ] Multi-channel audio support
- [ ] Longer time window analysis (5-10 seconds)
- [ ] ML-based music genre classification
- [ ] Beat tracking and tempo following
- [ ] Voice/music separation
- [ ] Real-time audio fingerprinting
- [ ] Adaptive quality thresholds
- [ ] Historical trend analysis
