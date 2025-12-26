from fastapi import FastAPI, Request, BackgroundTasks, Form
from fastapi.responses import PlainTextResponse, JSONResponse
from typing import Optional
import re

from services.database import get_or_create_user, update_user, get_all_ready_users
from services.whatsapp import send_message
from services.telegram import send_telegram_message  # ← ADD THIS
from services.astrology import calculate_birth_chart, get_today_panchang
from services.geocoding import search_cities
from services.ai import generate_daily_guidance, handle_user_query

app = FastAPI(title="nakshatra-app")

# Common greetings to ignore as names
GREETINGS = [
    "hi", "hello", "hey", "hii", "hiii", "hiiii", "namaste", "namaskar", 
    "hola", "start", "begin", "help", "menu", "reset", "restart",
    "yo", "sup", "helo", "hllo", "hy", "good morning", "good evening",
    "/start"
]


# ============== TWILIO WHATSAPP WEBHOOK ==============

@app.post("/webhook")
async def webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    From: Optional[str] = Form(None),
    Body: Optional[str] = Form(None)
):
    """Receive WhatsApp messages from Twilio"""
    
    try:
        phone = From.replace("whatsapp:", "").replace("+", "") if From else ""
        text = Body.strip() if Body else ""
        
        print(f"🔍 WhatsApp Received - Phone: {phone}, Text: {text}")
        
        if not phone or not text:
            return PlainTextResponse("")
        
        background_tasks.add_task(process_message, phone, text, "whatsapp")
        return PlainTextResponse("")
    
    except Exception as e:
        print(f"❌ WhatsApp Webhook error: {e}")
        return PlainTextResponse("")


# ============== TELEGRAM WEBHOOK ==============

@app.post("/telegram")
async def telegram_webhook(request: Request, background_tasks: BackgroundTasks):
    """Receive Telegram messages"""
    
    try:
        body = await request.json()
        print(f"🔍 Telegram Received: {body}")
        
        message = body.get("message", {})
        chat_id = str(message.get("chat", {}).get("id", ""))
        text = message.get("text", "").strip()
        
        if not chat_id or not text:
            return JSONResponse({"status": "ignored"})
        
        phone = f"TG_{chat_id}"
        
        background_tasks.add_task(process_message, phone, text, "telegram")
        return JSONResponse({"status": "ok"})
    
    except Exception as e:
        print(f"❌ Telegram Webhook error: {e}")
        return JSONResponse({"status": "error"})


# ============== MESSAGE PROCESSOR ==============

