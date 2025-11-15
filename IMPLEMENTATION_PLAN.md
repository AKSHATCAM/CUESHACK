# AI DJ Implementation Plan

## 📋 Detailed Step-by-Step Implementation

This document provides a concrete, actionable plan for building the AI DJ system.

## Phase 1: Foundation & MCP Server (Days 1-3)

### Day 1: Project Setup & MCP Basics

#### 1.1 Environment Setup
```bash
# Create project structure
mkdir -p src/{mcp_server,sensors,ai,music,utils}
mkdir -p tests/{unit,integration}
mkdir -p dashboard/src/{components,hooks,utils}
mkdir -p docs

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install core dependencies
pip install anthropic mcp fastapi uvicorn python-dotenv
```

#### 1.2 Basic MCP Server
**File**: `src/mcp_server/server.py`

Key components:
- Initialize MCP server instance
- Define server capabilities
- Set up stdio transport
- Implement basic health check

**File**: `src/mcp_server/tools.py`

Initial tools to implement:
- `get_crowd_energy()` - Returns energy level 0-100
- `get_crowd_mood()` - Returns dominant emotion
- `get_current_context()` - Returns full context snapshot

**File**: `src/mcp_server/resources.py`

Resources to expose:
- `crowd://current` - Current crowd state
- `music://history` - Recently played tracks
- `venue://info` - Venue metadata

#### 1.3 Mock Data Generator
**File**: `src/sensors/mock.py`

Create realistic crowd simulation:
- Energy oscillation (builds and drops)
- Time-based patterns (higher energy at night)
- Random events (sudden energy spikes)
- Realistic mood distributions

**Testing Goal**: MCP server responds to all tool calls with mock data

---

### Day 2: Claude Integration

#### 2.1 Claude Client Setup
**File**: `src/ai/client.py`

Implement:
- Anthropic client initialization
- MCP context injection
- Message streaming
- Error handling and retries

#### 2.2 Prompt Engineering
**File**: `src/ai/prompts.py`

Create prompt templates:
```python
DJ_SYSTEM_PROMPT = """
You are an expert DJ performing at a live event. Your goal is to keep
the crowd energized, engaged, and dancing.

You have access to real-time crowd data through MCP tools:
- get_crowd_energy(): Current energy level (0-100)
- get_crowd_mood(): Dominant emotions
- get_movement_intensity(): How much people are dancing

Your task: Recommend the next track based on context.
Consider:
1. Energy trajectory (building vs. maintaining vs. cooling down)
2. Smooth transitions (BPM, key, genre)
3. Crowd familiarity vs. surprise
4. Time in the set (opening, peak, closing)

Format your response as:
{
  "track_recommendation": "Artist - Song Name",
  "reasoning": "Why this track fits the moment",
  "energy_target": 85,
  "transition_style": "gradual" | "sudden",
  "confidence": 0.95
}
"""
```

#### 2.3 Decision Engine
**File**: `src/ai/decision.py`

Implement decision-making loop:
1. Call MCP tools to get context
2. Send context to Claude with prompt
3. Parse Claude's recommendation
4. Validate and enrich the decision
5. Return track selection

**Testing Goal**: Claude receives MCP context and returns music recommendations

---

### Day 3: Testing & Refinement

#### 3.1 Integration Tests
**File**: `tests/integration/test_mcp_claude.py`

Test scenarios:
- High energy crowd → Upbeat track recommendation
- Dropping energy → Energy-boosting track
- Mixed mood → Crowd-pleasing familiar track
- Late night → Slower, cooler tracks

#### 3.2 MCP Protocol Validation
Verify:
- All tools are callable
- Resources are accessible
- Prompts are available
- Error handling works

#### 3.3 Mock Event Simulation
Create a simulated 2-hour DJ set:
- Opening (low energy, warming up)
- Build-up (gradual increase)
- Peak time (high energy)
- Cool down (gradual decrease)

**Testing Goal**: End-to-end flow works with mock data

---

## Phase 2: Real-Time Sensors (Days 4-7)

### Day 4: Audio Analysis

#### 4.1 Noise Level Detection
**File**: `src/sensors/audio.py`

Implement using PyAudio:
```python
class NoiseDetector:
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.stream = None

    def start_monitoring(self):
        # Open audio stream
        # Calculate RMS (volume)
        # Detect peaks (cheering)
        # Return dB level

    def get_noise_level(self) -> float:
        # Returns 0-100 normalized noise level
        pass
```

Features:
- Real-time dB measurement
- Peak detection (cheering, applause)
- Background noise filtering
- Smoothing over time windows

#### 4.2 Audio Feature Extraction
Optional advanced features:
- Frequency analysis (bass vs. treble response)
- Singing detection
- Clapping rhythm detection

**Testing Goal**: Microphone captures and analyzes audio in real-time

---

### Day 5: Computer Vision - Facial Expressions

#### 5.1 Face Detection & Analysis
**File**: `src/sensors/vision.py`

