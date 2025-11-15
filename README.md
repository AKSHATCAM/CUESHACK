# 🎧 AI DJ - Hyper-Personalized Music with MCP

> A proactive, context-aware AI DJ that reads the crowd's energy in real-time and adapts music selection using Claude AI and Model Context Protocol (MCP).

## 🌟 Concept

Traditional recommendation systems rely on past history. **AI DJ** goes beyond that by understanding the **present context**. Using real-time data from the crowd—noise levels, facial expressions, movement, and more—the system feeds this context to Claude AI via a custom MCP server, enabling truly personalized, moment-by-moment music curation.

## 🎯 What Makes This Special

- **Real-Time Context Awareness**: Analyzes live crowd data, not historical patterns
- **MCP-Powered**: Custom Model Context Protocol server feeds Claude rich, structured data
- **Intelligent Decisions**: Claude acts as the "DJ brain" making informed music choices
- **Hyper-Personalized**: Adapts to the unique energy and mood of each moment
- **Proactive**: Anticipates crowd needs before energy drops

## 🏗️ Architecture

The system consists of three main layers:

1. **Data Collection Layer**: Sensors capturing crowd context
   - Audio analysis (noise levels, cheering)
   - Computer vision (facial expressions, movement)
   - Environmental sensors (density, time)

2. **MCP Server Layer**: Bridges sensors and AI
   - Aggregates and normalizes crowd data
   - Exposes MCP protocol endpoints
   - Provides real-time context to Claude

3. **AI Decision Layer**: Claude-powered intelligence
   - Analyzes crowd energy and mood
   - Selects appropriate music
   - Manages transitions and pacing

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+ (for dashboard)
- Anthropic API key
- Spotify API credentials (for music playback)
- Webcam and microphone (for sensors)

### Installation

```bash
# Clone repository
git clone <repository-url>
cd CUESHACK

# Set up Python environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Run the MCP server
python src/mcp_server/server.py

# In another terminal, run the main application
python src/main.py

# In another terminal, run the dashboard
cd dashboard
npm install
npm run dev
```

### Testing with Mock Data

```bash
# Run with simulated crowd data (no camera required)
python src/main.py --mock-data

# This will simulate a live event with varying crowd energy
```

## 📁 Project Structure

```
CUESHACK/
├── src/
│   ├── mcp_server/           # MCP server implementation
│   │   ├── server.py         # Main MCP server
│   │   ├── tools.py          # MCP tools (get_crowd_energy, etc.)
│   │   ├── resources.py      # MCP resources
│   │   └── prompts.py        # Pre-built MCP prompts
│   ├── sensors/              # Data collection modules
│   │   ├── audio.py          # Noise level detection
│   │   ├── vision.py         # Facial expression & movement
│   │   ├── crowd.py          # Density analysis
│   │   └── mock.py           # Mock data generator
│   ├── ai/                   # Claude integration
│   │   ├── client.py         # Claude API client
│   │   ├── prompts.py        # DJ prompting system
│   │   └── decision.py       # Decision-making logic
│   ├── music/                # Music playback
│   │   ├── spotify.py        # Spotify integration
│   │   ├── selector.py       # Track selection engine
│   │   └── transition.py     # Smooth transitions
│   └── main.py               # Application entry point
├── dashboard/                # React monitoring interface
│   ├── src/
│   │   ├── components/       # UI components
│   │   ├── hooks/            # React hooks
│   │   └── App.tsx           # Main app
│   └── package.json
├── tests/                    # Test suite
├── docs/                     # Documentation
├── ARCHITECTURE.md           # Detailed architecture
├── README.md                 # This file
└── requirements.txt          # Python dependencies
```

## 🎮 How It Works

1. **Sensors Collect Data**: Cameras and microphones capture crowd behavior
2. **MCP Server Processes**: Data is normalized and structured
3. **Claude Analyzes**: AI receives context and makes decisions
4. **Music Plays**: Selected tracks are queued and played
5. **Feedback Loop**: System observes crowd response and adapts

## 🔧 Configuration

Edit `.env` to configure:

```env
# Anthropic API
ANTHROPIC_API_KEY=your_api_key_here

# Spotify API
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret

# Sensor Configuration
CAMERA_INDEX=0
MICROPHONE_INDEX=0
UPDATE_INTERVAL=2  # seconds

# AI Configuration
ENERGY_THRESHOLD=70
TRANSITION_SMOOTHNESS=high
```

## 📊 Dashboard Features

- **Live Energy Graph**: Real-time crowd energy visualization
- **Mood Distribution**: See crowd emotions at a glance
- **Movement Heatmap**: Visualize dancing and activity
- **Claude Reasoning**: Understand why tracks were selected
- **Manual Controls**: Override and adjust on the fly

## 🧪 Development

### Running Tests

```bash
# Run all tests
pytest

# Run specific test suite
pytest tests/test_mcp_server.py

# Run with coverage
pytest --cov=src
```

### Mock Data Generation

For development without hardware:

```python
from src.sensors.mock import MockCrowdSimulator

simulator = MockCrowdSimulator()
data = simulator.generate_realistic_crowd()
# Returns: energy, mood, movement, noise levels
```

## 🎯 Use Cases

- **Live DJ Sets**: Augment human DJs with AI insights
- **Automated Venues**: Unmanned music spaces (gyms, cafes)
- **Events**: Weddings, parties, corporate events
- **Festivals**: Multi-stage coordination
- **Retail**: Dynamic background music

## 🔐 Privacy

- All facial analysis is processed **locally**
- **No images or videos are stored**
- Only aggregate, anonymized data is used
- Clear signage informs attendees
- Opt-out zones available

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details

## 🙏 Acknowledgments

- Anthropic for Claude AI and MCP
- Open source computer vision community
- Music venues for testing feedback

## 📞 Contact

Questions? Open an issue or reach out to the team.

---

**Built with ❤️ for CUESHACK Hackathon**
