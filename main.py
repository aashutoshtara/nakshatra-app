from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import JSONResponse
import re
from datetime import datetime

from services.database import get_or_create_user, update_user, get_all_ready_users
from services.whatsapp import send_message
from services.astrology import calculate_birth_chart, get_today_panchang
from services.ai import generate_daily_guidance, handle_user_query

app = FastAPI(title="nakshatra-app")


# ============== WEBHOOK ==============

@app.post("/webhook")
async def webhook(request: Request, background_tasks: BackgroundTasks):
    """Receive WhatsApp messages from Wati"""
    
    try:
        body = await request.json()
        
        # Extract message
        phone = body.get("waId", "")
        text = body.get("text", "").strip()
        
        if not phone or not text:
            return JSONResponse({"status": "ignored"})
        
        # Process in background
        background_tasks.add_task(process_message, phone, text)
        
        return JSONResponse({"status": "ok"})
    
    except Exception as e:
        print(f"Webhook error: {e}")
        return JSONResponse({"status": "error"})


async def process_message(phone: str, text: str):
    """Process message based on user state"""
    
    user = await get_or_create_user(phone)
    state = user.get("state", "NEW")
    
    print(f"📩 {phone} ({state}): {text}")
    
    if state in ["NEW", "AWAITING_NAME"]:
        if state == "NEW":
            await send_message(phone, 
                "🙏 *Namaste! Welcome to Nakshatra!*\n\n"
                "I'm your personal Vedic astrology guide.\n\n"
                "What's your *name*?"
            )
            await update_user(phone, {"state": "AWAITING_NAME"})
        else:
            name = text.strip().title()
            await update_user(phone, {"name": name, "state": "AWAITING_DOB"})
            await send_message(phone,
                f"Nice to meet you, *{name}*! ✨\n\n"
                "What's your *date of birth*?\n\n"
                "Format: DD-MM-YYYY\n"
                "Example: 15-03-1992"
            )
    
    elif state == "AWAITING_DOB":
        match = re.match(r'(\d{1,2})[-/](\d{1,2})[-/](\d{4})', text)
        if not match:
            await send_message(phone, "Please enter date as DD-MM-YYYY\n\nExample: 15-03-1992")
            return
        
        day, month, year = match.groups()
        dob = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        
        await update_user(phone, {"dob": dob, "state": "AWAITING_TIME_CHOICE"})
        await send_message(phone,
            "Got it! 📝\n\n"
            "Do you know your *exact birth time*?\n\n"
            "1️⃣ Yes\n"
            "2️⃣ No / Not sure\n\n"
            "Reply 1 or 2"
        )
    
    elif state == "AWAITING_TIME_CHOICE":
        if text in ["1", "yes", "Yes"]:
            await update_user(phone, {"state": "AWAITING_TIME_INPUT"})
            await send_message(phone, "What time were you born?\n\nExample: 5:30 AM or 17:30")
        else:
            await update_user(phone, {"birth_time": "12:00:00", "state": "AWAITING_CITY"})
            await send_message(phone, "No problem! Where were you *born*?\n\nExample: Mumbai, Delhi, Jaipur")
    
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
        await send_message(phone, "Where were you *born*?\n\nExample: Mumbai, Delhi, Jaipur")
    
    elif state == "AWAITING_CITY":
        city = text.strip().title()
        await send_message(phone, "✨ Calculating your birth chart...")
        
        # Get user data
        user = await get_or_create_user(phone)
        dob = user.get("dob", "1990-01-01")
        birth_time = user.get("birth_time", "12:00:00")
        name = user.get("name", "Friend")
        
        # Calculate chart
        chart = await calculate_birth_chart(dob, birth_time, city)
        
        # Update user
        await update_user(phone, {
            "birth_city": city,
            "moon_sign": chart["moon_sign"],
            "nakshatra": chart["nakshatra"],
            "ascendant": chart["ascendant"],
            "state": "READY"
        })
        
        # Get panchang & generate guidance
        panchang = await get_today_panchang()
        guidance = await generate_daily_guidance(name, chart["moon_sign"], chart["nakshatra"], panchang)
        
        await send_message(phone,
            f"🌟 *Your Vedic Profile*\n\n"
            f"*Moon Sign:* {chart['moon_sign']}\n"
            f"*Nakshatra:* {chart['nakshatra']}\n"
            f"*Ascendant:* {chart['ascendant']}\n\n"
            f"━━━━━━━━━━━━━━\n\n"
            f"{guidance}\n\n"
            f"━━━━━━━━━━━━━━\n\n"
            f"You'll get daily guidance every morning!\n"
            f"Ask me anything anytime 🙏"
        )
    
    elif state == "READY":
        name = user.get("name", "Friend")
        moon_sign = user.get("moon_sign", "Mesha")
        nakshatra = user.get("nakshatra", "Ashwini")
        
        response = await handle_user_query(name, moon_sign, nakshatra, text)
        await send_message(phone, response)


# ============== BROADCAST ==============

@app.get("/broadcast")
async def broadcast(background_tasks: BackgroundTasks):
    """Send daily guidance to all users"""
    
    users = await get_all_ready_users()
    
    if not users:
        return {"status": "no_users"}
    
    background_tasks.add_task(send_broadcast, users)
    return {"status": "started", "count": len(users)}


async def send_broadcast(users: list):
    """Send to all users"""
    
    panchang = await get_today_panchang()
    
    for user in users:
        try:
            guidance = await generate_daily_guidance(
                user.get("name", "Friend"),
                user.get("moon_sign", "Mesha"),
                user.get("nakshatra", "Ashwini"),
                panchang
            )
            
            await send_message(
                user["phone"],
                f"🌅 *Good Morning, {user.get('name', 'Friend')}!*\n\n{guidance}"
            )
            
            import asyncio
            await asyncio.sleep(1)
            
        except Exception as e:
            print(f"Broadcast error for {user.get('phone')}: {e}")
    
    print(f"✅ Broadcast done: {len(users)} users")


# ============== HEALTH CHECK ==============

@app.get("/")
async def health():
    return {"status": "running", "app": "nakshatra-app"}


# ============== RUN ==============

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

