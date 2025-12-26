import httpx
from config import TELEGRAM_BOT_TOKEN

BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"


async def send_telegram_message(chat_id: str, message: str) -> bool:
    """Send Telegram message"""
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": message,
                    "parse_mode": "Markdown"
                }
            )
            print(f"📤 Telegram to {chat_id}: {response.status_code}")
            return response.status_code == 200
    except Exception as e:
        print(f"❌ Telegram error: {e}")
        return False