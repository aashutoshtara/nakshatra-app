"""
AI Astrologer Service
Combines: Claude AI + Birth Chart + VedAstro Interpretations

This is the brain of Nakshatra - converts user questions into
personalized astrological insights.
"""

import anthropic
from typing import Optional
from dataclasses import dataclass
from datetime import datetime

from config import ANTHROPIC_API_KEY
from data.vedastro import vedastro


@dataclass
class UserChart:
    """User's birth chart data"""
    name: str
    birth_date: str
    birth_time: str
    birth_place: str
    
    # Core chart data
    ascendant: str = ""
    moon_sign: str = ""
    sun_sign: str = ""
    nakshatra: str = ""
    nakshatra_pada: int = 0
    
    # Planets (sign placements)
    planets: dict = None  # {"Sun": "Aries", "Moon": "Cancer", ...}
    
    # Houses (which sign in which house)
    houses: dict = None  # {"1": "Aries", "2": "Taurus", ...}
    
    # Current Dasha
    current_mahadasha: str = ""
    current_antardasha: str = ""
    
    def __post_init__(self):
        if self.planets is None:
            self.planets = {}
        if self.houses is None:
            self.houses = {}


class AIAstrologer:
    """
    Conversational AI Astrologer
    
    Takes a user's question + their birth chart and generates
    personalized astrological insights using Claude.
    """
    
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        self.model = "claude-sonnet-4-20250514"
        self.conversation_history = {}  # Track per-user to avoid repetition
    
    def ask(self, question: str, user_chart: UserChart, user_id: str = None) -> str:
        """
        Main entry point - ask the AI astrologer a question
        
        Args:
            question: User's question (e.g., "Why am I having career troubles?")
            user_chart: User's birth chart data
            user_id: Optional user ID for conversation tracking
        
        Returns:
            Personalized astrological response
        """
        import random
        
        # 1. Build context from chart + VedAstro
        context = self._build_context(user_chart, question)
        
        # 2. Get conversation history to avoid repetition
        history = []
        if user_id and user_id in self.conversation_history:
            history = self.conversation_history[user_id][-4:]  # Last 4 exchanges
        
        # 3. Create prompt with variety
        system_prompt = self._get_system_prompt()
        user_prompt = self._build_user_prompt(question, context, history)
        
        # 4. Build messages with history for context
        messages = []
        for h in history:
            messages.append({"role": "user", "content": h["question"]})
            messages.append({"role": "assistant", "content": h["answer"]})
        messages.append({"role": "user", "content": user_prompt})
        
        # 5. Call Claude with higher temperature for variety
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            temperature=random.uniform(0.75, 1.0),  # Higher temperature for more variety
            system=system_prompt,
            messages=messages
        )
        
        answer = response.content[0].text
        
        # 6. Store in history
        if user_id:
            if user_id not in self.conversation_history:
                self.conversation_history[user_id] = []
            self.conversation_history[user_id].append({
                "question": question,
                "answer": answer
            })
            # Keep only last 10 exchanges
            if len(self.conversation_history[user_id]) > 10:
                self.conversation_history[user_id] = self.conversation_history[user_id][-10:]
        
        return answer
    
    def _get_system_prompt(self) -> str:
        """System prompt for the AI astrologer with variety"""
        import random
        from datetime import datetime
        today = datetime.now()
        date_str = today.strftime("%B %d, %Y")
        
        # Different personality styles to rotate
        personalities = [
            "warm and nurturing, like a caring grandmother who has studied the stars for decades",
            "wise and thoughtful, like an ancient sage sharing timeless wisdom",
            "friendly and approachable, like a knowledgeable friend who happens to be an expert",
            "calm and reassuring, like a patient teacher guiding you through life's mysteries",
            "insightful and direct, offering clear guidance without unnecessary fluff",
            "gently humorous, weaving light moments into profound insights",
            "empathetic and understanding, always acknowledging feelings first"
        ]
        
        # Different opening styles
        response_styles = [
            "Start with a warm acknowledgment of their question, then dive into the chart.",
            "Begin by connecting their question to a specific placement in their chart.",
            "Open with an interesting observation about their chart that relates to their query.",
            "Start with empathy for what they might be experiencing, then offer insights.",
            "Jump straight into the most relevant astrological factor for their question.",
            "Begin with a gentle question that makes them reflect, then share insights.",
            "Start with what's going well in their chart before addressing challenges."
        ]
        
        # Ways to reference placements (example for prompt)
        placement_phrasings = [
            "Your Moon in Cancer...",
            "With Cancer as your Moon sign...",
            "The lunar placement in Cancer...",
            "Since the Moon occupies Cancer in your chart...",
            "Given your Cancerian Moon...",
            "Looking at how the Moon sits in Cancer..."
        ]
        
        personality = random.choice(personalities)
        style = random.choice(response_styles)
        phrasing_example = random.choice(placement_phrasings)
        
        return f"""You are a Vedic astrologer who is {personality}.

Today's date is {date_str}.

CRITICAL - Sound natural and varied, NOT like a bot:
- Never start two responses the same way
- Mix up sentence lengths - some short, some longer
- Use contractions naturally (you're, it's, that's)
- Occasionally use casual phrases ("Here's the thing...", "Interestingly...", "You know what's fascinating...")
- Don't always follow the same structure
- Reference placements in varied ways. Example phrasings: "{phrasing_example}"

For this response: {style}

Absolute DON'Ts:
- "Based on your chart..." (overused opener)
- "As a Vedic astrologer, I..." (never say this)
- Always listing Sun, Moon, then other planets in order
- Ending every response with "Does this resonate?" or similar
- Using "planetary influences" in every response
- Being preachy or lecture-like
- Repeating remedies you've already suggested

Response variety ideas:
- Sometimes ask them a reflective question
- Sometimes use a metaphor or analogy
- Sometimes be brief and direct (2-3 sentences if appropriate)
- Sometimes share a relevant story or example
- Sometimes focus on just ONE key insight rather than many
- Occasionally mention what's going RIGHT in their chart

Core principles:
1. Every insight must connect to THEIR specific chart
2. Balance honesty with hope
3. Free will matters - these are tendencies, not destiny
4. Be conversational, like a wise friend"""
    
    def _build_context(self, chart: UserChart, question: str) -> dict:
        """
        Build relevant context from chart and VedAstro interpretations
        """
        from datetime import datetime
        today = datetime.now()
        
        context = {
            "current_date": today.strftime("%B %d, %Y"),
            "chart_summary": self._get_chart_summary(chart),
            "planet_interpretations": [],
            "relevant_insights": [],
        }
        
        # Get interpretations for each planet placement
        for planet, sign in chart.planets.items():
            if sign:
                interp = vedastro.get_planet_in_sign(planet, sign)
                if interp:
                    context["planet_interpretations"].append({
                        "placement": f"{planet} in {sign}",
                        "nature": interp.get("nature", ""),
                        "meaning": interp.get("description", "")
                    })
        
        # Search for relevant interpretations based on question keywords
        keywords = self._extract_keywords(question)
        for keyword in keywords:
            results = vedastro.search_description(keyword)
            for r in results[:3]:  # Limit to top 3 per keyword
                context["relevant_insights"].append({
                    "topic": r.get("name", ""),
                    "insight": r.get("description", "")
                })
        
        # Add dasha context if available
        if chart.current_mahadasha:
            dasha_info = vedastro.get_dasha_effect(
                chart.moon_sign, 
                chart.current_mahadasha, 
                level=1
            )
            if dasha_info:
                context["current_dasha"] = {
                    "period": f"{chart.current_mahadasha} Mahadasha",
                    "effect": dasha_info.get("description", "")
                }
        
        return context
    
    def _get_chart_summary(self, chart: UserChart) -> str:
        """Create a text summary of the chart"""
        summary = f"""
Name: {chart.name}
Birth: {chart.birth_date} at {chart.birth_time}, {chart.birth_place}

Ascendant (Lagna): {chart.ascendant}
Moon Sign (Rashi): {chart.moon_sign}
Sun Sign: {chart.sun_sign}
Nakshatra: {chart.nakshatra} (Pada {chart.nakshatra_pada})

Planet Positions:
"""
        for planet, sign in chart.planets.items():
            if sign:
                summary += f"  - {planet}: {sign}\n"
        
        if chart.current_mahadasha:
            summary += f"\nCurrent Dasha: {chart.current_mahadasha}"
            if chart.current_antardasha:
                summary += f" / {chart.current_antardasha}"
        
        return summary.strip()
    
    def _build_user_prompt(self, question: str, context: dict, history: list = None) -> str:
        """Build the full prompt with context and history awareness"""
        import random
        
        prompt = f"""## Today's Date
{context.get('current_date', 'Unknown')}

## User's Birth Chart
{context['chart_summary']}

## Planetary Interpretations (from classical texts)
"""
        # Randomize which interpretations to show for variety
        interps = context.get('planet_interpretations', [])
        if len(interps) > 3:
            interps = random.sample(interps, min(4, len(interps)))
        
        for interp in interps:
            prompt += f"\n**{interp['placement']}** ({interp['nature']}): {interp['meaning'][:200]}..."
        
        if context.get('current_dasha'):
            prompt += f"\n\n## Current Dasha Period\n{context['current_dasha']['period']}: {context['current_dasha']['effect']}"
        
        if context.get('relevant_insights'):
            prompt += "\n\n## Relevant Classical Insights"
            insights = context['relevant_insights'][:3]
            for insight in insights:
                prompt += f"\n- {insight['insight'][:150]}..."
        
        # Add history awareness - be specific about what to avoid
        if history and len(history) > 0:
            prompt += "\n\n## Conversation Context (IMPORTANT - vary your approach)"
            prompt += "\nYou've already discussed:"
            for h in history[-3:]:
                # Summarize what was covered
                prev_q = h['question'][:60]
                prev_a_start = h['answer'][:100] if len(h.get('answer', '')) > 0 else ''
                prompt += f"\n- Q: \"{prev_q}...\" → You mentioned: \"{prev_a_start}...\""
            prompt += "\n\n⚠️ Do NOT repeat the same points, remedies, or phrasings. Take a FRESH angle."
        
        prompt += f"\n\n## User's Current Question\n\"{question}\""
        
        # Vary the instruction AND suggest a style
        instructions = [
            "Give a personalized insight (try starting with their most relevant placement):",
            "Share your perspective (maybe open with a thoughtful observation):",
            "Offer guidance (consider being direct and practical this time):",
            "Respond naturally (as if chatting with a friend who asked for advice):",
            "Provide insight (perhaps focus on just ONE key point rather than many):",
            "Share your thoughts (try using a metaphor or analogy if it fits):",
            "Give guidance (start with what's positive before any challenges):",
            "Respond helpfully (be conversational, not formal):",
        ]
        
        # Occasionally add a specific style suggestion
        style_hints = [
            "",  # No extra hint
            " Keep it brief - 2-3 sentences might be enough.",
            " Feel free to ask them a reflective question.",
            " Try a different structure than your usual format.",
            "",  # No extra hint
            " Consider mentioning timing or dasha if relevant.",
            "",  # No extra hint
        ]
        
        prompt += f"\n\n## Your Response\n{random.choice(instructions)}{random.choice(style_hints)}"
        
        return prompt
    
    def _extract_keywords(self, question: str) -> list:
        """Extract relevant keywords from the question for searching"""
        # Topic-based keywords
        topic_map = {
            "career": ["career", "profession", "job", "work", "business"],
            "marriage": ["marriage", "spouse", "wife", "husband", "partner", "relationship"],
            "money": ["money", "wealth", "finance", "income", "property"],
            "health": ["health", "disease", "illness", "body"],
            "children": ["children", "son", "daughter", "pregnancy"],
            "travel": ["travel", "journey", "foreign"],
            "education": ["education", "study", "learning", "knowledge"],
        }
        
        question_lower = question.lower()
        keywords = []
        
        for topic, words in topic_map.items():
            if any(word in question_lower for word in words):
                keywords.extend(words[:2])  # Add first 2 words from matching topic
        
        # If no specific topic found, use generic keywords
        if not keywords:
            keywords = ["fortune", "life"]
        
        return list(set(keywords))[:3]  # Return unique, max 3
    
    # =========================================================================
    # QUICK INSIGHT METHODS
    # =========================================================================
    
    def get_daily_insight(self, chart: UserChart) -> str:
        """Get a quick daily insight based on current transits"""
        question = "What should I focus on today based on my chart and current planetary positions?"
        return self.ask(question, chart)
    
    def get_personality_summary(self, chart: UserChart) -> str:
        """Get a personality summary based on the birth chart"""
        question = "Give me a brief personality summary based on my ascendant, moon sign, and key planetary placements."
        return self.ask(question, chart)
    
    def get_career_guidance(self, chart: UserChart) -> str:
        """Get career-specific guidance"""
        question = "What careers or professions am I naturally suited for based on my chart?"
        return self.ask(question, chart)
    
    def get_relationship_insight(self, chart: UserChart) -> str:
        """Get relationship insights"""
        question = "What does my chart say about my approach to relationships and compatibility?"
        return self.ask(question, chart)


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

