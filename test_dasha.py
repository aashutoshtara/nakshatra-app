import httpx
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

PROKERALA_CLIENT_ID = os.getenv("PROKERALA_CLIENT_ID")
PROKERALA_CLIENT_SECRET = os.getenv("PROKERALA_CLIENT_SECRET")

TEST_DOB = "1996-12-03"
TEST_TIME = "10:30:00"
TEST_LAT = 22.7196
TEST_LNG = 75.8577

def get_token():
    response = httpx.post(
        "https://api.prokerala.com/token",
        data={
            "grant_type": "client_credentials",
            "client_id": PROKERALA_CLIENT_ID,
            "client_secret": PROKERALA_CLIENT_SECRET
        }
    )
    return response.json()["access_token"]


def test_endpoints():
    print("🧪 TESTING CORRECT DASHA ENDPOINTS")
    print("=" * 60)
    
    token = get_token()
    datetime_str = f"{TEST_DOB}T{TEST_TIME}+05:30"
    coordinates = f"{TEST_LAT},{TEST_LNG}"
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: Kundli Advanced (includes Dasha)
    print("\n1️⃣ /v2/astrology/kundli/advanced")
    print("-" * 40)
    
    response = httpx.get(
        "https://api.prokerala.com/v2/astrology/kundli/advanced",
        params={
            "ayanamsa": 1,
            "coordinates": coordinates,
            "datetime": datetime_str
        },
        headers=headers,
        timeout=30
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ SUCCESS!")
        
        # Check for dasha data
        if "data" in data:
            d = data["data"]
            
            # Dasha Balance
            if "dasha_balance" in d:
                db = d["dasha_balance"]
                print(f"\n📅 DASHA BALANCE:")
                print(f"   Current Dasha Lord: {db.get('lord', {}).get('name', 'N/A')}")
                print(f"   Remaining: {db.get('description', 'N/A')}")
            
            # Dasha Periods
            if "dasha_periods" in d:
                print(f"\n📊 DASHA PERIODS:")
                now = datetime.now()
                
                for dasha in d["dasha_periods"]:
                    name = dasha.get("name", "Unknown")
                    start = dasha.get("start", "")
                    end = dasha.get("end", "")
                    
                    # Check if current
                    try:
                        start_dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
                        end_dt = datetime.fromisoformat(end.replace("Z", "+00:00"))
                        is_current = start_dt <= now.astimezone() <= end_dt
                        marker = " 👈 CURRENT" if is_current else ""
                    except:
                        marker = ""
                    
                    print(f"   {name}: {start[:10]} to {end[:10]}{marker}")
                    
                    # Show antardasha for current
                    if marker and "antardasha" in dasha:
                        print(f"\n   📍 Antardashas in {name} Mahadasha:")
                        for antar in dasha["antardasha"][:5]:  # First 5
                            a_name = antar.get("name", "Unknown")
                            a_start = antar.get("start", "")[:10]
                            a_end = antar.get("end", "")[:10]
                            print(f"      - {a_name}: {a_start} to {a_end}")
            else:
                print("❌ No dasha_periods in response")
                print(f"   Available keys: {list(d.keys())}")
    else:
        print(f"❌ Error: {response.text[:500]}")
    
    # Test 2: Dedicated Dasha endpoint
    print("\n" + "=" * 60)
    print("2️⃣ /v2/astrology/dasha-periods")
    print("-" * 40)
    
    response = httpx.get(
        "https://api.prokerala.com/v2/astrology/dasha-periods",
        params={
            "ayanamsa": 1,
            "coordinates": coordinates,
            "datetime": datetime_str
        },
        headers=headers,
        timeout=30
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ SUCCESS!")
        print(f"\nResponse structure:")
        print(json.dumps(data, indent=2)[:2000])
    else:
        print(f"❌ Error: {response.text[:500]}")


if __name__ == "__main__":
    test_endpoints()