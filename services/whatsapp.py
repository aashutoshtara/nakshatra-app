"""
WhatsApp Handler with AI Astrologer
Supports both structured flow and free-form questions via Twilio
"""

import logging
import re
from datetime import datetime
from typing import Optional

from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER
from services.geocoding import get_coordinates
from services.database import (
    get_or_create_user_by_phone,
    update_user_by_phone,
    save_user_birth_details,
)
from services.astrology import calculate_birth_chart, get_today_panchanga
from services.ai_astrologer import ask_astrologer, UserChart

logger = logging.getLogger(__name__)

# Initialize Twilio client
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Conversation states
STATE_NEW = "NEW"
STATE_ASKING_NAME = "ASKING_NAME"
STATE_ASKING_DATE = "ASKING_DATE"
STATE_ASKING_TIME = "ASKING_TIME"
STATE_ASKING_PLACE = "ASKING_PLACE"
STATE_CONFIRMING = "CONFIRMING"
STATE_READY = "READY"


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def normalize_phone(phone: str) -> str:
    """Normalize phone number to E.164 format"""
    phone = re.sub(r'[^\d+]', '', phone)
    phone = phone.replace('whatsapp:', '')
    
    if phone.startswith('00'):
        phone = '+' + phone[2:]
    elif not phone.startswith('+'):
        if len(phone) == 10:
            phone = '+91' + phone  # Default to India
        elif len(phone) == 11 and phone.startswith('1'):
            phone = '+' + phone  # US/Canada
        else:
            phone = '+' + phone
    
    return phone


def build_user_chart(user_data: dict, chart_result: dict = None) -> UserChart:
    """Build UserChart object from database user data and calculated chart"""
    
    planets = {}
    if chart_result and chart_result.get("planets"):
        for planet_data in chart_result["planets"]:
            planets[planet_data["planet"]] = planet_data["sign"]
    
    return UserChart(
        name=user_data.get("name", "Friend"),
        birth_date=user_data.get("birth_date", ""),
        birth_time=user_data.get("birth_time", ""),
        birth_place=user_data.get("birth_place", ""),
        ascendant=user_data.get("ascendant") or (chart_result.get("ascendant", {}).get("sign", "") if chart_result else ""),
        moon_sign=user_data.get("moon_sign", ""),
        sun_sign=user_data.get("sun_sign", ""),
        nakshatra=user_data.get("nakshatra", ""),
        nakshatra_pada=user_data.get("nakshatra_pada", 0),
        planets=planets,
        current_mahadasha=user_data.get("current_dasha", "").split("/")[0] if user_data.get("current_dasha") else "",
        current_antardasha=user_data.get("current_dasha", "").split("/")[1] if user_data.get("current_dasha") and "/" in user_data.get("current_dasha", "") else "",
    )


def format_chart_message(chart_result: dict, name: str) -> str:
    """Format birth chart for WhatsApp"""
    msg = f"🌟 *{name}'s Birth Chart* 🌟\n\n"
    
    asc = chart_result.get("ascendant", {})
    msg += f"⬆️ *Ascendant:* {asc.get('sign', 'N/A')}\n"
    
    moon_data = next((p for p in chart_result.get("planets", []) if p["planet"] == "Moon"), {})
    msg += f"🌙 *Moon Sign:* {moon_data.get('sign', 'N/A')}\n"
    msg += f"⭐ *Nakshatra:* {moon_data.get('nakshatra', 'N/A')}\n\n"
    
    sun_data = next((p for p in chart_result.get("planets", []) if p["planet"] == "Sun"), {})
    msg += f"☀️ *Sun Sign:* {sun_data.get('sign', 'N/A')}\n\n"
    
    msg += "*Planets:*\n"
    for planet in chart_result.get("planets", []):
        msg += f"• {planet['planet']}: {planet['sign']}\n"
    
    if chart_result.get("dasha"):
        dasha = chart_result["dasha"]
        msg += f"\n🔮 *Dasha:* {dasha.get('mahadasha', '')} / {dasha.get('antardasha', '')}\n"
    
    msg += "\n💬 *Ask me anything about your chart!*"
    return msg


