import httpx
import base64
import os
from dotenv import load_dotenv

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

TEST_PHONE = "917722080160"  # Your number

print("🧪 TWILIO TEST")
print("=" * 40)
print(f"Account SID: {TWILIO_ACCOUNT_SID[:10]}...")
print(f"From: {TWILIO_WHATSAPP_NUMBER}")
print(f"To: {TEST_PHONE}")
print("=" * 40)

url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json"

auth_string = base64.b64encode(
    f"{TWILIO_ACCOUNT_SID}:{TWILIO_AUTH_TOKEN}".encode()
).decode()

headers = {
    "Authorization": f"Basic {auth_string}",
    "Content-Type": "application/x-www-form-urlencoded"
}

data = {
    "From": f"whatsapp:{TWILIO_WHATSAPP_NUMBER}",
    "To": f"whatsapp:+{TEST_PHONE}",
    "Body": "🧪 Test from Nakshatra!"
}

response = httpx.post(url, headers=headers, data=data)

print(f"\nStatus: {response.status_code}")
print(f"Response: {response.text[:300]}")

if response.status_code == 201:
    print("\n✅ SUCCESS! Check your WhatsApp!")
else:
    print("\n❌ Failed - Check error above")

