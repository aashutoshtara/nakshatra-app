"""
Telegram Bot Handler with AI Astrologer
Supports commands, free-form questions, and city selection
"""

import logging
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

from config import TELEGRAM_BOT_TOKEN
from services.geocoding import get_coordinates, search_cities
from services.database import (
    get_or_create_user_by_telegram,
    save_user_birth_details,
)
from services.astrology import calculate_birth_chart, get_today_panchanga
from services.ai_astrologer import ask_astrologer, UserChart

logger = logging.getLogger(__name__)

# Conversation states
(ASKING_NAME, ASKING_GENDER, ASKING_BIRTHDATE, ASKING_BIRTHTIME, 
 ASKING_BIRTHPLACE, SELECTING_CITY, CONFIRMING) = range(7)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def build_user_chart(user_data: dict, chart_result: dict = None) -> UserChart:
    """Build UserChart object from database user data and calculated chart"""
    
    planets = {}
    
    if chart_result:
        # Handle nested structure from full_analysis
        chart = chart_result.get("chart", chart_result)
        planets_data = chart.get("planets") or {}
        
        if isinstance(planets_data, dict):
            # Format: {"Sun": {"rashi_short": "Aries", ...}, ...}
            for planet_name, planet_info in planets_data.items():
                sign = planet_info.get("rashi_short") or planet_info.get("rashi", "")
                planets[planet_name] = sign
        elif isinstance(planets_data, list):
            # Format: [{"planet": "Sun", "sign": "Aries", ...}, ...]
            for planet in planets_data:
                planets[planet.get("planet", "")] = planet.get("sign", "")
    
    # Extract ascendant
    ascendant = user_data.get("ascendant", "")
    if not ascendant and chart_result:
        chart = chart_result.get("chart", chart_result)
        asc_data = chart.get("ascendant") or {}
        ascendant = asc_data.get("rashi_short") or asc_data.get("rashi", "")
    
    # Extract moon sign
    moon_sign = user_data.get("moon_sign", "")
    if not moon_sign and chart_result:
        chart = chart_result.get("chart", chart_result)
        moon_data = chart.get("moon_sign") or {}
        moon_sign = moon_data.get("rashi_short") or moon_data.get("rashi", "")
    
    # Extract sun sign
    sun_sign = user_data.get("sun_sign", "")
    if not sun_sign and chart_result:
        chart = chart_result.get("chart", chart_result)
        sun_data = chart.get("sun_sign") or {}
        sun_sign = sun_data.get("rashi_short") or sun_data.get("rashi", "")
    
    # Extract nakshatra
    nakshatra = user_data.get("nakshatra", "")
    if not nakshatra and chart_result:
        chart = chart_result.get("chart", chart_result)
        nak_data = chart.get("nakshatra") or {}
        nakshatra = nak_data.get("name", "")
    
    # Extract dasha
    mahadasha = ""
    antardasha = ""
    if user_data.get("current_dasha"):
        parts = user_data.get("current_dasha", "").split("/")
        mahadasha = parts[0] if len(parts) > 0 else ""
        antardasha = parts[1] if len(parts) > 1 else ""
    elif chart_result:
        dasha = chart_result.get("dasha") or {}
        mahadasha = dasha.get("current_mahadasha", {}).get("lord", "")
        antardasha = dasha.get("current_antardasha", {}).get("lord", "")
    
    return UserChart(
        name=user_data.get("name", "Friend"),
        birth_date=str(user_data.get("birth_date", "")),
        birth_time=str(user_data.get("birth_time", "")),
        birth_place=user_data.get("birth_place", ""),
        ascendant=ascendant,
        moon_sign=moon_sign,
        sun_sign=sun_sign,
        nakshatra=nakshatra,
        nakshatra_pada=user_data.get("nakshatra_pada", 0),
        planets=planets,
        current_mahadasha=mahadasha,
        current_antardasha=antardasha,
    )