def format_panchanga_message(panchanga: dict) -> str:
    """Format panchanga for WhatsApp"""
    msg = f"🕉️ *Today's Panchanga*\n"
    msg += f"📅 {datetime.now().strftime('%A, %B %d, %Y')}\n\n"
    msg += f"🌙 *Tithi:* {panchanga.get('tithi', 'N/A')}\n"
    msg += f"⭐ *Nakshatra:* {panchanga.get('nakshatra', 'N/A')}\n"
    msg += f"🌅 *Sunrise:* {panchanga.get('sunrise', 'N/A')}\n"
    msg += f"🌇 *Sunset:* {panchanga.get('sunset', 'N/A')}\n"
    return msg


# =============================================================================
# SEND MESSAGES
# =============================================================================

def send_whatsapp_message(to: str, message: str) -> bool:
    """Send WhatsApp message via Twilio"""
    try:
        to_number = normalize_phone(to)
        if not to_number.startswith('whatsapp:'):
            to_number = f'whatsapp:{to_number}'
        
        from_number = TWILIO_WHATSAPP_NUMBER
        if not from_number.startswith('whatsapp:'):
            from_number = f'whatsapp:{from_number}'
        
        twilio_client.messages.create(
            body=message,
            from_=from_number,
            to=to_number
        )
        return True
    except Exception as e:
        logger.error(f"Error sending WhatsApp: {e}")
        return False


# =============================================================================
# STATE HANDLERS
# =============================================================================

def handle_new_user(phone: str, message: str, user: dict) -> str:
    """Handle new user or user without chart"""
    msg_lower = message.lower().strip()
    
    # Check for commands
    if msg_lower in ["hi", "hello", "start", "help"]:
        update_user_by_phone(phone, {"state": STATE_NEW})
        return (
            "Namaste! 🙏 I'm your AI Vedic Astrologer.\n\n"
            "I can help you with:\n"
            "• Birth chart analysis\n"
            "• Career & relationship guidance\n"
            "• Life predictions\n\n"
            "Reply *CHART* to create your birth chart\n"
            "Reply *TODAY* for today's panchanga"
        )
    
    elif msg_lower == "chart":
        update_user_by_phone(phone, {"state": STATE_ASKING_NAME})
        return "Let's create your birth chart! 🌟\n\nWhat's your full name?"
    
    elif msg_lower == "today":
        panchanga = get_today_panchanga(lat=28.6139, lng=77.2090)
        return format_panchanga_message(panchanga)
    
    else:
        # User trying to ask question without chart
        return (
            "I'd love to help! But first I need your birth details.\n\n"
            "Reply *CHART* to create your birth chart, then ask me anything! 🌟"
        )


def handle_asking_name(phone: str, message: str, user: dict) -> str:
    """Handle name input"""
    name = message.strip()
    
    if len(name) < 2:
        return "Please enter a valid name (at least 2 characters)."
    
    update_user_by_phone(phone, {
        "name": name,
        "state": STATE_ASKING_DATE
    })
    
    return f"Nice to meet you, {name}! 🙏\n\nWhat's your date of birth?\nFormat: DD/MM/YYYY (e.g., 15/08/1990)"


def handle_asking_date(phone: str, message: str, user: dict) -> str:
    """Handle birth date input"""
    date_text = message.strip()
    
    # Parse date
    parsed_date = None
    for fmt in ["%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%d %m %Y"]:
        try:
            parsed_date = datetime.strptime(date_text, fmt)
            break
        except ValueError:
            continue
    
    if not parsed_date:
        return "❌ Invalid date. Please use DD/MM/YYYY format.\nExample: 15/08/1990"
    
    update_user_by_phone(phone, {
        "birth_date": parsed_date.strftime("%Y-%m-%d"),
        "state": STATE_ASKING_TIME
    })
    
    return "What time were you born? ⏰\nFormat: HH:MM (24-hour, e.g., 14:30)\n\nIf unsure, enter 12:00"


