# AI DJ Quick Start Guide

Get up and running with the AI DJ application in minutes!

## 🚀 5-Minute Demo (No Hardware Required)

Want to see it in action without setting up cameras and microphones? Start with mock data:

### Step 1: Clone and Setup

```bash
# Navigate to the project
cd CUESHACK

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your Anthropic API key
# You only need ANTHROPIC_API_KEY for the basic demo
nano .env  # or use your preferred editor
```

Add this line to `.env`:
```
ANTHROPIC_API_KEY=your_key_here
ENABLE_MOCK_DATA=true
```

### Step 3: Test the MCP Server

```bash
# Run the mock data simulator
python src/sensors/mock.py
```

You should see simulated crowd data being generated!

### Step 4: Test MCP Tools

```bash
# Test the MCP server (in another terminal)
python -m src.mcp_server.server
```

The MCP server is now running and ready to provide crowd context to Claude!

## 📋 What You've Built So Far

### ✅ Architecture & Planning
- **ARCHITECTURE.md** - Complete system design
- **IMPLEMENTATION_PLAN.md** - 15-day implementation roadmap
- **README.md** - Project overview and documentation

### ✅ MCP Server Foundation
- **src/mcp_server/server.py** - Full MCP server implementation
- **src/mcp_server/tools.py** - 7 MCP tools for crowd analysis
  - `get_crowd_energy()` - Energy level 0-100
  - `get_crowd_mood()` - Emotional analysis
  - `get_noise_level()` - Audio levels in dB
  - `get_movement_intensity()` - Dancing intensity
  - `get_crowd_density()` - People count
  - `get_time_context()` - Temporal information
  - `get_full_context()` - Complete snapshot

### ✅ Mock Data System
- **src/sensors/mock.py** - Realistic crowd simulation
  - Simulates 2-hour DJ set progression
  - Energy builds and peaks naturally
  - Correlated metrics (noise, mood, movement)
  - Random events and variations

### ✅ AI Prompt System
- **src/ai/prompts.py** - Professional DJ prompts for Claude
  - System prompt defining DJ expertise
  - Context-aware prompt selection
  - Emergency, peak, opening, closing scenarios
  - Genre transition guidance

## 🎯 Next Steps

### Option A: Complete the MVP (Recommended)
Follow the 3-day MVP plan in IMPLEMENTATION_PLAN.md:

1. **Connect Claude to MCP** (Day 1)
   - Implement `src/ai/client.py`
   - Test MCP ↔ Claude communication
   - Get AI recommendations based on mock data

2. **Add Music Integration** (Day 2)
   - Implement `src/music/spotify.py`
   - Track selection based on AI recommendations
   - Test playback

3. **Build Simple Dashboard** (Day 3)
   - Create real-time monitoring interface
   - Visualize crowd energy
   - Display AI decision reasoning

### Option B: Add Real Sensors
Implement actual hardware sensing:

1. **Audio Detection**
   ```bash
   pip install pyaudio
   python src/sensors/audio.py
   ```

2. **Computer Vision**
   ```bash
   pip install opencv-python deepface
   python src/sensors/vision.py
   ```

### Option C: Full Implementation
Follow the complete 15-day plan in IMPLEMENTATION_PLAN.md

## 🧪 Testing the System

### Test Mock Data Generator
```bash
python src/sensors/mock.py
```

Expected output:
```
Mock Crowd Simulator Test
==================================================

Minute 0.0:
  Energy: 42.3 (rising)
  Mood: neutral
  Noise: 68.5 dB
  Movement: 38.2
  Crowd: 65 people

Minute 0.5:
  Energy: 45.7 (rising)
  Mood: happy
  ...
```

### Test MCP Server Tools
```python
# In Python
from src.mcp_server.tools import get_full_context
import asyncio

context = asyncio.run(get_full_context())
print(context)
```

Expected output:
```json
{
  "energy": {
    "energy": 67.3,
    "trend": "rising",
    "interpretation": "Moderate - good baseline energy"
  },
  "mood": {
    "dominant_emotion": "happy",
    "mood_distribution": {...}
  },
  ...
}
```

## 🎮 How the System Works

```
┌─────────────────────────────────────┐
│  1. Sensors Collect Data            │
│     (Currently: Mock Simulator)     │
│     - Energy, mood, movement, etc.  │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  2. MCP Server Provides Context     │
│     - Normalizes data               │
│     - Exposes tools to Claude       │
│     - get_crowd_energy()            │
│     - get_crowd_mood()              │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  3. Claude Analyzes & Decides       │
│     - Calls MCP tools               │
│     - Understands crowd context     │
│     - Recommends next track         │
│     - Explains reasoning            │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  4. Music Plays                     │
│     (Next: Spotify integration)     │
│     - Track selected and queued     │
│     - Smooth transition executed    │
└──────────────┬──────────────────────┘
               │
               ▼ (feedback loop)
┌─────────────────────────────────────┐
│  5. Monitor Crowd Response          │
│     - Energy changes tracked        │
│     - System adapts in real-time    │
└─────────────────────────────────────┘
```

