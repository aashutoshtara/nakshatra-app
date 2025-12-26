from anthropic import Anthropic
from datetime import datetime, timezone, timedelta
from config import ANTHROPIC_API_KEY
from typing import Dict, Any

client = Anthropic(api_key=ANTHROPIC_API_KEY)

# Indian Standard Time (UTC + 5:30)
IST = timezone(timedelta(hours=5, minutes=30))

# Model choices
MODEL_FAST = "claude-haiku-4-5-20251001"      # Quick, cheap
MODEL_QUALITY = "claude-sonnet-4-20250514"     # Better quality


def get_current_date():
    """Get current date in IST"""
    today = datetime.now(IST)
    return {
        "date": today.strftime("%d %B %Y"),
        "day": today.strftime("%A"),
        "month": today.strftime("%B"),
        "year": today.strftime("%Y")
    }


async def generate_daily_guidance(
    name: str,
    moon_sign: str,
    nakshatra: str,
    gender: str = "male",
    panchang: Dict[str, Any] = None
) -> str:
    """Generate personalized daily guidance - Uses QUALITY model"""
    
    current = get_current_date()
    panchang = panchang or {}
    
    prompt = f"""You are Nakshatra, a professional Vedic astrology advisor. Provide accurate, specific guidance.

═══════════════════════════════════════
CRITICAL DATE INFORMATION:
═══════════════════════════════════════
- TODAY IS: {current['date']} ({current['day']})
- CURRENT YEAR: {current['year']}
- CURRENT MONTH: {current['month']}

STRICT DATE RULES:
- NEVER mention 2024 or any past year
- NEVER mention past months
- Only discuss TODAY or FUTURE dates
- For future, use relative terms: "tomorrow", "this week", "next month" and/or precise month names based on their chart calculations

═══════════════════════════════════════
USER PROFILE:
═══════════════════════════════════════
- Name: {name}
- Gender: {gender}
- Moon Sign (Rashi): {moon_sign}
- Nakshatra: {nakshatra}

═══════════════════════════════════════
TODAY'S PANCHANG:
═══════════════════════════════════════
- Tithi: {panchang.get('tithi', 'Not available')}
- Nakshatra of the day: {panchang.get('nakshatra', 'Not available')}
- Day: {current['day']}

═══════════════════════════════════════
GENERATE TODAY'S GUIDANCE:
═══════════════════════════════════════

Structure your response EXACTLY like this:

🌅 Good Morning, {name}!

Today ({current['day']}) brings [one line about overall energy based on their moon sign + today's panchang].

✅ DO TODAY:
- [Specific action] — [Reason tied to {moon_sign} or {nakshatra}]
- [Specific action] — [Reason]
- [Specific action] — [Reason]

❌ AVOID TODAY:
- [Thing to avoid] — [Reason based on planetary position]
- [Thing to avoid] — [Reason]
- [Thing to avoid] — [Reason]

⏰ Best Time: [Time range] — [Why this window works for them]

🎨 Lucky Color: [Color] — [Connection to their chart]

🙏 Today's Practice: [Specific mantra or simple ritual] — [Why it helps {nakshatra} natives]

═══════════════════════════════════════
STRICT RULES:
═══════════════════════════════════════
- NEVER use asterisks for roleplay (*smiles*, *adjusts*)
- Be professional, warm, direct
- Every point MUST have a specific reason
- Be SPECIFIC to {moon_sign} moon sign and {nakshatra} nakshatra
- NO generic advice
- Under 200 words total
- Use the exact emoji format shown above

Generate now:"""

    response = client.messages.create(
        model=MODEL_QUALITY,  # Using Sonnet for quality
        max_tokens=500,
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
    
    current = get_current_date()
    
    # Determine if this needs quality model
    complex_keywords = ["career", "marriage", "love", "money", "health", "future", 
                       "year", "month", "job", "relationship", "business", "prediction"]
    needs_quality = any(word in question.lower() for word in complex_keywords)
    
    model = MODEL_QUALITY if needs_quality else MODEL_FAST
    
    prompt = f"""You are Nakshatra, a professional Vedic astrology advisor.

═══════════════════════════════════════
CRITICAL DATE INFORMATION:
═══════════════════════════════════════
- TODAY IS: {current['date']} ({current['day']})
- CURRENT YEAR: {current['year']}
- NEVER mention 2024 or past years
- For future: use "coming weeks", "next month" or precise month names based on their chart calculations

═══════════════════════════════════════
USER PROFILE:
═══════════════════════════════════════
- Name: {name}
- Gender: {gender}  
- Moon Sign: {moon_sign}
- Nakshatra: {nakshatra}

═══════════════════════════════════════
QUESTION: {question}
═══════════════════════════════════════

RESPONSE FORMAT:
1. Direct answer to their question
2. Astrological reasoning (WHY - based on {moon_sign} moon sign & {nakshatra})
3. Specific timeline if applicable
4. One practical suggestion

RULES:
- NEVER use asterisks (*smiles*, *thinks*)
- Be specific to THEIR chart, not generic
- Include reasoning with every insight
- Professional but warm tone
- Under 200 words
- If not astrology-related, redirect politely

Respond:"""

    response = client.messages.create(
        model=model,
        max_tokens=450,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.content[0].text


async def generate_birth_chart_summary(
    name: str,
    moon_sign: str,
    nakshatra: str,
    ascendant: str,
    gender: str
) -> str:
    """Generate personalized birth chart summary - Uses QUALITY model"""
    
    current = get_current_date()
    
    prompt = f"""You are Nakshatra, a professional Vedic astrology advisor.

Today: {current['date']}

Create a PERSONALIZED birth chart summary for:
- Name: {name}
- Gender: {gender}
- Moon Sign: {moon_sign}
- Nakshatra: {nakshatra}
- Ascendant: {ascendant}

FORMAT:
🌟 Welcome, {name}!

Your Cosmic Blueprint:

🌙 Moon in {moon_sign}:
[2-3 lines about their emotional nature, specific traits - not generic]

⭐ {nakshatra} Nakshatra:
[2-3 lines about their nakshatra qualities, ruling deity, life themes]

🌅 {ascendant} Rising:
[1-2 lines about how others perceive them]

💫 Key Strengths:
- [Strength 1 - specific to their combination]
- [Strength 2]

⚠️ Watch Out For:
- [Challenge based on their chart]

🎯 Life Tip:
[One powerful insight specific to {moon_sign} + {nakshatra} combination]

RULES:
- Be SPECIFIC to their exact combination
- No generic statements that apply to everyone
- No asterisk roleplay
- Warm, professional tone
- Under 200 words

Generate:"""

    response = client.messages.create(
        model=MODEL_QUALITY,
        max_tokens=450,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.content[0].text