def handle_asking_time(phone: str, message: str, user: dict) -> str:
    """Handle birth time input"""
    time_text = message.strip()
    
    # Parse time
    parsed_time = None
    for fmt in ["%H:%M", "%I:%M %p", "%H%M", "%I:%M%p"]:
        try:
            parsed_time = datetime.strptime(time_text, fmt)
            break
        except ValueError:
            continue
    
    if not parsed_time:
        return "❌ Invalid time. Please use HH:MM format (24-hour).\nExample: 14:30 or 09:15"
    
    update_user_by_phone(phone, {
        "birth_time": parsed_time.strftime("%H:%M"),
        "state": STATE_ASKING_PLACE
    })
    
    return "Where were you born? 📍\nPlease enter the city name (e.g., Mumbai, India)"


def handle_asking_place(phone: str, message: str, user: dict) -> str:
    """Handle birth place input"""
    place_text = message.strip()
    
    # Geocode
    coords = get_coordinates(place_text)
    if not coords:
        return "❌ Couldn't find that location. Please try again.\nExample: Mumbai, India"
    
    update_user_by_phone(phone, {
        "birth_place": place_text,
        "birth_lat": coords["lat"],
        "birth_lng": coords["lng"],
        "state": STATE_CONFIRMING
    })
    
    # Get updated user data
    user = get_or_create_user_by_phone(phone)
    
    return (
        f"Please confirm your details:\n\n"
        f"👤 Name: {user.get('name')}\n"
        f"📅 Date: {user.get('birth_date')}\n"
        f"⏰ Time: {user.get('birth_time')}\n"
        f"📍 Place: {user.get('birth_place')}\n\n"
        f"Reply *YES* to confirm or *NO* to start over"
    )


def handle_confirming(phone: str, message: str, user: dict) -> str:
    """Handle confirmation"""
    msg_lower = message.lower().strip()
    
    if msg_lower in ["yes", "y", "confirm", "ok"]:
        try:
            # Calculate chart
            chart_result = calculate_birth_chart(
                date_str=user["birth_date"],
                time_str=user["birth_time"],
                lat=user["birth_lat"],
                lng=user["birth_lng"],
                place_name=user["birth_place"]
            )
            
            # Extract data
            moon_data = next((p for p in chart_result.get("planets", []) if p["planet"] == "Moon"), {})
            sun_data = next((p for p in chart_result.get("planets", []) if p["planet"] == "Sun"), {})
            
            # Save to database
            save_user_birth_details(
                phone=phone,
                name=user.get("name"),
                birth_date=user["birth_date"],
                birth_time=user["birth_time"],
                birth_place=user["birth_place"],
                birth_lat=user["birth_lat"],
                birth_lng=user["birth_lng"],
                moon_sign=moon_data.get("sign", ""),
                sun_sign=sun_data.get("sign", ""),
                ascendant=chart_result.get("ascendant", {}).get("sign", ""),
                nakshatra=moon_data.get("nakshatra", ""),
                current_dasha=f"{chart_result.get('dasha', {}).get('mahadasha', '')}/{chart_result.get('dasha', {}).get('antardasha', '')}"
            )
            
            update_user_by_phone(phone, {"state": STATE_READY})
            
            return format_chart_message(chart_result, user.get("name", "Friend"))
            
        except Exception as e:
            logger.error(f"Error calculating chart: {e}")
            update_user_by_phone(phone, {"state": STATE_NEW})
            return "❌ Error calculating chart. Please try again with *CHART*"
    
    elif msg_lower in ["no", "n", "cancel"]:
        update_user_by_phone(phone, {"state": STATE_NEW})
        return "No problem! Reply *CHART* to start over."
    
    else:
        return "Please reply *YES* to confirm or *NO* to start over."