async def process_message(phone: str, text: str, platform: str = "whatsapp"):
    """Process message based on user state"""
    
    # Helper to reply on correct platform
    async def reply(message: str):
        if platform == "telegram":
            chat_id = phone.replace("TG_", "")
            await send_telegram_message(chat_id, message)
        else:
            await send_message(phone, message)
    
    user = await get_or_create_user(phone)
    state = user.get("state", "NEW")
    text_lower = text.lower().strip()
    
    print(f"📩 [{platform.upper()}] {phone} ({state}): {text}")
    
    # ===== RESET COMMAND =====
    if text_lower in ["reset", "restart", "start over"]:
        await update_user(phone, {
            "state": "NEW",
            "name": None,
            "gender": None,
            "dob": None,
            "birth_time": None,
            "birth_city": None,
            "moon_sign": None,
            "nakshatra": None,
            "ascendant": None
        })
        await reply(
            "🔄 Let's start fresh!\n\n"
            "🙏 *Namaste! Welcome to Nakshatra!*\n\n"
            "I'm your personal Vedic astrology guide.\n\n"
            "What's your *name*?"
        )
        await update_user(phone, {"state": "AWAITING_NAME"})
        return
    
    # ===== STATE: NEW =====
    if state == "NEW" or state is None:
        await reply(
            "🙏 *Namaste! Welcome to Nakshatra!*\n\n"
            "I'm your personal Vedic astrology guide.\n\n"
            "What's your *name*?"
        )
        await update_user(phone, {"state": "AWAITING_NAME"})
        return
    
    # ===== STATE: AWAITING_NAME =====
    elif state == "AWAITING_NAME":
        if text_lower in GREETINGS:
            await reply(
                "Please tell me your *actual name* 😊\n\n"
                "For example: Rahul, Priya, Amit"
            )
            return
        
        name = text.strip().title()
        
        if len(name) < 2:
            await reply(
                "Name too short. Please enter your full name.\n\n"
                "For example: Rahul, Priya, Amit"
            )
            return
        
        if not re.match(r'^[a-zA-Z\s]+$', name):
            await reply(
                "Please enter a valid name (letters only)\n\n"
                "For example: Rahul, Priya, Amit"
            )
            return
        
        await update_user(phone, {"name": name, "state": "AWAITING_GENDER"})
        await reply(
            f"Nice to meet you, *{name}*! ✨\n\n"
            "Are you:\n\n"
            "1️⃣ Male\n"
            "2️⃣ Female"
        )
        return
    
    # ===== STATE: AWAITING_GENDER ===== ← THIS WAS MISSING!
    elif state == "AWAITING_GENDER":
        if text_lower in ["1", "male", "m", "boy", "man", "ladka"]:
            gender = "male"
        elif text_lower in ["2", "female", "f", "girl", "woman", "ladki"]:
            gender = "female"
        else:
            await reply(
                "Please reply:\n\n"
                "1️⃣ for Male\n"
                "2️⃣ for Female"
            )
            return
        
        await update_user(phone, {"gender": gender, "state": "AWAITING_DOB"})
        await reply(
            "What's your *date of birth*?\n\n"
            "Format: DD-MM-YYYY\n"
            "Example: 15-03-1992"
        )
        return
    
    # ===== STATE: AWAITING_DOB =====
    elif state == "AWAITING_DOB":
        match = re.match(r'(\d{1,2})[-/](\d{1,2})[-/](\d{4})', text)
        if not match:
            await reply(
                "Please enter date as *DD-MM-YYYY*\n\n"
                "Example: 15-03-1992"
            )
            return
        
        day, month, year = match.groups()
        
        try:
            day_int, month_int, year_int = int(day), int(month), int(year)
            if not (1 <= day_int <= 31 and 1 <= month_int <= 12 and 1900 <= year_int <= 2025):
                raise ValueError("Invalid date")
        except:
            await reply("Please enter a valid date\n\nExample: 15-03-1992")
            return
        
        dob = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        
        await update_user(phone, {"dob": dob, "state": "AWAITING_TIME_CHOICE"})
        await reply(
            "Got it! 📝\n\n"
            "Do you know your *exact birth time*?\n\n"
            "1️⃣ Yes\n"
            "2️⃣ No / Not sure\n\n"
            "Reply 1 or 2"
        )
        return
    
    # ===== STATE: AWAITING_TIME_CHOICE =====
    elif state == "AWAITING_TIME_CHOICE":
        if text_lower in ["1", "yes", "haan", "ha"]:
            await update_user(phone, {"state": "AWAITING_TIME_INPUT"})
            await reply(
                "What time were you born?\n\n"
                "Example: 5:30 AM or 17:30"
            )
        else:
            await update_user(phone, {"birth_time": "12:00:00", "state": "AWAITING_CITY"})
            await reply(
                "No problem! 👍\n\n"
                "Where were you *born*? (City name)\n\n"
                "Example: Indore, Varanasi, Pune"
            )
        return
    
    # ===== STATE: AWAITING_TIME_INPUT =====
    elif state == "AWAITING_TIME_INPUT":
        time_str = "12:00:00"
        match = re.match(r'(\d{1,2}):?(\d{2})?\s*(am|pm|AM|PM)?', text)
        if match:
            hours = int(match.group(1))
            mins = match.group(2) or "00"
            period = match.group(3)
            if period and period.lower() == "pm" and hours < 12:
                hours += 12
            if period and period.lower() == "am" and hours == 12:
                hours = 0
            time_str = f"{hours:02d}:{mins}:00"
        
        await update_user(phone, {"birth_time": time_str, "state": "AWAITING_CITY"})
        await reply(
            "Where were you *born*? (City name)\n\n"
            "Example: Indore, Varanasi, Pune"
        )
        return
    
    # ===== STATE: AWAITING_CITY =====
    elif state == "AWAITING_CITY":
        city_input = text.strip().title()
        
        city_options = await search_cities(city_input)
        
        if not city_options:
            await reply(
                f"Couldn't find *{city_input}*. 🤔\n\n"
                "Please try:\n"
                "• Check spelling\n"
                "• Enter nearest big city\n"
                "• Add state name (e.g., Indore MP)"
            )
            return
        
        if len(city_options) == 1:
            city = city_options[0]
            await update_user(phone, {
                "pending_city": city["name"],
                "pending_lat": city["lat"],
                "pending_lng": city["lng"],
                "state": "AWAITING_CITY_CONFIRM"
            })
            await reply(
                f"📍 Found: *{city['name']}*\n\n"
                "Is this correct?\n\n"
                "1️⃣ Yes\n"
                "2️⃣ No, search again"
            )
        else:
            options_text = "📍 *Multiple locations found:*\n\n"
            for i, city in enumerate(city_options[:5], 1):
                options_text += f"{i}️⃣ {city['name']}\n"
            
            options_text += "\nReply with the number (1-5)"
            
            await update_user(phone, {
                "pending_cities": city_options[:5],
                "state": "AWAITING_CITY_SELECT"
            })
            await reply(options_text)
        return
    
    # ===== STATE: AWAITING_CITY_SELECT =====
    elif state == "AWAITING_CITY_SELECT":
        try:
            selection = int(text.strip())
            pending_cities = user.get("pending_cities", [])
            
            if 1 <= selection <= len(pending_cities):
                city = pending_cities[selection - 1]
                await update_user(phone, {
                    "pending_city": city["name"],
                    "pending_lat": city["lat"],
                    "pending_lng": city["lng"],
                    "state": "AWAITING_CITY_CONFIRM"
                })
                await reply(
                    f"📍 You selected: *{city['name']}*\n\n"
                    "Is this correct?\n\n"
                    "1️⃣ Yes\n"
                    "2️⃣ No, search again"
                )
            else:
                await reply("Please reply with a number from the list (1-5)")
        except:
            await reply("Please reply with a number (1-5)")
        return
    
    # ===== STATE: AWAITING_CITY_CONFIRM =====
    elif state == "AWAITING_CITY_CONFIRM":
        if text_lower in ["1", "yes", "haan", "ha", "correct", "sahi"]:
            await reply("✨ Calculating your birth chart...")
            
            user = await get_or_create_user(phone)
            city = user.get("pending_city", "Delhi")
            lat = user.get("pending_lat", 28.6139)
            lng = user.get("pending_lng", 77.2090)
            dob = user.get("dob", "1990-01-01")
            birth_time = user.get("birth_time", "12:00:00")
            name = user.get("name", "Friend")
            gender = user.get("gender", "male")
            
            chart = await calculate_birth_chart(dob, birth_time, city, lat, lng)
            
            await update_user(phone, {
                "birth_city": city,
                "latitude": lat,
                "longitude": lng,
                "moon_sign": chart["moon_sign"],
                "nakshatra": chart["nakshatra"],
                "ascendant": chart["ascendant"],
                "state": "READY",
                "pending_city": None,
                "pending_lat": None,
                "pending_lng": None,
                "pending_cities": None
            })
            
            panchang = await get_today_panchang()
            guidance = await generate_daily_guidance(
                name, 
                chart["moon_sign"], 
                chart["nakshatra"], 
                gender,
                panchang
            )
            
            await reply(
                f"🌟 *Your Vedic Profile*\n\n"
                f"*Name:* {name}\n"
                f"*Moon Sign:* {chart['moon_sign']}\n"
                f"*Nakshatra:* {chart['nakshatra']}\n"
                f"*Ascendant:* {chart['ascendant']}\n\n"
                f"━━━━━━━━━━━━━━\n\n"
                f"{guidance}\n\n"
                f"━━━━━━━━━━━━━━\n\n"
                f"Ask me anything anytime! 🙏\n\n"
                f"_Type 'reset' to start over_"
            )
        else:
            await update_user(phone, {"state": "AWAITING_CITY"})
            await reply(
                "No problem! Enter your birth city again:\n\n"
                "💡 Tip: Add state name for better results\n"
                "Example: Indore MP, Varanasi UP"
            )
        return
    
    # ===== STATE: READY =====
    elif state == "READY":
        name = user.get("name", "Friend")
        gender = user.get("gender", "male")
        moon_sign = user.get("moon_sign", "Mesha")
        nakshatra = user.get("nakshatra", "Ashwini")
        
        response = await handle_user_query(name, moon_sign, nakshatra, gender, text)
        await reply(response)
        return


# ============== HEALTH CHECK ==============

@app.get("/")
async def health():
    return {"status": "running", "app": "Nakshatra Bot", "platforms": ["whatsapp", "telegram"]}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)