def format_chart_message(chart_result: dict, name: str) -> str:
    """Format birth chart as a nice message"""
    if not chart_result:
        return f"🌟 *{name}'s Birth Chart* 🌟\n\n❌ Chart data not available."
    
    msg = f"🌟 *{name}'s Birth Chart* 🌟\n\n"
    
    # Handle nested structure from full_analysis
    # chart_result could have "chart" key containing the actual chart
    chart = chart_result.get("chart", chart_result)
    
    # Ascendant - look for "sign" or "rashi" or "rashi_short"
    asc = chart.get("ascendant") or {}
    asc_sign = asc.get("sign") or asc.get("rashi_short") or asc.get("rashi", "N/A")
    msg += f"⬆️ *Ascendant:* {asc_sign}\n"
    
    # Moon Sign & Nakshatra
    moon_sign_data = chart.get("moon_sign") or {}
    moon_sign = moon_sign_data.get("rashi_short") or moon_sign_data.get("rashi", "N/A")
    msg += f"🌙 *Moon Sign:* {moon_sign}\n"
    
    nakshatra_data = chart.get("nakshatra") or {}
    nakshatra_name = nakshatra_data.get("name", "N/A")
    msg += f"⭐ *Nakshatra:* {nakshatra_name}\n\n"
    
    # Sun Sign
    sun_sign_data = chart.get("sun_sign") or {}
    sun_sign = sun_sign_data.get("rashi_short") or sun_sign_data.get("rashi", "N/A")
    msg += f"☀️ *Sun Sign:* {sun_sign}\n\n"
    
    # All planets - could be dict or list
    planets = chart.get("planets") or {}
    
    planet_emojis = {
        "Sun": "☀️", "Moon": "🌙", "Mars": "🔴", "Mercury": "💚",
        "Jupiter": "🟡", "Venus": "💗", "Saturn": "⚫", "Rahu": "🐍", "Ketu": "🔥"
    }
    
    if planets:
        msg += "*Planet Positions:*\n"
        
        if isinstance(planets, dict):
            # Format: {"Sun": {...}, "Moon": {...}, ...}
            for planet_name, planet_data in planets.items():
                emoji = planet_emojis.get(planet_name, "•")
                sign = planet_data.get("rashi_short") or planet_data.get("rashi", "N/A")
                nakshatra = planet_data.get("nakshatra", "")
                msg += f"{emoji} {planet_name}: {sign} ({nakshatra})\n"
        elif isinstance(planets, list):
            # Format: [{"planet": "Sun", ...}, ...]
            for planet in planets:
                planet_name = planet.get("planet", "")
                emoji = planet_emojis.get(planet_name, "•")
                sign = planet.get("sign") or planet.get("rashi_short", "N/A")
                nakshatra = planet.get("nakshatra", "")
                msg += f"{emoji} {planet_name}: {sign} ({nakshatra})\n"
    
    # Dasha - could be nested in chart_result or at top level
    dasha = chart_result.get("dasha") or chart.get("dasha") or {}
    if dasha:
        mahadasha = dasha.get("current_mahadasha", {}).get("lord", "")
        antardasha = dasha.get("current_antardasha", {}).get("lord", "")
        if mahadasha:
            msg += f"\n🔮 *Current Dasha:* {mahadasha}"
            if antardasha and antardasha != "Unknown":
                msg += f" - {antardasha}"
            msg += "\n"
    
    import random
    
    endings = [
        "\n💬 *Ask me anything about your chart!*",
        "\n✨ *What would you like to know?*",
        "\n🔮 *Curious about something? Just ask!*",
        "\n💫 *Ready to explore? Type your question!*",
        "\n🌟 *What's on your mind?*",
    ]
    
    msg += random.choice(endings)
    return msg