ai_astrologer = AIAstrologer()


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def ask_astrologer(question: str, user_chart: UserChart, user_id: str = None) -> str:
    """
    Quick function to ask the AI astrologer
    
    Args:
        question: User's question
        user_chart: UserChart object with birth details
        user_id: Optional user ID for conversation tracking (avoids repetition)
    
    Example:
        from services.ai_astrologer import ask_astrologer, UserChart
        
        chart = UserChart(
            name="John",
            birth_date="1990-05-15",
            birth_time="10:30",
            birth_place="Mumbai",
            moon_sign="Cancer",
            sun_sign="Taurus",
            ascendant="Leo",
            nakshatra="Pushya",
            planets={"Sun": "Taurus", "Moon": "Cancer", "Mars": "Aries", ...}
        )
        
        response = ask_astrologer("Why am I having career troubles?", chart, user_id="123")
        print(response)
    """
    return ai_astrologer.ask(question, user_chart, user_id)


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    # Test with sample data
    sample_chart = UserChart(
        name="Test User",
        birth_date="1990-05-15",
        birth_time="10:30",
        birth_place="Mumbai, India",
        ascendant="Leo",
        moon_sign="Cancer",
        sun_sign="Taurus",
        nakshatra="Pushya",
        nakshatra_pada=2,
        planets={
            "Sun": "Taurus",
            "Moon": "Cancer",
            "Mars": "Aries",
            "Mercury": "Taurus",
            "Jupiter": "Cancer",
            "Venus": "Gemini",
            "Saturn": "Capricorn",
        },
        current_mahadasha="Jupiter",
        current_antardasha="Saturn"
    )
    
    print("=" * 60)
    print("Testing AI Astrologer")
    print("=" * 60)
    
    # Test context building (without API call)
    context = ai_astrologer._build_context(sample_chart, "career")
    print("\n📋 Chart Summary:")
    print(context["chart_summary"])
    
    print("\n📚 Planet Interpretations Found:")
    for interp in context["planet_interpretations"][:3]:
        print(f"  - {interp['placement']}: {interp['meaning'][:80]}...")
    
    print("\n✅ Context building works!")
    print("\nTo test full AI response, uncomment the ask() call below")
    
    # Uncomment to test actual API call:
    # response = ai_astrologer.ask("What careers suit me best?", sample_chart)
    # print("\n🔮 AI Response:")
    # print(response)