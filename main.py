"""
Nakshatra - AI Vedic Astrologer
Main FastAPI Application

Run locally:
    python main.py

Run with uvicorn:
    uvicorn main:app --reload --port 8000
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse, JSONResponse

from config import TELEGRAM_BOT_TOKEN, WEBHOOK_URL, DEBUG

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# =============================================================================
# LIFESPAN (Startup/Shutdown)
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown"""
    logger.info("🚀 Starting Nakshatra...")
    
    # Initialize Telegram bot
    try:
        from services.telegram import create_telegram_bot
        app.state.telegram_bot = create_telegram_bot()
        await app.state.telegram_bot.initialize()
        
        # Set webhook if URL configured
        if WEBHOOK_URL:
            webhook_url = f"{WEBHOOK_URL}/webhook/telegram"
            await app.state.telegram_bot.bot.set_webhook(webhook_url)
            logger.info(f"✅ Telegram webhook set: {webhook_url}")
        else:
            logger.info("⚠️ No WEBHOOK_URL set - Telegram webhook not configured")
            
    except Exception as e:
        logger.error(f"❌ Failed to initialize Telegram: {e}")
        app.state.telegram_bot = None
    
    # Test VedAstro data
    try:
        from data.vedastro import vedastro
        test = vedastro.get_planet_in_sign("Sun", "Aries")
        if test:
            logger.info("✅ VedAstro data loaded")
        else:
            logger.warning("⚠️ VedAstro data might not be loaded correctly")
    except Exception as e:
        logger.error(f"❌ VedAstro error: {e}")
    
    # Test database connection
    try:
        from services.database import get_user_by_phone
        logger.info("✅ Database module loaded")
    except Exception as e:
        logger.error(f"❌ Database error: {e}")
    
    logger.info("🌟 Nakshatra is ready!")
    
    yield  # App runs here
    
    # Shutdown
    logger.info("👋 Shutting down Nakshatra...")
    if hasattr(app.state, 'telegram_bot') and app.state.telegram_bot:
        await app.state.telegram_bot.shutdown()


# =============================================================================
# FASTAPI APP
# =============================================================================

app = FastAPI(
    title="Nakshatra",
    description="AI Vedic Astrologer - Telegram & WhatsApp Bot",
    version="1.0.0",
    lifespan=lifespan
)


# =============================================================================
# HEALTH ENDPOINTS
# =============================================================================

@app.get("/")
async def root():
    """Health check"""
    return {"status": "ok", "service": "Nakshatra AI Astrologer"}


@app.get("/health")
async def health():
    """Detailed health check"""
    status = {
        "status": "healthy",
        "service": "Nakshatra",
        "components": {}
    }
    
    # Check Telegram
    if hasattr(app.state, 'telegram_bot') and app.state.telegram_bot:
        status["components"]["telegram"] = "connected"
    else:
        status["components"]["telegram"] = "not configured"
    
    # Check VedAstro
    try:
        from data.vedastro import vedastro
        test = vedastro.get_planet_in_sign("Moon", "Cancer")
        status["components"]["vedastro"] = "loaded" if test else "error"
    except:
        status["components"]["vedastro"] = "error"
    
    # Check Database
    try:
        from services.database import supabase
        status["components"]["database"] = "connected" if supabase else "not configured"
    except:
        status["components"]["database"] = "error"
    
    return status


# =============================================================================
# TELEGRAM WEBHOOK
# =============================================================================

@app.post("/webhook/telegram")
async def telegram_webhook(request: Request):
    """Handle Telegram webhook"""
    try:
        if not hasattr(app.state, 'telegram_bot') or not app.state.telegram_bot:
            logger.error("Telegram bot not initialized")
            return JSONResponse({"status": "error", "message": "Bot not initialized"})
        
        # Get update data
        data = await request.json()
        logger.debug(f"Telegram update: {data}")
        
        # Process update
        from telegram import Update
        update = Update.de_json(data, app.state.telegram_bot.bot)
        await app.state.telegram_bot.process_update(update)
        
        return JSONResponse({"status": "ok"})
        
    except Exception as e:
        logger.error(f"Telegram webhook error: {e}")
        return JSONResponse({"status": "error", "message": str(e)})


# =============================================================================
# WHATSAPP WEBHOOK
# =============================================================================

@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    """Handle Twilio WhatsApp webhook"""
    try:
        # Parse form data
        form_data = await request.form()
        form_dict = dict(form_data)
        
        logger.debug(f"WhatsApp webhook: {form_dict}")
        
        # Process message
        from services.whatsapp import process_whatsapp_webhook
        twiml_response = await process_whatsapp_webhook(form_dict)
        
        return PlainTextResponse(twiml_response, media_type="application/xml")
        
    except Exception as e:
        logger.error(f"WhatsApp webhook error: {e}")
        # Return empty TwiML on error
        return PlainTextResponse(
            '<?xml version="1.0" encoding="UTF-8"?><Response></Response>',
            media_type="application/xml"
        )


# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.get("/api/v1/panchanga")
async def get_panchanga(lat: float = 28.6139, lng: float = 77.2090):
    """Get today's panchanga for a location"""
    try:
        from services.astrology import get_today_panchanga
        panchanga = get_today_panchanga(lat=lat, lng=lng)
        return {"status": "success", "data": panchanga}
    except Exception as e:
        logger.error(f"Panchanga error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/chart")