Implement using OpenCV + DeepFace:
```python
class FacialExpressionAnalyzer:
    def __init__(self):
        self.detector = DeepFace

    def analyze_frame(self, frame):
        # Detect all faces
        # Analyze each face for emotion
        # Aggregate emotions
        # Return mood distribution

    def get_crowd_mood(self) -> dict:
        # Returns: {
        #   "happy": 0.6,
        #   "excited": 0.2,
        #   "neutral": 0.15,
        #   "bored": 0.05
        # }
        pass
```

Features:
- Multi-face detection
- Emotion classification (7 basic emotions)
- Aggregate mood calculation
- Trend analysis (mood improving vs. declining)

#### 5.2 Privacy Protection
Implement:
- Local processing only
- No frame storage
- Face blurring in debug mode
- Aggregated data only

**Testing Goal**: Webcam detects faces and analyzes emotions

---

### Day 6: Computer Vision - Movement Tracking

#### 6.1 Motion Detection
**File**: `src/sensors/movement.py`

Implement using OpenCV optical flow:
```python
class MovementTracker:
    def __init__(self):
        self.prev_frame = None

    def calculate_movement(self, frame):
        # Optical flow calculation
        # Movement magnitude
        # Direction analysis
        # Return intensity 0-100

    def get_movement_intensity(self) -> float:
        pass
```

Features:
- Overall movement intensity
- Dancing vs. walking detection
- Synchronized movement (everyone dancing together)
- Crowd density estimation

#### 6.2 Advanced Movement Analysis
Optional features:
- Body pose estimation (MediaPipe)
- Jump detection (high energy moments)
- Crowd synchronization metric

**Testing Goal**: Camera tracks movement and reports intensity

---

### Day 7: Sensor Integration & Calibration

#### 7.1 Sensor Aggregator
**File**: `src/sensors/aggregator.py`

Combine all sensors:
```python
class SensorAggregator:
    def __init__(self):
        self.audio = NoiseDetector()
        self.vision = FacialExpressionAnalyzer()
        self.movement = MovementTracker()

    def get_full_context(self) -> dict:
        return {
            "energy": self.calculate_energy(),
            "mood": self.vision.get_crowd_mood(),
            "movement": self.movement.get_movement_intensity(),
            "noise": self.audio.get_noise_level(),
            "timestamp": time.time()
        }
```

#### 7.2 Calibration System
Implement sensor calibration:
- Baseline noise level for venue
- Camera positioning optimization
- Movement threshold tuning
- Energy calculation formula refinement

**Testing Goal**: All sensors work together providing unified context

---

## Phase 3: Music Integration (Days 8-10)

### Day 8: Spotify Integration

#### 8.1 Spotify API Client
**File**: `src/music/spotify.py`

Implement using spotipy:
```python
class SpotifyClient:
    def __init__(self):
        self.sp = spotipy.Spotify(auth_manager=...)

    def search_track(self, query: str) -> dict:
        # Search for track
        # Return track metadata

    def get_track_features(self, track_id: str) -> dict:
        # Get audio features (BPM, energy, valence)
        # Return features dict

    def play_track(self, track_id: str):
        # Add to queue
        # Start playback
```

Features:
- Track search and metadata
- Audio feature analysis (BPM, energy, key)
- Playlist creation
- Playback control

#### 8.2 Music Database
**File**: `src/music/database.py`

Create local music index:
- Pre-indexed tracks by genre
- BPM ranges
- Energy levels
- Popularity scores

**Testing Goal**: Can search, analyze, and play Spotify tracks

---

### Day 9: Track Selection Engine

#### 9.1 Selection Algorithm
**File**: `src/music/selector.py`

Implement intelligent selection:
```python
class TrackSelector:
    def select_next_track(self, context: dict, current_track: dict) -> dict:
        # Get Claude's recommendation
        # Find matching tracks in database
        # Filter by BPM compatibility
        # Check transition quality
        # Return best match
```

Features:
- Genre-aware selection
- BPM matching (±5 BPM for smooth transitions)
- Key compatibility checking
- Energy trajectory planning

#### 9.2 Transition Engine
**File**: `src/music/transition.py`

Implement smooth transitions:
- Crossfade timing
- BPM alignment
- Energy curve management
- Harmonic mixing (optional)

**Testing Goal**: Smooth, DJ-quality transitions between tracks

---

### Day 10: Playlist Management

#### 10.1 Queue System
Implement smart queueing:
- Next track buffer (always 2-3 tracks ahead)
- Fallback tracks for errors
- Genre diversity management
- Energy pacing

#### 10.2 History Tracking
**File**: `src/music/history.py`

Track what's been played:
- Prevent repeats (within 2 hours)
- Track energy trajectory
- Monitor crowd response per track
- Learn preferences over time

**Testing Goal**: Full music playback system operational

---

## Phase 4: Dashboard (Days 11-13)

### Day 11: Backend API

#### 11.1 FastAPI Server
**File**: `src/api/server.py`

Implement REST API:
```python
@app.get("/api/context")
def get_current_context():
    # Return current crowd context

@app.get("/api/track/current")
def get_current_track():
    # Return now playing

@app.ws("/api/ws")
def websocket_endpoint(websocket: WebSocket):
    # Real-time updates
```

