"""
MCP Server Implementation for AI DJ
Exposes real-time crowd context to Claude via Model Context Protocol
"""

import asyncio
import json
from typing import Any
from datetime import datetime

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    INVALID_PARAMS,
    INTERNAL_ERROR,
)

from .tools import (
    get_crowd_energy,
    get_crowd_mood,
    get_noise_level,
    get_movement_intensity,
    get_crowd_density,
    get_time_context,
    get_full_context,
)


class AIDJMCPServer:
    """MCP Server for AI DJ application"""

    def __init__(self):
        self.server = Server("ai-dj-mcp")
        self.setup_handlers()

    def setup_handlers(self):
        """Register all MCP protocol handlers"""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available tools for crowd analysis"""
            return [
                Tool(
                    name="get_crowd_energy",
                    description="Get current crowd energy level (0-100). "
                    "Higher values indicate more energetic crowd. "
                    "Use this to determine if energy is building, maintaining, or dropping.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "time_window": {
                                "type": "number",
                                "description": "Time window in seconds to average over (default: 5)",
                                "default": 5,
                            }
                        },
                    },
                ),
                Tool(
                    name="get_crowd_mood",
                    description="Analyze dominant mood/emotions of the crowd. "
                    "Returns distribution of emotions: happy, excited, neutral, bored, confused. "
                    "Use this to understand crowd sentiment.",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                    },
                ),
                Tool(
                    name="get_noise_level",
                    description="Get current noise level in decibels (dB). "
                    "Higher values indicate more crowd engagement (cheering, singing). "
                    "Typical range: 60-100 dB.",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                    },
                ),
                Tool(
                    name="get_movement_intensity",
                    description="Get crowd movement/dancing intensity (0-100). "
                    "Higher values indicate more people dancing and moving. "
                    "Use this to gauge physical engagement.",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                    },
                ),
                Tool(
                    name="get_crowd_density",
                    description="Get number of people detected and crowd density. "
                    "Returns people count and density rating (sparse/moderate/packed). "
                    "Use this for context about venue capacity.",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                    },
                ),
                Tool(
                    name="get_time_context",
                    description="Get temporal context: time of day, time in set, event duration. "
                    "Use this to make time-appropriate decisions (opening vs peak vs closing).",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                    },
                ),
                Tool(
                    name="get_full_context",
                    description="Get complete crowd context snapshot with all metrics. "
                    "Returns energy, mood, noise, movement, density, and time context. "
                    "Use this for comprehensive analysis.",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                    },
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[TextContent]:
            """Execute tool calls"""
            try:
                if name == "get_crowd_energy":
                    time_window = arguments.get("time_window", 5)
                    result = await get_crowd_energy(time_window)
                elif name == "get_crowd_mood":
                    result = await get_crowd_mood()
                elif name == "get_noise_level":
                    result = await get_noise_level()
                elif name == "get_movement_intensity":
                    result = await get_movement_intensity()
                elif name == "get_crowd_density":
                    result = await get_crowd_density()
                elif name == "get_time_context":
                    result = await get_time_context()
                elif name == "get_full_context":
                    result = await get_full_context()
                else:
                    raise ValueError(f"Unknown tool: {name}")

                return [
                    TextContent(
                        type="text",
                        text=json.dumps(result, indent=2),
                    )
                ]
            except Exception as e:
                return [
                    TextContent(
                        type="text",
                        text=json.dumps({"error": str(e), "tool": name}),
                    )
                ]

        @self.server.list_resources()
        async def list_resources() -> list[Any]:
            """List available resources"""
            return [
                {
                    "uri": "crowd://current",
                    "name": "Current Crowd State",
                    "description": "Real-time snapshot of all crowd metrics",
                    "mimeType": "application/json",
                },
                {
                    "uri": "music://history",
                    "name": "Music History",
                    "description": "Recently played tracks and crowd response",
                    "mimeType": "application/json",
                },
                {
                    "uri": "venue://info",
                    "name": "Venue Information",
                    "description": "Venue metadata and configuration",
                    "mimeType": "application/json",
                },
            ]

        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            """Read resource content"""
            if uri == "crowd://current":
                context = await get_full_context()
                return json.dumps(context, indent=2)
            elif uri == "music://history":
                # TODO: Implement music history tracking
                return json.dumps(
                    {
                        "recent_tracks": [],
                        "message": "Music history not yet implemented",
                    }
                )
            elif uri == "venue://info":
                return json.dumps(
                    {
                        "name": "AI DJ Venue",
                        "capacity": 200,
                        "type": "nightclub",
                        "acoustics": "good",
                    }
                )
            else:
                raise ValueError(f"Unknown resource: {uri}")

        @self.server.list_prompts()
        async def list_prompts() -> list[Any]:
            """List available prompt templates"""
            return [
                {
                    "name": "high_energy_needed",
                    "description": "Crowd energy is dropping, need an energy boost",
                },
                {
                    "name": "peak_time",
                    "description": "Peak time of the event, maximize energy",
                },
                {
                    "name": "opening_set",
                    "description": "Opening the set, warm up the crowd",
                },
                {
                    "name": "closing_set",
                    "description": "Closing the event, cool down gradually",
                },
            ]

        @self.server.get_prompt()
        async def get_prompt(name: str, arguments: Any) -> str:
            """Get prompt content"""
            prompts = {
                "high_energy_needed": (
                    "The crowd energy is dropping below 50. "
                    "Recommend a track that will boost energy and re-engage the crowd. "
                    "Consider using familiar, high-energy tracks."
                ),
                "peak_time": (
                    "This is peak time! Energy is high and the crowd is engaged. "
                    "Maintain or increase energy with your best tracks."
                ),
                "opening_set": (
                    "You're opening the set. The crowd is just arriving. "
                    "Start with moderate energy and build gradually."
                ),
                "closing_set": (
                    "The event is ending soon. Begin cooling down the energy "
                    "while keeping the crowd satisfied."
                ),
            }
            return prompts.get(name, "Unknown prompt")

    async def run(self):
        """Run the MCP server"""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options(),
            )


def main():
    """Entry point for MCP server"""
    server = AIDJMCPServer()
    asyncio.run(server.run())


if __name__ == "__main__":
    main()
