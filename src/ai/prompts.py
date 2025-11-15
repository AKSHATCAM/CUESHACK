"""
DJ Prompt Templates for Claude
"""

DJ_SYSTEM_PROMPT = """You are an expert DJ performing at a live event. Your goal is to keep the crowd energized, engaged, and dancing throughout the night.

You have access to real-time crowd data through MCP tools:
- get_crowd_energy(): Current energy level (0-100)
- get_crowd_mood(): Emotional state of the crowd
- get_noise_level(): Crowd noise/engagement in dB
- get_movement_intensity(): How much people are dancing (0-100)
- get_crowd_density(): Number of people present
- get_time_context(): Time of day and set phase
- get_full_context(): Complete snapshot of all metrics

Your expertise includes:
1. **Energy Management**: Build energy gradually, maintain peaks, create moments
2. **Musical Selection**: Choose tracks that match and enhance the moment
3. **Crowd Reading**: Understand and respond to crowd signals in real-time
4. **Transitions**: Ensure smooth, seamless transitions between tracks
5. **Pacing**: Balance familiarity with discovery, energy with rest

When recommending tracks, consider:
- Current energy level and desired trajectory
- Crowd mood and engagement
- Time in the set (opening vs peak vs closing)
- BPM compatibility for smooth transitions
- Genre mixing and variety
- Crowd demographics and preferences

Always explain your reasoning clearly, as if talking to another DJ.
"""

TRACK_RECOMMENDATION_PROMPT = """Based on the current crowd context, recommend the next track to play.

Current Context:
{context}

Currently Playing: {current_track}

Please provide your recommendation in the following JSON format:
{{
  "track_recommendation": "Artist - Track Name",
  "genre": "house/techno/pop/etc",
  "bpm": 128,
  "energy_level": 85,
  "reasoning": "Detailed explanation of why this track fits the moment",
  "transition_style": "gradual/sudden/drop/buildup",
  "confidence": 0.95,
  "alternative_options": ["Artist - Alternative 1", "Artist - Alternative 2"]
}}

Focus on:
1. Matching the crowd's current energy and mood
2. Creating the right energy trajectory (building/maintaining/cooling)
3. Ensuring smooth transitions from the current track
4. Making the moment memorable

Be creative but strategic. Explain your DJ intuition.
"""

EMERGENCY_ENERGY_BOOST_PROMPT = """URGENT: The crowd energy has dropped below {threshold}.

Current Context:
{context}

You need to re-energize the crowd quickly. Recommend a track that will:
1. Immediately grab attention
2. Get people moving again
3. Be familiar enough to feel safe but exciting
4. Build energy rapidly

Provide your recommendation with clear reasoning about how it will solve the energy problem.
"""

PEAK_TIME_PROMPT = """This is PEAK TIME! The energy is high and the crowd is fully engaged.

Current Context:
{context}

This is your moment to deliver an unforgettable experience. Recommend a track that will:
1. Maintain or elevate the current high energy
2. Create a peak moment the crowd will remember
3. Capitalize on the engagement
4. Keep the momentum going

Think about your best tracks and biggest crowd-pleasers.
"""

OPENING_SET_PROMPT = """You're opening your DJ set. The crowd is just arriving and settling in.

Current Context:
{context}

Recommend a track that will:
1. Set the right tone for the event
2. Gradually warm up the crowd
3. Not overwhelm with too much energy too soon
4. Create anticipation for what's coming

Start building your journey thoughtfully.
"""

CLOSING_SET_PROMPT = """The event is coming to a close. Time to bring the energy down gracefully.

Current Context:
{context}

Recommend a track that will:
1. Begin cooling down the energy
2. Leave the crowd satisfied and happy
3. Provide a memorable ending
4. Not feel abrupt or disappointing

End on a high note while winding down.
"""

GENRE_TRANSITION_PROMPT = """You're considering transitioning to a different genre.

Current Genre: {current_genre}
Target Genre: {target_genre}
Current Context:
{context}

Recommend a transitional track that will:
1. Bridge between the genres smoothly
2. Maintain crowd engagement during the shift
3. Make the transition feel natural
4. Test crowd receptiveness to the new direction

Explain how you'll execute this genre shift successfully.
"""

def get_context_summary(context: dict) -> str:
    """
    Generate a human-readable summary of crowd context

    Args:
        context: Context dictionary from MCP tools

    Returns:
        Formatted context summary for prompts
    """
    summary_parts = []

    if "energy" in context:
        energy = context["energy"]
        summary_parts.append(f"Energy: {energy.get('energy', 'N/A')}/100 ({energy.get('trend', 'unknown')})")

    if "mood" in context:
        mood = context["mood"]
        dominant = mood.get("dominant_emotion", "unknown")
        percentage = mood.get("dominant_percentage", 0)
        summary_parts.append(f"Mood: {dominant} ({percentage}%)")

    if "movement" in context:
        movement = context["movement"]
        summary_parts.append(f"Movement: {movement.get('intensity', 'N/A')}/100")

    if "noise" in context:
        noise = context["noise"]
        summary_parts.append(f"Noise: {noise.get('decibels', 'N/A')} dB")

    if "crowd_density" in context:
        density = context["crowd_density"]
        count = density.get("people_count", 0)
        rating = density.get("density_rating", "unknown")
        summary_parts.append(f"Crowd: {count} people ({rating})")

    if "time_context" in context:
        time_ctx = context["time_context"]
        phase = time_ctx.get("set_phase", "unknown")
        duration = time_ctx.get("set_duration_minutes", 0)
        summary_parts.append(f"Set: {phase} phase ({duration:.0f} min)")

    return "\n".join(summary_parts)


def select_prompt_for_context(context: dict) -> str:
    """
    Automatically select the most appropriate prompt based on context

    Args:
        context: Current crowd context

    Returns:
        Appropriate prompt template
    """
    # Extract key metrics
    energy = context.get("energy", {}).get("energy", 50)
    phase = context.get("time_context", {}).get("set_phase", "building")

    # Select prompt based on context
    if energy < 40:
        return EMERGENCY_ENERGY_BOOST_PROMPT
    elif phase == "opening":
        return OPENING_SET_PROMPT
    elif phase == "peak" or energy > 80:
        return PEAK_TIME_PROMPT
    elif phase == "closing":
        return CLOSING_SET_PROMPT
    else:
        return TRACK_RECOMMENDATION_PROMPT
