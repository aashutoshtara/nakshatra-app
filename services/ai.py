from anthropic import Anthropic
from datetime import datetime, timezone, timedelta
from config import ANTHROPIC_API_KEY
from typing import Dict, Any

client = Anthropic(api_key=ANTHROPIC_API_KEY)

# Indian Standard Time
IST = timezone(timedelta(hours=5, minutes=30))

# Models
MODEL_QUALITY = "claude-haiku-4-5-20251001"
MODEL_FAST = "claude-haiku-4-5-20251001"


def get_current_date():
    """Get current date in IST"""
    today = datetime.now(IST)
    return {
        "date": today.strftime("%d %B %Y"),
        "day": today.strftime("%A"),
        "month": today.strftime("%B"),
        "year": today.strftime("%Y")
    }


def format_planets(planets: Dict) -> str:
    """Format planet positions for prompt"""
    if not planets:
        return "Planet data not available"
    
    lines = []
    for planet, data in planets.items():
        if planet != "Ascendant":
            retro = " (R)" if data.get("retrograde") else ""
            lines.append(f"- {planet}: {data.get('sign', 'Unknown')}{retro}")
    
    return "\n".join(lines)


async def generate_daily_guidance(
    name: str,
    moon_sign: str,
    nakshatra: str,
    gender: str = "male",
    panchang: Dict[str, Any] = None,
    chart_data: Dict[str, Any] = None
) -> str:
    """Generate precise daily guidance using full chart"""
    
    current = get_current_date()
    panchang = panchang or {}
    chart_data = chart_data or {}
    
    # Extract chart details
    current_dasha = chart_data.get("current_dasha", "Unknown")
    current_antardasha = chart_data.get("current_antardasha", "Unknown")
    nakshatra_lord = chart_data.get("nakshatra_lord", "Unknown")
    ascendant = chart_data.get("ascendant", "Unknown")
    planets = chart_data.get("planets", {})
    mangal_dosha = chart_data.get("mangal_dosha", False)
    
    prompt = f"""You are Nakshatra, an expert Vedic astrologer providing precise predictions.

═══════════════════════════════════════
CURRENT DATE: {current['date']} ({current['day']})
YEAR: {current['year']}
═══════════════════════════════════════

═══════════════════════════════════════
USER'S BIRTH CHART:
═══════════════════════════════════════
Name: {name}
Gender: {gender}

CORE CHART:
- Moon Sign (Chandra Rashi): {moon_sign}
- Nakshatra: {nakshatra} (Pada {chart_data.get('nakshatra_pada', 1)})
- Nakshatra Lord: {nakshatra_lord}
- Ascendant (Lagna): {ascendant}
- Sun Sign: {chart_data.get('sun_sign', 'Unknown')}

CURRENT PLANETARY PERIOD:
- Mahadasha: {current_dasha}
- Antardasha: {current_antardasha}
- Dasha ends: {chart_data.get('dasha_end_date', 'Unknown')}

BIRTH CHART PLANETS:
{format_planets(planets)}

SPECIAL FACTORS:
- Mangal Dosha: {"Yes" if mangal_dosha else "No"}
- Nakshatra Deity: {chart_data.get('deity', 'Unknown')}
- Gana: {chart_data.get('gana', 'Unknown')}
- Birth Stone: {chart_data.get('birth_stone', 'Unknown')}

═══════════════════════════════════════
TODAY'S PANCHANG:
═══════════════════════════════════════
- Tithi: {panchang.get('tithi', 'Unknown')}
- Nakshatra: {panchang.get('nakshatra', 'Unknown')}
- Yoga: {panchang.get('yoga', 'Unknown')}
- Karana: {panchang.get('karana', 'Unknown')}
- Rahu Kaal: {panchang.get('rahu_kaal_start', '')} - {panchang.get('rahu_kaal_end', '')}
- Moon Transit: {panchang.get('moon_sign_today', 'Unknown')}

═══════════════════════════════════════
ANALYSIS REQUIRED:
═══════════════════════════════════════

Analyze the interaction between:
1. Today's transiting Moon in {panchang.get('moon_sign_today', 'Unknown')} vs birth Moon in {moon_sign}
2. Today's nakshatra ({panchang.get('nakshatra', 'Unknown')}) vs birth nakshatra ({nakshatra})
3. Current {current_dasha}/{current_antardasha} dasha influence
4. Today's tithi and yoga effects on {moon_sign} natives

═══════════════════════════════════════
OUTPUT FORMAT:
═══════════════════════════════════════

🌅 Good Morning, {name}!

📊 TODAY'S ENERGY FOR YOU:
[2 lines analyzing Moon transit impact on their chart + dasha influence]

✅ DO TODAY:
- [Action] — [Precise reason: e.g., "Moon transits your 5th house, favoring creativity"]
- [Action] — [Reason tied to current dasha/antardasha]
- [Action] — [Reason tied to today's nakshatra compatibility]

❌ AVOID TODAY:
- [Thing] — [Reason: e.g., "Rahu Kaal from X-Y affects your 7th lord"]
- [Thing] — [Reason tied to challenging transit]
- [Thing] — [Reason tied to tithi]

⏰ BEST TIME: [Time] — [Why: based on Rahu Kaal and planetary hours]

🎨 LUCKY COLOR: {chart_data.get('lucky_color', 'Unknown')} — [Why this works for {nakshatra}]

🙏 TODAY'S REMEDY:
[Specific mantra or practice for {nakshatra_lord} or current dasha lord]

═══════════════════════════════════════
STRICT RULES:
═══════════════════════════════════════
- NEVER mention 2024 or past dates
- NO asterisk roleplay (*smiles*, etc.)
- Every point MUST have astrological reasoning
- Be SPECIFIC to their exact chart
- Under 220 words
- Professional, warm tone
- For future dates, use precise months and years based on user's chart and dasha

Generate now:"""

    response = client.messages.create(
        model=MODEL_QUALITY,
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.content[0].text


async def handle_user_query(
    name: str,
    moon_sign: str,
    nakshatra: str,
    gender: str,
    question: str,
    chart_data: Dict[str, Any] = None
) -> str:
    """Handle precise astrology queries"""
    
    current = get_current_date()
    chart_data = chart_data or {}
    
    # Check if complex question
    complex_keywords = ["career", "marriage", "love", "money", "health", "future", 
                       "year", "month", "job", "relationship", "business", "when",
                       "prediction", "forecast", "dasha", "transit"]
    needs_quality = any(word in question.lower() for word in complex_keywords)
    
    current_dasha = chart_data.get("current_dasha", "Unknown")
    current_antardasha = chart_data.get("current_antardasha", "Unknown")
    
    prompt = f"""You are Nakshatra, an expert Vedic astrologer.

═══════════════════════════════════════
TODAY: {current['date']} ({current['day']})
YEAR: {current['year']} (NEVER mention 2024 or past years)
═══════════════════════════════════════

═══════════════════════════════════════
USER'S CHART:
═══════════════════════════════════════
Name: {name} | Gender: {gender}
Moon Sign: {moon_sign}
Nakshatra: {nakshatra} (Lord: {chart_data.get('nakshatra_lord', 'Unknown')})
Ascendant: {chart_data.get('ascendant', 'Unknown')}
Sun Sign: {chart_data.get('sun_sign', 'Unknown')}

Current Dasha: {current_dasha} / {current_antardasha}
Dasha until: {chart_data.get('dasha_end_date', 'Unknown')}

Mangal Dosha: {"Yes" if chart_data.get('mangal_dosha') else "No"}

═══════════════════════════════════════
QUESTION: {question}
═══════════════════════════════════════

RESPONSE STRUCTURE:
1. Direct answer with SPECIFIC TIMELINE
2. Astrological reasoning (cite their dasha, moon sign, transits)
3. What to watch for
4. One actionable suggestion

EXAMPLES OF PRECISE ANSWERS:
- "Your {current_dasha} mahadasha runs until {chart_data.get('dasha_end_date', 'Unknown')}, which means..."
- "With Moon in {moon_sign} and current {current_antardasha} antardasha..."
- "Since your 7th lord is in X, marriage prospects improve after..."

RULES:
- Be SPECIFIC with timelines (months, periods)
- Reference their actual dasha periods
- No generic advice
- NO roleplay or asterisks
- Under 150 words
- If question unrelated to astrology, redirect politely

Respond:"""

    model = MODEL_QUALITY if needs_quality else MODEL_FAST
    
    response = client.messages.create(
        model=model,
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.content[0].text


async def generate_birth_chart_summary(
    name: str,
    gender: str,
    chart_data: Dict[str, Any]
) -> str:
    """Generate detailed birth chart summary"""
    
    current = get_current_date()
    
    moon_sign = chart_data.get("moon_sign", "Unknown")
    nakshatra = chart_data.get("nakshatra", "Unknown")
    ascendant = chart_data.get("ascendant", "Unknown")
    current_dasha = chart_data.get("current_dasha", "Unknown")
    current_antardasha = chart_data.get("current_antardasha", "Unknown")
    
    prompt = f"""You are Nakshatra, an expert Vedic astrologer.

═══════════════════════════════════════
COMPLETE BIRTH CHART ANALYSIS
═══════════════════════════════════════

Name: {name}
Gender: {gender}

CORE POSITIONS:
- Moon Sign: {moon_sign}
- Nakshatra: {nakshatra} (Pada {chart_data.get('nakshatra_pada', 1)})
- Nakshatra Lord: {chart_data.get('nakshatra_lord', 'Unknown')}
- Ascendant: {ascendant}
- Sun Sign: {chart_data.get('sun_sign', 'Unknown')}

NAKSHATRA DETAILS:
- Deity: {chart_data.get('deity', 'Unknown')}
- Gana: {chart_data.get('gana', 'Unknown')}
- Nadi: {chart_data.get('nadi', 'Unknown')}
- Animal Sign: {chart_data.get('animal_sign', 'Unknown')}
- Lucky Direction: {chart_data.get('lucky_direction', 'Unknown')}
- Birth Stone: {chart_data.get('birth_stone', 'Unknown')}
- Lucky Syllables: {chart_data.get('syllables', 'Unknown')}

CURRENT PERIOD:
- Mahadasha: {current_dasha} (until {chart_data.get('dasha_end_date', 'Unknown')})
- Antardasha: {current_antardasha}

SPECIAL FACTORS:
- Mangal Dosha: {"Yes - " + chart_data.get('mangal_dosha_desc', '') if chart_data.get('mangal_dosha') else "No"}

═══════════════════════════════════════
GENERATE PROFILE:
═══════════════════════════════════════

🌟 COSMIC PROFILE: {name}

🌙 MOON IN {moon_sign.upper()}:
[3 specific personality traits unique to {moon_sign} moon - be precise, not generic]

⭐ {nakshatra.upper()} NAKSHATRA:
[2-3 lines about life themes, strengths from this nakshatra. Mention deity {chart_data.get('deity', '')} blessing]

🌅 {ascendant.upper()} RISING:
[How others perceive them, external personality]

🔮 CURRENT LIFE PHASE ({current_dasha} Dasha):
[What this dasha period brings until {chart_data.get('dasha_end_date', 'Unknown')}. Be specific about themes]

💎 YOUR POWER FACTORS:
- Birth Stone: {chart_data.get('birth_stone', 'Unknown')} — [Why it helps them]
- Lucky Direction: {chart_data.get('lucky_direction', 'Unknown')} — [How to use it]
- Power Syllables: {chart_data.get('syllables', 'Unknown')} — [For naming/mantras]

⚠️ GROWTH AREAS:
[1-2 challenges based on their specific chart combination]

🎯 LIFE TIP:
[One powerful insight specific to {moon_sign} + {nakshatra} + {current_dasha} dasha combination]

RULES:
- Be SPECIFIC to their exact combination
- No generic horoscope content
- NO asterisk roleplay
- Under 250 words
- Today is {current['date']} - never mention 2024
- For future dates, use precise months and years based on user's chart and dasha

Generate:"""

    response = client.messages.create(
        model=MODEL_QUALITY,
        max_tokens=700,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.content[0].text