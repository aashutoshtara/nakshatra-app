import httpx
import os
from dotenv import load_dotenv

load_dotenv()

WATI_API_KEY = os.getenv("WATI_API_KEY")
WATI_BASE_URL = os.getenv("WATI_BASE_URL")

TEST_PHONE = "917722080160"

print("🧪 WATI API TESTS")
print("=" * 50)

headers = {
    "Authorization": f"Bearer {WATI_API_KEY}",
    "Content-Type": "application/json"
}

# Test 1: Check contact exists
print("\n1️⃣ Checking contact...")
response = httpx.get(
    f"{WATI_BASE_URL}/api/v1/getContacts",
    headers=headers,
    timeout=10
)
print(f"   Status: {response.status_code}")

# Test 2: Get contact by phone
print("\n2️⃣ Getting contact info...")
response = httpx.get(
    f"{WATI_BASE_URL}/api/v1/getContactInfo/{TEST_PHONE}",
    headers=headers,
    timeout=10
)
print(f"   Status: {response.status_code}")
print(f"   Response: {response.text[:200] if response.text else 'Empty'}")

# Test 3: Try session message with different payload
print("\n3️⃣ Sending session message...")
response = httpx.post(
    f"{WATI_BASE_URL}/api/v1/sendSessionMessage/{TEST_PHONE}",
    headers=headers,
    json={"messageText": "Test from bot"},
    timeout=10
)
print(f"   Status: {response.status_code}")
print(f"   Response: {response.text[:200] if response.text else 'Empty'}")

# Test 4: Try interactive message
print("\n4️⃣ Sending interactive message...")
response = httpx.post(
    f"{WATI_BASE_URL}/api/v1/sendInteractiveButtonsMessage",
    headers=headers,
    params={"whatsappNumber": TEST_PHONE},
    json={
        "body": "Test message",
        "buttons": [{"text": "OK"}]
    },
    timeout=10
)
print(f"   Status: {response.status_code}")
print(f"   Response: {response.text[:200] if response.text else 'Empty'}")

# Test 5: Check session status
print("\n5️⃣ Getting messages...")
response = httpx.get(
    f"{WATI_BASE_URL}/api/v1/getMessages/{TEST_PHONE}",
    headers=headers,
    timeout=10
)
print(f"   Status: {response.status_code}")
print(f"   Response: {response.text[:300] if response.text else 'Empty'}")