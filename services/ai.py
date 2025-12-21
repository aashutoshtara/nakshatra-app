from anthropic import Anthropic
from datetime import datetime
from config import ANTHROPIC_API_KEY
from typing import Dict, Any

client = Anthropic(api_key=ANTHROPIC_API_KEY)


async def generate_daily_guidance(
    name: str,
    moon_sign: str,
    nakshatra: str,
    panchang: Dict[str, Any] = None
) -> str:
    """Generate personalized daily guidance"""
    
    today = datetime.now()
    date_str = today.strftime("%d %B %Y")
    day = today.strftime("%A")
    
    panchang = panchang or {}
    
    prompt = f"""You are JyotiSaathi, a warm Vedic astrology guide. Generate daily guidance.

USER:
- Name: {name}
- Moon Sign: {moon_sign}
- Nakshatra: {nakshatra}

TODAY: {date_str} ({day})
- Tithi: {panchang.get('tithi', 'Unknown')}
- Nakshatra: {panchang.get('nakshatra', 'Unknown')}

Generate a personalized message with:
1. Warm greeting using their name
2. 3 things to DO today
3. 3 things to AVOID today
4. Best time for important work
5. Lucky color
6. One simple practice (mantra/ritual)

Keep it under 150 words. Be warm, specific, not generic. Use minimal emojis."""

    response = client.messages.create(
        model="claude-3-5-haiku-20241022",
        max_tokens=350,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.content[0].text


async def handle_user_query(
    name: str,
    moon_sign: str,
    nakshatra: str,
    question: str
) -> str:
    """Handle user's question"""
    
    prompt = f"""You are JyotiSaathi, a warm Vedic astrology guide.

USER: {name}
Moon Sign: {moon_sign}
Nakshatra: {nakshatra}

QUESTION: {question}

Give a helpful, personalized answer based on Vedic astrology.
Keep it under 100 words. Be warm and practical."""

    response = client.messages.create(
        model="claude-3-5-haiku-20241022",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.content[0].text