def format_panchanga_message(panchanga: dict) -> str:
    """Format today's panchanga"""
    msg = f"🕉️ *Today's Panchanga* 🕉️\n"
    msg += f"📅 {datetime.now().strftime('%A, %B %d, %Y')}\n\n"
    
    msg += f"🌙 *Tithi:* {panchanga.get('tithi', 'N/A')}\n"
    msg += f"⭐ *Nakshatra:* {panchanga.get('nakshatra', 'N/A')}\n"
    msg += f"🌅 *Sunrise:* {panchanga.get('sunrise', 'N/A')}\n"
    msg += f"🌇 *Sunset:* {panchanga.get('sunset', 'N/A')}\n"
    
    if panchanga.get("rahu_kala"):
        msg += f"\n⚠️ *Rahu Kala:* {panchanga['rahu_kala']}\n"
    
    return msg


def parse_date(date_text: str) -> tuple:
    """Parse date and return (year, month, day) or None"""
    for fmt in ["%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%d %m %Y"]:
        try:
            parsed = datetime.strptime(date_text.strip(), fmt)
            return (parsed.year, parsed.month, parsed.day)
        except ValueError:
            continue
    return None


def parse_time(time_text: str) -> tuple:
    """Parse time and return (hour, minute) or None"""
    for fmt in ["%H:%M", "%I:%M %p", "%H%M"]:
        try:
            parsed = datetime.strptime(time_text.strip(), fmt)
            return (parsed.hour, parsed.minute)
        except ValueError:
            continue
    return None


# =============================================================================
# COMMAND HANDLERS
# =============================================================================

def _get_varied_greeting(name: str, returning: bool = False) -> str:
    """Get a varied greeting message"""
    import random
    
    if returning:
        greetings = [
            f"Welcome back, {name}! 🙏\n\nYour chart is ready. What's on your mind today?",
            f"Namaste {name}! 🌟\n\nGood to see you again. What would you like to explore?",
            f"Hello {name}! ✨\n\nI'm here with your chart. Ask me anything!",
            f"Hey {name}! 🙏\n\nReady to dive into some cosmic insights? Just type your question.",
            f"Welcome, {name}! 🌙\n\nYour chart awaits. What shall we explore today?",
        ]
    else:
        greetings = [
            f"Namaste {name}! 🙏\n\nI'm your personal Vedic astrologer. Let's create your birth chart to unlock personalized insights.\n\nTap /chart to begin!",
            f"Hello {name}! 🌟\n\nWelcome! I blend ancient Jyotish wisdom with modern conversation. First, let's map your stars.\n\nUse /chart to get started.",
            f"Hey {name}! ✨\n\nExcited to be your cosmic guide! To give you personalized insights, I'll need your birth details.\n\nReady? Tap /chart",
            f"Welcome, {name}! 🌙\n\nI'm here to help you navigate life through the lens of Vedic astrology.\n\nLet's start with /chart to create your kundali.",
        ]
    
    return random.choice(greetings)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command"""
    user = update.effective_user
    
    # Get or create user in database
    db_user = await get_or_create_user_by_telegram(
        telegram_id=str(user.id),
        telegram_username=user.username,
        name=user.first_name
    )
    
    # Check if user already has birth details
    if db_user and db_user.get("birth_date"):
        greeting = _get_varied_greeting(user.first_name, returning=True)
        await update.message.reply_text(greeting)
    else:
        greeting = _get_varied_greeting(user.first_name, returning=False)
        await update.message.reply_text(
            greeting,
            reply_markup=ReplyKeyboardMarkup(
                [["/chart", "/today"]], 
                resize_keyboard=True,
                one_time_keyboard=True
            )
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command"""
    await update.message.reply_text(
        "🌟 *Nakshatra - Your AI Vedic Astrologer* 🌟\n\n"
        "*Commands:*\n"
        "/start - Welcome message\n"
        "/chart - Create/view your birth chart\n"
        "/newchart - Update birth details\n"
        "/today - Today's panchanga\n"
        "/help - This message\n\n"
        "*Ask me anything:*\n"
        "• Why am I having career troubles?\n"
        "• Is this a good time to start a business?\n"
        "• What does my chart say about relationships?\n"
        "• When will my luck improve?\n\n"
        "Just type your question and I'll give you personalized guidance! 🔮",
        parse_mode="Markdown"
    )


