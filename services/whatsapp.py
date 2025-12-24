import httpx
import base64
from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER


async def send_message(phone: str, message: str) -> bool:
    """Send WhatsApp message via Twilio"""
    
    # Format phone number
    phone = phone.replace("+", "").replace(" ", "")
    if not phone.startswith("91"):
        phone = f"91{phone}"
    
    url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json"
    
    # Basic auth
    auth_string = base64.b64encode(
        f"{TWILIO_ACCOUNT_SID}:{TWILIO_AUTH_TOKEN}".encode()
    ).decode()
    
    headers = {
        "Authorization": f"Basic {auth_string}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    data = {
        "From": f"whatsapp:{TWILIO_WHATSAPP_NUMBER}",
        "To": f"whatsapp:+{phone}",
        "Body": message
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, data=data)
            print(f"📤 Message to {phone}: {response.status_code}")
            
            if response.status_code in [200, 201]:
                return True
            else:
                print(f"❌ Error: {response.text[:200]}")
                return False
                
    except Exception as e:
        print(f"❌ Twilio error: {e}")
        return False