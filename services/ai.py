from anthropic import Anthropic
from datetime import datetime
from config import ANTHROPIC_API_KEY
from typing import Dict, Any

client = Anthropic(api_key=ANTHROPIC_API_KEY)


async def generate_daily_guidance(
    name: str,
    moon_sign: str,
    nakshatra: str,
    gender: str = "male",
    panchang: Dict[str, Any] = None
) -> str:
    """Generate personalized daily guidance"""
    
    today = datetime.now()
    date_str = today.strftime("%d %B %Y")
    day = today.strftime("%A")
    
    panchang = panchang or {}
    
    # Gender-appropriate terms
    if gender == "female":
        honorific = "Didi"
        pronoun = "her"
        possessive = "her"
    else:
        honorific = "Bhaiya"
        pronoun = "him"
        possessive = "his"
    
    prompt = f"""You are Nakshatra, a warm and friendly Vedic astrology guide. Generate personalized daily guidance.

USER PROFILE:
- Name: {name}
- Gender: {gender}
- Moon Sign (Rashi): {moon_sign}
- Nakshatra: {nakshatra}

TODAY'S PANCHANG ({date_str}, {day}):
- Tithi: {panchang.get('tithi', 'Unknown')}
- Nakshatra: {panchang.get('nakshatra', 'Unknown')}
- Day: {day}

INSTRUCTIONS:
1. Address the user warmly by name
2. Use gender-appropriate language and examples
3. Give 3 specific things to DO today (based on moon sign + panchang)
4. Give 3 specific things to AVOID today
5. Suggest best time for important work
6. Mention lucky color for today
7. Recommend one simple practice (mantra/small ritual)

STYLE:
- Keep it under 150 words
- Be warm, personal, not generic
- Use simple Hindi terms where appropriate (with meaning)
- Minimal emojis (1-2 max)
- Practical, actionable advice

Generate the guidance now:"""

    response = client.messages.create(
        model="claude-3-5-haiku-20241022",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.content[0].text


async def handle_user_query(
    name: str,
    moon_sign: str,
    nakshatra: str,
    gender: str,
    question: str
) -> str:
    """Handle user's astrology question"""
    
    # Gender-appropriate terms
    if gender == "female":
        honorific = "Devi"
        pronoun = "she"
        possessive = "her"
    else:
        honorific = "Dev"
        pronoun = "he"
        possessive = "his"
    
    prompt = f"""You are Nakshatra, a warm Vedic astrology guide.

USER PROFILE:
- Name: {name}
- Gender: {gender}
- Moon Sign: {moon_sign}
- Nakshatra: {nakshatra}

USER'S QUESTION: {question}

INSTRUCTIONS:
1. Answer based on Vedic astrology principles
2. Personalize based on {possessive} moon sign and nakshatra
3. Use gender-appropriate language
4. Be warm, supportive, practical
5. Keep response under 100 words
6. If question is not astrology-related, gently redirect

Respond now:"""

    response = client.messages.create(
        model="claude-3-5-haiku-20241022",
        max_tokens=250,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.content[0].text