async def today_panchanga(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /today command"""
    try:
        panchanga = get_today_panchanga(latitude=28.6139, longitude=77.2090)
        msg = format_panchanga_message(panchanga)
        await update.message.reply_text(msg, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Error getting panchanga: {e}")
        import random
        errors = [
            "Couldn't fetch today's panchanga right now. Try again in a moment?",
            "The panchanga calculation hit a snag. Give it another try?",
            "Hmm, trouble getting today's cosmic calendar. Please retry!",
        ]
        await update.message.reply_text(random.choice(errors))


# =============================================================================
# CHART CREATION CONVERSATION
# =============================================================================

async def chart_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start chart creation - ask for name"""
    user = update.effective_user
    context.user_data.clear()
    context.user_data["telegram_id"] = str(user.id)
    
    await update.message.reply_text(
        "Let's create your birth chart! 🌟\n\n"
        "What's your full name?",
        reply_markup=ReplyKeyboardRemove()
    )
    return ASKING_NAME


async def received_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Received name, ask for gender"""
    context.user_data["name"] = update.message.text.strip()
    
    await update.message.reply_text(
        f"Nice to meet you, {context.user_data['name']}! 🙏\n\n"
        "What's your gender?",
        reply_markup=ReplyKeyboardMarkup(
            [["Male", "Female"]], 
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )
    return ASKING_GENDER


async def received_gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Received gender, ask for birth date"""
    gender_text = update.message.text.strip().lower()
    
    if gender_text in ["male", "m", "पुरुष"]:
        context.user_data["gender"] = "male"
    elif gender_text in ["female", "f", "महिला", "स्त्री"]:
        context.user_data["gender"] = "female"
    else:
        await update.message.reply_text(
            "Please select Male or Female",
            reply_markup=ReplyKeyboardMarkup(
                [["Male", "Female"]], 
                resize_keyboard=True,
                one_time_keyboard=True
            )
        )
        return ASKING_GENDER
    
    await update.message.reply_text(
        "What's your date of birth? 📅\n"
        "Format: DD/MM/YYYY (e.g., 15/08/1990)",
        reply_markup=ReplyKeyboardRemove()
    )
    return ASKING_BIRTHDATE


async def received_birthdate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Received birth date, ask for time"""
    date_text = update.message.text.strip()
    parsed = parse_date(date_text)
    
    if not parsed:
        await update.message.reply_text(
            "❌ Invalid date format. Please use DD/MM/YYYY\n"
            "Example: 15/08/1990"
        )
        return ASKING_BIRTHDATE
    
    context.user_data["birth_year"] = parsed[0]
    context.user_data["birth_month"] = parsed[1]
    context.user_data["birth_day"] = parsed[2]
    context.user_data["birth_date"] = f"{parsed[0]}-{parsed[1]:02d}-{parsed[2]:02d}"
    
    await update.message.reply_text(
        "What time were you born? ⏰\n"
        "Format: HH:MM (24-hour, e.g., 14:30)\n\n"
        "If you don't know exact time, enter approximate or 12:00"
    )
    return ASKING_BIRTHTIME


async def received_birthtime(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Received birth time, ask for place"""
    time_text = update.message.text.strip()
    parsed = parse_time(time_text)
    
    if not parsed:
        await update.message.reply_text(
            "❌ Invalid time format. Please use HH:MM (24-hour)\n"
            "Example: 14:30 or 09:15"
        )
        return ASKING_BIRTHTIME
    
    context.user_data["birth_hour"] = parsed[0]
    context.user_data["birth_minute"] = parsed[1]
    context.user_data["birth_time"] = f"{parsed[0]:02d}:{parsed[1]:02d}"
    
    location_button = KeyboardButton("📍 Share Location", request_location=True)
    await update.message.reply_text(
        "Where were you born? 📍\n\n"
        "Type the city name (e.g., Mumbai, Maharashtra)\n"
        "or share your birth location:",
        reply_markup=ReplyKeyboardMarkup(
            [[location_button], ["Cancel"]], 
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )
    return ASKING_BIRTHPLACE


async def received_birthplace(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Received birth place - search and offer options"""
    
    # Check if location was shared
    if update.message.location:
        lat = update.message.location.latitude
        lng = update.message.location.longitude
        context.user_data["birth_lat"] = lat
        context.user_data["birth_lng"] = lng
        context.user_data["birth_place"] = f"Lat: {lat:.4f}, Lng: {lng:.4f}"
        return await show_confirmation(update, context)
    
    place_text = update.message.text.strip()
    
    if place_text.lower() == "cancel":
        await update.message.reply_text(
            "Cancelled. Use /chart to start again.",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    
    # Search for cities
    city_options = await search_cities(place_text)
    
    if not city_options:
        await update.message.reply_text(
            f"❌ Couldn't find *{place_text}*\n\n"
            "Please try:\n"
            "• Check spelling\n"
            "• Enter nearest big city\n"
            "• Add state name (e.g., Indore, MP)",
            parse_mode="Markdown"
        )
        return ASKING_BIRTHPLACE
    
    if len(city_options) == 1:
        # Only one result - ask for confirmation
        city = city_options[0]
        context.user_data["birth_place"] = city["name"]
        context.user_data["birth_lat"] = city["lat"]
        context.user_data["birth_lng"] = city["lng"]
        return await show_confirmation(update, context)
    
    # Multiple results - let user choose
    context.user_data["city_options"] = city_options
    
    options_text = "📍 *Multiple locations found:*\n\n"
    keyboard = []
    for i, city in enumerate(city_options[:5], 1):
        options_text += f"{i}️⃣ {city['name']}\n"
        keyboard.append([f"{i}. {city['name'][:30]}"])
    
    keyboard.append(["🔄 Search again"])
    
    await update.message.reply_text(
        options_text + "\nSelect your birth place:",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    )
    return SELECTING_CITY


async def select_city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle city selection from options"""
    text = update.message.text.strip()
    
    if "search again" in text.lower():
        await update.message.reply_text(
            "Enter your birth city:",
            reply_markup=ReplyKeyboardRemove()
        )
        return ASKING_BIRTHPLACE
    
    # Extract selection number
    try:
        selection = int(text[0])
        city_options = context.user_data.get("city_options", [])
        
        if 1 <= selection <= len(city_options):
            city = city_options[selection - 1]
            context.user_data["birth_place"] = city["name"]
            context.user_data["birth_lat"] = city["lat"]
            context.user_data["birth_lng"] = city["lng"]
            return await show_confirmation(update, context)
    except (ValueError, IndexError):
        pass
    
    await update.message.reply_text("Please select a valid option from the list.")
    return SELECTING_CITY


async def show_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show confirmation of details"""
    data = context.user_data
    
    gender_emoji = "👨" if data.get("gender") == "male" else "👩"
    
    await update.message.reply_text(
        f"Please confirm your details:\n\n"
        f"👤 Name: {data['name']}\n"
        f"{gender_emoji} Gender: {data.get('gender', 'N/A').title()}\n"
        f"📅 Date: {data['birth_date']}\n"
        f"⏰ Time: {data['birth_time']}\n"
        f"📍 Place: {data['birth_place']}\n\n"
        f"Is this correct?",
        reply_markup=ReplyKeyboardMarkup(
            [["✅ Yes, create my chart!", "❌ No, start over"]], 
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )
    return CONFIRMING


async def confirmed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """User confirmed details - calculate chart"""
    response = update.message.text
    
    if "Yes" in response or "✅" in response:
        await update.message.reply_text(
            "🔮 Calculating your birth chart...",
            reply_markup=ReplyKeyboardRemove()
        )
        
        try:
            data = context.user_data
            
            # Debug logging
            logger.info(f"Chart data: name={data.get('name')}, "
                       f"year={data.get('birth_year')}, month={data.get('birth_month')}, "
                       f"day={data.get('birth_day')}, hour={data.get('birth_hour')}, "
                       f"minute={data.get('birth_minute')}, place={data.get('birth_place')}, "
                       f"lat={data.get('birth_lat')}, lng={data.get('birth_lng')}")
            
            # Calculate chart with CORRECT function signature
            chart_result = calculate_birth_chart(
                name=str(data["name"]),
                year=int(data["birth_year"]),
                month=int(data["birth_month"]),
                day=int(data["birth_day"]),
                hour=int(data["birth_hour"]),
                minute=int(data["birth_minute"]),
                place_name=str(data["birth_place"]),
                latitude=float(data["birth_lat"]),
                longitude=float(data["birth_lng"])
            )
            
            # Debug: log the chart result
            logger.info(f"Chart result: {chart_result}")
            
            if not chart_result:
                logger.error("Chart result is empty!")
                await update.message.reply_text(
                    "❌ Chart calculation returned empty result. Please try again."
                )
                return ConversationHandler.END
            
            # Extract key data for database
            chart = chart_result.get("chart", chart_result)
            
            # Get moon data
            moon_sign_data = chart.get("moon_sign") or {}
            moon_sign = moon_sign_data.get("rashi_short") or moon_sign_data.get("rashi", "")
            
            # Get sun data
            sun_sign_data = chart.get("sun_sign") or {}
            sun_sign = sun_sign_data.get("rashi_short") or sun_sign_data.get("rashi", "")
            
            # Get ascendant
            asc_data = chart.get("ascendant") or {}
            ascendant = asc_data.get("rashi_short") or asc_data.get("rashi", "")
            
            # Get nakshatra
            nak_data = chart.get("nakshatra") or {}
            nakshatra = nak_data.get("name", "")
            
            # Get dasha
            dasha_data = chart_result.get("dasha") or {}
            mahadasha = dasha_data.get("current_mahadasha", {}).get("lord", "")
            antardasha = dasha_data.get("current_antardasha", {}).get("lord", "")
            
            # Save to database
            await save_user_birth_details(
                telegram_id=data["telegram_id"],
                name=data["name"],
                gender=data.get("gender", ""),
                birth_date=data["birth_date"],
                birth_time=data["birth_time"],
                birth_place=data["birth_place"],
                birth_lat=data["birth_lat"],
                birth_lng=data["birth_lng"],
                moon_sign=moon_sign,
                sun_sign=sun_sign,
                ascendant=ascendant,
                nakshatra=nakshatra,
                current_dasha=f"{mahadasha}/{antardasha}" if mahadasha else ""
            )
            
            # Store chart in context for follow-up questions
            context.user_data["chart_result"] = chart_result
            
            # Send formatted chart
            msg = format_chart_message(chart_result, data["name"])
            await update.message.reply_text(msg, parse_mode="Markdown")
            
        except Exception as e:
            logger.error(f"Error calculating chart: {e}")
            import random
            errors = [
                "❌ Oops! Something went wrong with the calculation. Try /chart again?",
                "❌ The stars weren't aligned for that calculation. Please retry with /chart",
                "❌ Hit a cosmic bump! Give /chart another go?",
            ]
            await update.message.reply_text(random.choice(errors))
    else:
        await update.message.reply_text(
            "No problem! Use /chart to start over.",
            reply_markup=ReplyKeyboardRemove()
        )
    
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the conversation"""
    await update.message.reply_text(
        "Cancelled. Use /chart to start again.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


# =============================================================================
# AI CHAT HANDLER
# =============================================================================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle free-form messages - AI chat mode"""
    user = update.effective_user
    message = update.message.text.strip()
    
    # Get user from database
    db_user = await get_or_create_user_by_telegram(
        telegram_id=str(user.id),
        telegram_username=user.username,
        name=user.first_name
    )
    
    # Check if user has birth details
    if not db_user or not db_user.get("birth_date"):
        await update.message.reply_text(
            "I'd love to help! But first, I need your birth details to give personalized guidance.\n\n"
            "Use /chart to create your birth chart, then ask me anything! 🌟"
        )
        return
    
    # Show typing indicator
    await update.message.chat.send_action("typing")
    
    try:
        # Get or calculate chart
        chart_result = context.user_data.get("chart_result")
        
        if not chart_result:
            # Parse stored date/time - handle different formats
            birth_date = db_user.get("birth_date", "1990-01-01")
            birth_time = db_user.get("birth_time", "12:00")
            
            # Handle date - could be string, date object, or other
            if hasattr(birth_date, 'year'):
                # It's a date object
                year, month, day = birth_date.year, birth_date.month, birth_date.day
            elif isinstance(birth_date, str):
                year, month, day = map(int, birth_date.split("-")[:3])
            else:
                year, month, day = 1990, 1, 1
            
            # Handle time - could be string, time object, or other
            if hasattr(birth_time, 'hour'):
                # It's a time object
                hour, minute = birth_time.hour, birth_time.minute
            elif isinstance(birth_time, str):
                parts = birth_time.replace(":", " ").split()[:2]
                hour, minute = int(parts[0]), int(parts[1]) if len(parts) > 1 else 0
            else:
                hour, minute = 12, 0
            
            # Recalculate chart
            chart_result = calculate_birth_chart(
                name=db_user.get("name", "User"),
                year=year,
                month=month,
                day=day,
                hour=hour,
                minute=minute,
                place_name=db_user.get("birth_place", "Delhi"),
                latitude=float(db_user.get("birth_lat", 28.6139)),
                longitude=float(db_user.get("birth_lng", 77.2090))
            )
            context.user_data["chart_result"] = chart_result
        
        # Build UserChart object
        user_chart = build_user_chart(db_user, chart_result)
        
        # Ask the AI astrologer with user_id for conversation memory
        user_id = str(user.id)  # Telegram user ID
        response = ask_astrologer(message, user_chart, user_id=user_id)
        
        # Send response (split if too long)
        if len(response) > 4000:
            for i in range(0, len(response), 4000):
                await update.message.reply_text(response[i:i+4000])
        else:
            await update.message.reply_text(response)
            
    except Exception as e:
        logger.error(f"Error in AI response: {e}")
        
        import random
        error_messages = [
            "🙏 Hmm, I had a little trouble with that. Could you rephrase your question?",
            "✨ Let me try again - could you ask that differently?",
            "🌙 Something went off track. Try asking in another way?",
            "💫 My cosmic connection flickered! Mind rephrasing that?",
            "🙏 Apologies, that one stumped me. What else would you like to know?",
        ]
        
        await update.message.reply_text(random.choice(error_messages))


# =============================================================================
# BOT SETUP
# =============================================================================

def create_telegram_bot() -> Application:
    """Create and configure the Telegram bot"""
    
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Chart creation conversation
    chart_conv = ConversationHandler(
        entry_points=[
            CommandHandler("chart", chart_start),
            CommandHandler("newchart", chart_start),
        ],
        states={
            ASKING_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, received_name)],
            ASKING_GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, received_gender)],
            ASKING_BIRTHDATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, received_birthdate)],
            ASKING_BIRTHTIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, received_birthtime)],
            ASKING_BIRTHPLACE: [
                MessageHandler(filters.LOCATION, received_birthplace),
                MessageHandler(filters.TEXT & ~filters.COMMAND, received_birthplace),
            ],
            SELECTING_CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_city)],
            CONFIRMING: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirmed)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("today", today_panchanga))
    application.add_handler(chart_conv)
    
    # AI Chat handler - catches all other messages
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, 
        handle_message
    ))
    
    return application