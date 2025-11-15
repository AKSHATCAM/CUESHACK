# AI DJ - Hyper-Personalized MCP Application Architecture

## 🎯 Project Vision

Build a proactive, context-aware AI DJ that reads the crowd's energy in real-time and adapts music selection accordingly. Unlike traditional DJs that rely on past history, this system uses live contextual data through Model Context Protocol (MCP) to make intelligent, personalized decisions.

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     AI DJ Application                        │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              Claude AI (Brain)                        │  │
│  │  - Analyzes crowd context                            │  │
│  │  - Makes music selection decisions                   │  │
│  │  - Adapts to real-time feedback                      │  │
│  └───────────────────────────────────────────────────────┘  │
│                           ↑                                  │
│                    MCP Protocol                              │
│                           ↓                                  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │           MCP Server (Context Provider)               │  │
│  │  ┌─────────────┐ ┌──────────────┐ ┌──────────────┐  │  │
│  │  │ Noise Level │ │  Facial      │ │  Movement    │  │  │
│  │  │  Detector   │ │  Expression  │ │  Tracker     │  │  │
│  │  │             │ │  Analyzer    │ │              │  │  │
│  │  └─────────────┘ └──────────────┘ └──────────────┘  │  │
│  │  ┌─────────────┐ ┌──────────────┐ ┌──────────────┐  │  │
│  │  │ Crowd       │ │  Time/        │ │  Environment │  │  │
│  │  │ Density     │ │  Schedule     │ │  Sensors     │  │  │
│  │  └─────────────┘ └──────────────┘ └──────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
│                           ↓                                  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │         Music Playback Engine                         │  │
│  │  - Spotify Integration                                │  │
│  │  - Smooth transitions                                 │  │
│  │  - Queue management                                   │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 📊 Data Flow

1. **Data Collection Layer**
   - Sensors continuously collect crowd data
   - Data is processed and normalized
   - Context snapshots are created

2. **MCP Server Layer**
   - Aggregates all context data
   - Exposes standardized MCP protocol endpoints
   - Provides real-time context to Claude

3. **AI Decision Layer (Claude)**
   - Receives context via MCP
   - Analyzes crowd energy and mood
   - Generates music recommendations
   - Provides reasoning for decisions

4. **Execution Layer**
   - Executes music selection
   - Monitors crowd response
   - Feeds back into the context loop

## 🎵 Core Components

### 1. MCP Server Implementation

**Purpose**: Provide real-time crowd context to Claude

**Key Features**:
- **Tools**: Methods Claude can call to get specific data
  - `get_crowd_energy()` - Overall energy level (0-100)
  - `get_crowd_mood()` - Emotional analysis from faces
  - `get_noise_level()` - Current audio level in dB
  - `get_movement_intensity()` - Dance/movement activity
  - `get_crowd_density()` - Number of people detected
  - `get_time_context()` - Time of day, event duration

- **Resources**: Contextual data sources
  - Current playlist history
  - Venue information
  - Music library metadata

- **Prompts**: Pre-built scenarios for Claude
  - "High energy transition needed"
  - "Crowd energy is dropping"
  - "New crowd arriving"

### 2. Real-Time Data Collection Modules

#### A. Noise Level Detector
- **Technology**: PyAudio / Web Audio API
- **Metrics**:
  - Peak dB levels
  - Average noise over time windows
  - Cheering/singing detection
- **Update Frequency**: Every 1-2 seconds

#### B. Facial Expression Analyzer
- **Technology**: OpenCV + DeepFace / face-api.js
- **Metrics**:
  - Happiness, excitement, boredom, confusion
  - Aggregate mood score
  - Trend analysis (improving vs declining)
- **Update Frequency**: Every 3-5 seconds
- **Privacy**: Local processing, no image storage

#### C. Movement Tracker
- **Technology**: OpenCV optical flow / MediaPipe
- **Metrics**:
  - Movement intensity (0-100)
  - Number of people dancing
  - Synchronized movement detection
- **Update Frequency**: Every 2-3 seconds

#### D. Crowd Density Analyzer
- **Technology**: YOLO / OpenCV person detection
- **Metrics**:
  - Total people count
  - Distribution across venue
  - Entry/exit flow
- **Update Frequency**: Every 5 seconds

### 3. Claude Integration

**Approach**: Use Claude with MCP context to make intelligent decisions