async def calculate_chart(
    date: str,
    time: str,
    lat: float,
    lng: float,
    place: str = "Unknown"
):
    """
    Calculate birth chart
    
    Args:
        date: YYYY-MM-DD
        time: HH:MM
        lat: Latitude
        lng: Longitude
        place: Place name
    """
    try:
        from services.astrology import calculate_birth_chart
        chart = calculate_birth_chart(
            date_str=date,
            time_str=time,
            lat=lat,
            lng=lng,
            place_name=place
        )
        return {"status": "success", "data": chart}
    except Exception as e:
        logger.error(f"Chart calculation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/ask")
async def ask_astrologer_api(
    question: str,
    name: str,
    birth_date: str,
    birth_time: str,
    birth_place: str,
    lat: float,
    lng: float
):
    """
    Ask the AI astrologer a question
    
    This calculates the chart and returns an AI-powered response.
    """
    try:
        from services.astrology import calculate_birth_chart
        from services.ai_astrologer import ask_astrologer, UserChart
        
        # Calculate chart
        chart_result = calculate_birth_chart(
            date_str=birth_date,
            time_str=birth_time,
            lat=lat,
            lng=lng,
            place_name=birth_place
        )
        
        # Build planets dict
        planets = {}
        for p in chart_result.get("planets", []):
            planets[p["planet"]] = p["sign"]
        
        # Get moon data
        moon_data = next((p for p in chart_result.get("planets", []) if p["planet"] == "Moon"), {})
        sun_data = next((p for p in chart_result.get("planets", []) if p["planet"] == "Sun"), {})
        
        # Build user chart
        user_chart = UserChart(
            name=name,
            birth_date=birth_date,
            birth_time=birth_time,
            birth_place=birth_place,
            ascendant=chart_result.get("ascendant", {}).get("sign", ""),
            moon_sign=moon_data.get("sign", ""),
            sun_sign=sun_data.get("sign", ""),
            nakshatra=moon_data.get("nakshatra", ""),
            planets=planets,
            current_mahadasha=chart_result.get("dasha", {}).get("mahadasha", ""),
            current_antardasha=chart_result.get("dasha", {}).get("antardasha", ""),
        )
        
        # Ask AI
        response = ask_astrologer(question, user_chart)
        
        return {
            "status": "success",
            "question": question,
            "response": response,
            "chart_summary": {
                "ascendant": user_chart.ascendant,
                "moon_sign": user_chart.moon_sign,
                "sun_sign": user_chart.sun_sign,
                "nakshatra": user_chart.nakshatra,
                "current_dasha": f"{user_chart.current_mahadasha}/{user_chart.current_antardasha}"
            }
        }
        
    except Exception as e:
        logger.error(f"Ask API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/interpretation/{prediction_name}")
async def get_interpretation(prediction_name: str):
    """
    Get VedAstro interpretation by name
    
    Examples:
        /api/v1/interpretation/SunInAries
        /api/v1/interpretation/House7LordInHouse1
    """
    try:
        from data.vedastro import vedastro
        result = vedastro.get_prediction(prediction_name)
        
        if result:
            return {"status": "success", "data": result}
        else:
            raise HTTPException(status_code=404, detail="Prediction not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Interpretation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/search")
async def search_interpretations(q: str, tag: str = None):
    """
    Search VedAstro interpretations
    
    Args:
        q: Search keyword
        tag: Optional tag filter (Yoga, Travel, Marriage, etc.)
    """
    try:
        from data.vedastro import vedastro
        
        if tag:
            results = vedastro.search_by_tag(tag)
            # Filter by keyword if provided
            if q:
                q_lower = q.lower()
                results = [r for r in results if q_lower in r.get("description", "").lower()]
        else:
            results = vedastro.search_description(q)
        
        return {
            "status": "success",
            "query": q,
            "tag": tag,
            "count": len(results),
            "results": results[:20]  # Limit to 20
        }
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# RUN SERVER
# =============================================================================

if __name__ == "__main__":
    import sys
    
    print("""
    ╔═══════════════════════════════════════════╗
    ║     🌟 NAKSHATRA - AI Vedic Astrologer     ║
    ╠═══════════════════════════════════════════╣
    ║  Telegram + WhatsApp + REST API            ║
    ║  Powered by Claude AI + VedAstro           ║
    ╚═══════════════════════════════════════════╝
    """)
    
    if "--polling" in sys.argv:
        # =================================================================
        # LOCAL TESTING - Polling Mode
        # =================================================================
        print("🔄 Starting in POLLING mode (local testing)...")
        print("   Press Ctrl+C to stop\n")
        
        import asyncio
        from services.telegram import create_telegram_bot
        
        async def run_polling():
            # Create bot
            bot_app = create_telegram_bot()
            
            # Initialize
            await bot_app.initialize()
            await bot_app.start()
            
            # Delete any existing webhook
            await bot_app.bot.delete_webhook()
            
            # Start polling
            await bot_app.updater.start_polling(drop_pending_updates=True)
            
            print("🌟 Nakshatra Bot is running!")
            print("   Send /start to your bot on Telegram\n")
            
            # Keep running until Ctrl+C
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                print("\n👋 Shutting down...")
            finally:
                await bot_app.updater.stop()
                await bot_app.stop()
                await bot_app.shutdown()
        
        asyncio.run(run_polling())
    
    else:
        # =================================================================
        # PRODUCTION - Webhook Mode
        # =================================================================
        import uvicorn
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=DEBUG
        )