def handle_ready_user(phone: str, message: str, user: dict) -> str:
    """Handle user with chart - AI Chat mode! ✨"""
    msg_lower = message.lower().strip()
    
    # Check for commands
    if msg_lower == "chart":
        # Recalculate and show chart
        try:
            chart_result = calculate_birth_chart(
                date_str=user["birth_date"],
                time_str=user["birth_time"],
                lat=user["birth_lat"],
                lng=user["birth_lng"],
                place_name=user["birth_place"]
            )
            return format_chart_message(chart_result, user.get("name", "Friend"))
        except Exception as e:
            logger.error(f"Error: {e}")
            return "Error fetching chart. Please try again."
    
    elif msg_lower == "today":
        panchanga = get_today_panchanga(lat=user.get("birth_lat", 28.6139), lng=user.get("birth_lng", 77.2090))
        return format_panchanga_message(panchanga)
    
    elif msg_lower in ["newchart", "reset", "update"]:
        update_user_by_phone(phone, {"state": STATE_ASKING_NAME})
        return "Let's update your birth chart! 🌟\n\nWhat's your full name?"
    
    elif msg_lower == "help":
        return (
            "🌟 *Nakshatra Commands* 🌟\n\n"
            "*CHART* - View your birth chart\n"
            "*TODAY* - Today's panchanga\n"
            "*NEWCHART* - Update birth details\n"
            "*HELP* - This message\n\n"
            "Or just ask me anything:\n"
            "• Why am I having career troubles?\n"
            "• Is this good time for business?\n"
            "• What about my relationships?"
        )
    
    else:
        # AI CHAT MODE! 🔮
        try:
            # Calculate chart for context
            chart_result = calculate_birth_chart(
                date_str=user["birth_date"],
                time_str=user["birth_time"],
                lat=user["birth_lat"],
                lng=user["birth_lng"],
                place_name=user["birth_place"]
            )
            
            # Build UserChart
            user_chart = build_user_chart(user, chart_result)
            
            # Ask the AI! ✨
            response = ask_astrologer(message, user_chart)
            
            return response
            
        except Exception as e:
            logger.error(f"AI Error: {e}")
            return (
                "🙏 Sorry, I had trouble with that. Try asking differently.\n\n"
                "Examples:\n"
                "• What careers suit me?\n"
                "• How's my love life?\n"
                "• Why am I facing obstacles?"
            )


# =============================================================================
# MAIN HANDLER
# =============================================================================

def handle_whatsapp_message(phone: str, message: str) -> str:
    """
    Main entry point for WhatsApp messages
    Returns response text
    """
    phone = normalize_phone(phone)
    
    # Get or create user
    user = get_or_create_user_by_phone(phone)
    state = user.get("state", STATE_NEW)
    
    logger.info(f"WhatsApp from {phone}, state={state}, msg={message[:50]}")
    
    # Route based on state
    if state == STATE_ASKING_NAME:
        return handle_asking_name(phone, message, user)
    
    elif state == STATE_ASKING_DATE:
        return handle_asking_date(phone, message, user)
    
    elif state == STATE_ASKING_TIME:
        return handle_asking_time(phone, message, user)
    
    elif state == STATE_ASKING_PLACE:
        return handle_asking_place(phone, message, user)
    
    elif state == STATE_CONFIRMING:
        return handle_confirming(phone, message, user)
    
    elif state == STATE_READY and user.get("birth_date"):
        return handle_ready_user(phone, message, user)
    
    else:
        return handle_new_user(phone, message, user)


# =============================================================================
# WEBHOOK HANDLER (for FastAPI)
# =============================================================================

async def process_whatsapp_webhook(form_data: dict) -> str:
    """
    Process incoming Twilio webhook
    Returns TwiML response
    """
    from_number = form_data.get("From", "")
    body = form_data.get("Body", "").strip()
    
    logger.info(f"Webhook: From={from_number}, Body={body[:50]}")
    
    # Get response
    response_text = handle_whatsapp_message(from_number, body)
    
    # Create TwiML response
    twiml = MessagingResponse()
    twiml.message(response_text)
    
    return str(twiml)