## 📖 Key Files Explained

### MCP Server (`src/mcp_server/`)
- **server.py** - Main MCP server, handles protocol communication
- **tools.py** - Implements all MCP tools that Claude can call

### Sensors (`src/sensors/`)
- **mock.py** - ✅ DONE - Simulates realistic crowd behavior
- **audio.py** - TODO - Real microphone noise detection
- **vision.py** - TODO - Camera-based facial expressions & movement
- **aggregator.py** - TODO - Combines all sensor data

### AI (`src/ai/`)
- **prompts.py** - ✅ DONE - DJ prompts for Claude
- **client.py** - TODO - Claude API client with MCP
- **decision.py** - TODO - Decision-making logic

### Music (`src/music/`)
- **spotify.py** - TODO - Spotify API integration
- **selector.py** - TODO - Track selection algorithm
- **transition.py** - TODO - Smooth transitions

## 🔍 Understanding MCP

The Model Context Protocol (MCP) is the secret sauce that makes this work:

### What is MCP?
- A standard protocol for providing context to AI models
- Like an API that your AI can call to get real-time information
- Much better than embedding static data in prompts

### Why Use MCP?
- **Real-time**: Data is always current, not stale
- **Structured**: Well-defined tools and resources
- **Efficient**: Only fetch what's needed, when needed
- **Scalable**: Easy to add new data sources

### MCP in AI DJ
Instead of telling Claude "the energy is 75", we give it tools:
- Claude can call `get_crowd_energy()` whenever it needs to check
- Data is always live and accurate
- Claude can query specific aspects (just mood, just movement, etc.)

## 🎨 Customization

### Adjust Crowd Simulation
Edit `src/sensors/mock.py`:
```python
class MockCrowdSimulator:
    def __init__(self):
        self.start_time = time.time()
        self.base_energy = 50.0  # Starting energy
        self.time_scale = 1.0    # Speed up/slow down simulation
```

### Modify DJ Personality
Edit `src/ai/prompts.py`:
```python
DJ_SYSTEM_PROMPT = """You are an expert DJ...
# Add your own DJ style and preferences here
"""
```

### Change Energy Thresholds
Edit `.env`:
```
ENERGY_THRESHOLD_HIGH=75  # When to trigger peak mode
ENERGY_THRESHOLD_LOW=40   # When to boost energy
```

## 🐛 Troubleshooting

### Issue: MCP server won't start
```bash
# Check Python version (need 3.11+)
python --version

# Reinstall MCP
pip install --upgrade mcp
```

### Issue: Mock data not generating
```bash
# Run with debug output
python -c "from src.sensors.mock import MockCrowdSimulator; s = MockCrowdSimulator(); print(s.get_current_state())"
```

### Issue: Import errors
```bash
# Make sure you're in the project root
pwd  # Should show /path/to/CUESHACK

# Ensure virtual environment is activated
which python  # Should show venv/bin/python
```

## 📚 Learn More

- **MCP Documentation**: https://modelcontextprotocol.io/
- **Anthropic Claude**: https://docs.anthropic.com/
- **Full Architecture**: See `ARCHITECTURE.md`
- **Implementation Plan**: See `IMPLEMENTATION_PLAN.md`

## 🎯 Success Criteria

You'll know it's working when:
- ✅ Mock crowd simulator generates realistic data
- ✅ MCP server starts without errors
- ✅ MCP tools return crowd context
- ⏳ Claude receives context and makes recommendations (next step)
- ⏳ Music plays based on AI decisions (next step)
- ⏳ Dashboard shows real-time visualizations (next step)

## 🚀 Ready for More?

Once you've verified the basics work, move on to:
1. **Implement Claude Integration** - See `IMPLEMENTATION_PLAN.md` Day 2
2. **Add Music Playback** - See `IMPLEMENTATION_PLAN.md` Day 8-10
3. **Build Dashboard** - See `IMPLEMENTATION_PLAN.md` Day 11-13
4. **Add Real Sensors** - See `IMPLEMENTATION_PLAN.md` Day 4-7

---

**Questions?** Check the documentation or open an issue!

**Built with ❤️ for CUESHACK Hackathon**
