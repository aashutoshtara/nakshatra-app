import httpx
import asyncio
from dotenv import load_dotenv
import os

load_dotenv()

# Load all keys
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
PROKERALA_CLIENT_ID = os.getenv("PROKERALA_CLIENT_ID")  
PROKERALA_CLIENT_SECRET = os.getenv("PROKERALA_CLIENT_SECRET")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
WATI_API_KEY = os.getenv("WATI_API_KEY")
WATI_BASE_URL = os.getenv("WATI_BASE_URL")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

print("=" * 50)
print("🧪 JYOTISAATHI - SERVICE TESTS")
print("=" * 50)


# ============== TEST 1: SUPABASE ==============
def test_supabase():
    print("\n1️⃣ SUPABASE")
    print("-" * 30)
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Missing SUPABASE_URL or SUPABASE_KEY")
        return False
    
    print(f"   URL: {SUPABASE_URL[:40]}...")
    print(f"   Key: {SUPABASE_KEY[:20]}...")
    
    try:
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json"
        }
        
        response = httpx.get(
            f"{SUPABASE_URL}/rest/v1/users?limit=1",
            headers=headers
        )
        
        if response.status_code == 200:
            print("   ✅ Supabase connected!")
            return True
        else:
            print(f"   ❌ Error: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


# ============== TEST 2: ANTHROPIC (CLAUDE) ==============
def test_anthropic():
    print("\n2️⃣ ANTHROPIC (Claude AI)")
    print("-" * 30)
    
    if not ANTHROPIC_API_KEY:
        print("❌ Missing ANTHROPIC_API_KEY")
        return False
    
    print(f"   Key: {ANTHROPIC_API_KEY[:20]}...")
    
    try:
        response = httpx.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            },
            json={
                "model": "claude-3-5-haiku-20241022",
                "max_tokens": 50,
                "messages": [{"role": "user", "content": "Say 'Hello' in Hindi"}]
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            text = result["content"][0]["text"]
            print(f"   ✅ Claude says: {text[:50]}...")
            return True
        else:
            print(f"   ❌ Error: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


# ============== TEST 3: PROKERALA ==============
def test_prokerala():
    print("\n3️⃣ PROKERALA (Astrology)")
    print("-" * 30)
    
    if not PROKERALA_CLIENT_ID or not PROKERALA_CLIENT_SECRET:
        print("❌ Missing Prokerala credentials")
        return False
    
    print(f"   Client ID: {PROKERALA_CLIENT_ID[:20]}...")
    
    try:
        # Get token
        response = httpx.post(
            "https://api.prokerala.com/token",
            data={
                "grant_type": "client_credentials",
                "client_id": PROKERALA_CLIENT_ID,
                "client_secret": PROKERALA_CLIENT_SECRET
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            token = response.json().get("access_token")
            print(f"   ✅ Token received: {token[:20]}...")
            
            # Test panchang
            panchang_response = httpx.get(
                "https://api.prokerala.com/v2/astrology/panchang",
                params={
                    "ayanamsa": 1,
                    "coordinates": "28.6139,77.2090",
                    "datetime": "2025-01-01T12:00:00+05:30"
                },
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if panchang_response.status_code == 200:
                print("   ✅ Panchang API working!")
                return True
            else:
                print(f"   ❌ Panchang error: {panchang_response.status_code}")
                return False
        else:
            print(f"   ❌ Token error: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


# ============== TEST 4: GOOGLE MAPS ==============
def test_google_maps():
    print("\n4️⃣ GOOGLE MAPS (Geocoding)")
    print("-" * 30)
    
    if not GOOGLE_MAPS_API_KEY:
        print("❌ Missing GOOGLE_MAPS_API_KEY")
        return False
    
    print(f"   Key: {GOOGLE_MAPS_API_KEY[:15]}...")
    
    try:
        response = httpx.get(
            "https://maps.googleapis.com/maps/api/geocode/json",
            params={
                "address": "Mumbai, India",
                "key": GOOGLE_MAPS_API_KEY
            }
        )
        
        data = response.json()
        
        if data.get("status") == "OK":
            location = data["results"][0]["geometry"]["location"]
            print(f"   ✅ Mumbai: {location['lat']}, {location['lng']}")
            return True
        else:
            print(f"   ❌ Error: {data.get('status')}")
            print(f"   Message: {data.get('error_message', 'No details')}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


# ============== TEST 5: WATI ==============
def test_wati():
    print("\n5️⃣ WATI (WhatsApp)")
    print("-" * 30)
    
    if not WATI_API_KEY or not WATI_BASE_URL:
        print("❌ Missing WATI_API_KEY or WATI_BASE_URL")
        return False
    
    print(f"   URL: {WATI_BASE_URL}")
    print(f"   Key: {WATI_API_KEY[:30]}...")
    
    try:
        # Test API by getting contacts list
        response = httpx.get(
            f"{WATI_BASE_URL}/api/v1/getContacts",
            headers={
                "Authorization": f"Bearer {WATI_API_KEY}",
                "Content-Type": "application/json"
            },
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Wati API connected!")
            return True
        elif response.status_code == 401:
            print("   ❌ 401 Unauthorized - Check API key and Base URL")
            print(f"   Response: {response.text[:200]}")
            return False
        else:
            print(f"   ❌ Error: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


# ============== RUN ALL TESTS ==============
def run_all_tests():
    results = {
        "Supabase": test_supabase(),
        "Anthropic": test_anthropic(),
        "Prokerala": test_prokerala(),
        "Google Maps": test_google_maps(),
        "Wati": test_wati()
    }
    
    print("\n" + "=" * 50)
    print("📊 RESULTS SUMMARY")
    print("=" * 50)
    
    for service, passed in results.items():
        status = "✅ Pass" if passed else "❌ Fail"
        print(f"   {service}: {status}")
    
    passed_count = sum(results.values())
    total = len(results)
    
    print(f"\n   Total: {passed_count}/{total} services working")
    
    if passed_count == total:
        print("\n🎉 ALL SERVICES READY! You can deploy!")
    else:
        print("\n⚠️ Fix failing services before deploying")


# Run tests
if __name__ == "__main__":
    run_all_tests()