**Prompt Engineering**:
```
You are an expert DJ at a live event. Your goal is to keep the crowd
energized and engaged. You have access to real-time crowd data through
your MCP tools.

Current Context:
- Crowd Energy: {energy_level}/100
- Dominant Mood: {mood}
- Movement Intensity: {movement}/100
- Noise Level: {noise_db} dB
- Time in Set: {duration} minutes

Based on this context, recommend the next track and explain your reasoning.
Consider:
- Energy transitions (gradual vs. sudden)
- Genre mixing
- Crowd familiarity vs. discovery
- Peak time management
```

### 4. Music Selection Engine

**Capabilities**:
- Genre-based selection
- BPM matching for smooth transitions
- Energy level matching
- Contextual awareness (time, crowd type)

**Integration Options**:
- Spotify API (primary)
- Local music library (backup)
- SoundCloud API (optional)

### 5. Monitoring Dashboard

**Real-Time Visualizations**:
- Live crowd energy graph
- Mood distribution pie chart
- Movement intensity heatmap
- Audio waveform and dB levels
- Claude's decision reasoning display

**Controls**:
- Manual override capability
- Genre preferences
- Energy target adjustment
- Emergency playlist activation

## 🔧 Technology Stack

### Backend
- **Language**: Python 3.11+
- **MCP Framework**: `mcp` Python SDK
- **AI Integration**: Anthropic Claude API
- **Music APIs**: Spotify Web API, spotipy
- **Computer Vision**: OpenCV, MediaPipe, DeepFace
- **Audio Processing**: PyAudio, librosa
- **Web Framework**: FastAPI (for dashboard API)

### Frontend (Dashboard)
- **Framework**: React + TypeScript
- **Visualization**: D3.js, Chart.js
- **Real-time Updates**: WebSocket
- **UI Library**: Tailwind CSS + shadcn/ui

### Infrastructure
- **Camera Input**: USB webcams / IP cameras
- **Microphone**: USB audio interface
- **Processing**: Local GPU recommended for CV
- **Deployment**: Docker containers

## 📋 Implementation Phases

### Phase 1: Foundation (Week 1-2)
- [ ] Set up project structure
- [ ] Implement basic MCP server
- [ ] Create mock data generators
- [ ] Build Claude integration
- [ ] Test MCP ↔ Claude communication

### Phase 2: Data Collection (Week 3-4)
- [ ] Implement noise level detection
- [ ] Build facial expression analyzer
- [ ] Create movement tracking system
- [ ] Integrate crowd density detection
- [ ] Test all sensors with live camera feed

### Phase 3: AI Logic (Week 5-6)
- [ ] Design DJ decision-making prompts
- [ ] Implement music selection algorithms
- [ ] Build transition logic
- [ ] Create feedback loop system
- [ ] Test with simulated scenarios

### Phase 4: Music Integration (Week 7-8)
- [ ] Spotify API integration
- [ ] Build music database/indexing
- [ ] Implement playlist management
- [ ] Create smooth transition engine
- [ ] Audio playback testing

### Phase 5: Dashboard & Polish (Week 9-10)
- [ ] Build real-time monitoring dashboard
- [ ] Implement control interface
- [ ] Add manual override features
- [ ] Create visualization components
- [ ] End-to-end testing

### Phase 6: Live Testing & Refinement (Week 11-12)
- [ ] Small venue testing
- [ ] Gather feedback and iterate
- [ ] Performance optimization
- [ ] Documentation
- [ ] Demo preparation

## 🎯 Success Metrics

1. **Response Time**: Context → Decision < 2 seconds
2. **Accuracy**: Crowd mood prediction vs. manual DJ assessment
3. **Engagement**: Sustained high energy levels (>70/100)
4. **Smoothness**: Seamless music transitions
5. **User Satisfaction**: Post-event surveys

## 🔐 Privacy & Ethics

- All facial analysis processed locally
- No image/video storage
- Anonymized aggregate data only
- Clear signage about AI DJ system
- Manual override always available
- Opt-out zones for privacy-conscious attendees

## 🚀 Future Enhancements

- Multi-room support with different contexts
- Voice command integration
- Predictive crowd behavior modeling
- Integration with social media sentiment
- Collaborative filtering with crowd preferences
- Genre discovery based on micro-expressions
- Integration with lighting and visual effects

## 📝 Notes

- Start with simulated data to test the full pipeline
- Gradually introduce real sensors
- Maintain human DJ oversight initially
- Build trust with gradual automation
- Focus on augmenting human DJs, not replacing them
