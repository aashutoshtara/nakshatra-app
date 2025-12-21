import httpx
from config import WATI_API_KEY, WATI_BASE_URL


async def send_message(phone: str, message: str) -> bool:
    """Send WhatsApp message via Wati.io"""
    
    # Remove + if present
    phone = phone.replace("+", "")
    
    url = f"{WATI_BASE_URL}/api/v1/sendSessionMessage/{phone}"
    
    headers = {
        "Authorization": f"Bearer {WATI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {"messageText": message}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            print(f"📤 Message to {phone}: {response.status_code}")
            return response.status_code == 200
    except Exception as e:
        print(f"❌ WhatsApp error: {e}")
        return False