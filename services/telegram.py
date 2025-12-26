import httpx
from config import TELEGRAM_BOT_TOKEN

BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}" if TELEGRAM_BOT_TOKEN else ""


async def send_telegram_message(chat_id: str, message: str) -> bool:
    """Send Telegram message"""
    
    if not TELEGRAM_BOT_TOKEN:
        print("⚠️ Telegram not configured - skipping")
        return False
    
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            # Try with Markdown first
            response = await client.post(
                f"{BASE_URL}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": message,
                    "parse_mode": "Markdown"
                }
            )
            
            # If Markdown fails, try without formatting
            if response.status_code != 200:
                print(f"⚠️ Markdown failed, trying plain text...")
                response = await client.post(
                    f"{BASE_URL}/sendMessage",
                    json={
                        "chat_id": chat_id,
                        "text": message.replace("*", "").replace("_", "")
                    }
                )
            
            print(f"📤 Telegram to {chat_id}: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ Telegram API error: {response.text}")
            
            return response.status_code == 200
            
    except httpx.TimeoutException:
        print(f"❌ Telegram timeout - server slow")
        return False
    except Exception as e:
        print(f"❌ Telegram error: {type(e).__name__}: {e}")
        return False