Endpoints:
- `/api/context` - Current crowd data
- `/api/track/current` - Now playing
- `/api/track/history` - Recent tracks
- `/api/control/override` - Manual control
- `/ws` - WebSocket for real-time updates

#### 11.2 WebSocket Streaming
Push real-time updates:
- Crowd energy (every 2 seconds)
- Track changes
- Claude decision reasoning

**Testing Goal**: API serves all necessary data

---

### Day 12: Frontend Dashboard

#### 12.1 React Setup
**File**: `dashboard/src/App.tsx`

Key components:
- `EnergyGraph` - Live energy visualization
- `MoodDisplay` - Emotion pie chart
- `MovementHeatmap` - Activity visualization
- `NowPlaying` - Current track display
- `ControlPanel` - Manual overrides

#### 12.2 Real-Time Visualization
Implement using Chart.js:
- Scrolling energy graph
- Mood distribution chart
- Movement intensity meter
- Audio waveform display

**Testing Goal**: Dashboard shows live data

---

### Day 13: Controls & Polish

#### 13.1 Manual Controls
Implement:
- Emergency stop
- Skip track
- Energy target adjustment
- Genre preference sliders
- Fallback playlist activation

#### 13.2 Claude Reasoning Display
Show Claude's thought process:
- Why track was selected
- Context analysis
- Confidence level
- Alternative options considered

**Testing Goal**: Fully functional monitoring and control interface

---

## Phase 5: Integration & Testing (Days 14-15)

### Day 14: End-to-End Integration

#### 14.1 Full System Test
Run complete pipeline:
1. Sensors collect data
2. MCP server provides context
3. Claude makes decisions
4. Music plays
5. Dashboard updates
6. Feedback loop continues

#### 14.2 Performance Optimization
- Reduce latency (target < 2 seconds per decision)
- Optimize computer vision (GPU acceleration)
- Efficient MCP communication
- Dashboard rendering optimization

#### 14.3 Error Handling
Implement robust error recovery:
- Sensor failures (fallback to mock data)
- API timeouts (retry logic)
- Spotify errors (fallback tracks)
- Network issues (local queue buffer)

**Testing Goal**: System runs reliably for 2+ hours

---

### Day 15: Live Testing & Refinement

#### 15.1 Simulated Event Testing
Run realistic simulations:
- Various crowd sizes
- Different energy patterns
- Edge cases (empty venue, packed venue)
- Rapid mood changes

#### 15.2 Calibration & Tuning
Fine-tune parameters:
- Energy calculation weights
- Mood thresholds
- Transition timing
- Claude prompt adjustments

#### 15.3 Documentation
Complete documentation:
- API documentation
- Setup guide
- Troubleshooting guide
- Demo video

**Testing Goal**: Production-ready system

---

## 🎯 Success Criteria

### Technical Metrics
- [ ] MCP server responds < 100ms
- [ ] Claude decision time < 2 seconds
- [ ] Sensor update frequency: 1-3 seconds
- [ ] Smooth music transitions (no gaps)
- [ ] Dashboard latency < 500ms
- [ ] 99% uptime over 2-hour session

### Functional Requirements
- [ ] Detects crowd energy accurately
- [ ] Selects appropriate music
- [ ] Adapts to changing context
- [ ] Provides explainable decisions
- [ ] Allows manual override
- [ ] Handles errors gracefully

### User Experience
- [ ] Dashboard is intuitive
- [ ] Reasoning is clear and helpful
- [ ] Music selection feels natural
- [ ] Transitions are smooth
- [ ] System feels "alive" and responsive

---

## 🚀 Quick Start Implementation

### Minimal Viable Product (MVP) - 3 Days

If you need to build a working demo quickly:

**Day 1**: MCP + Claude + Mock Data
- Basic MCP server with 3 tools
- Claude integration
- Mock crowd simulator
- Simple decision logic

**Day 2**: One Real Sensor + Music
- Implement audio noise detection only
- Spotify integration
- Basic track selection
- Playback working

**Day 3**: Simple Dashboard
- Real-time energy graph
- Now playing display
- Basic controls
- Claude reasoning box

This gives you a working demo that showcases the core concept.

---

## 📦 Deliverables Checklist

- [ ] Working MCP server
- [ ] Claude integration with context awareness
- [ ] At least 2 real sensors (audio + vision)
- [ ] Music playback via Spotify
- [ ] Real-time monitoring dashboard
- [ ] Manual control interface
- [ ] Test suite with >80% coverage
- [ ] Documentation (setup, API, architecture)
- [ ] Demo video (3-5 minutes)
- [ ] GitHub repository with CI/CD

---

## 🎓 Learning Resources

### MCP Protocol
- [MCP Documentation](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/anthropics/mcp-python)
- [Example MCP Servers](https://github.com/anthropics/mcp-examples)

### Computer Vision
- OpenCV tutorials
- DeepFace documentation
- MediaPipe guides

### Music APIs
- Spotify Web API reference
- spotipy documentation

### Claude AI
- Anthropic API documentation
- Prompt engineering guide
- Claude best practices

---

This plan provides a structured approach to building the AI DJ system. Adjust timelines based on your experience level and available time. Good luck! 🎵
