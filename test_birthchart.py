import httpx
import os
import json
from dotenv import load_dotenv

load_dotenv()

PROKERALA_CLIENT_ID = os.getenv("PROKERALA_CLIENT_ID")
PROKERALA_CLIENT_SECRET = os.getenv("PROKERALA_CLIENT_SECRET")

# Your birth details for testing
TEST_DOB = "1996-12-03"       # Change to YOUR DOB (YYYY-MM-DD)
TEST_TIME = "18:35:00"        # Change to YOUR birth time
TEST_LAT = 20.884327            # Change to your birth city lat
TEST_LNG = 76.202608          # Change to your birth city lng

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

def test_birth_chart():
    print("🧪 BIRTH CHART DEBUG TEST")
    print("=" * 50)
    print(f"DOB: {TEST_DOB}")
    print(f"Time: {TEST_TIME}")
    print(f"Coordinates: {TEST_LAT}, {TEST_LNG}")
    print("=" * 50)
    
    token = get_token()
    datetime_str = f"{TEST_DOB}T{TEST_TIME}+05:30"
    
    print(f"\n📤 Calling Prokerala API...")
    print(f"   Datetime: {datetime_str}")
    
    response = httpx.get(
        "https://api.prokerala.com/v2/astrology/kundli",
        params={
            "ayanamsa": 1,
            "coordinates": f"{TEST_LAT},{TEST_LNG}",
            "datetime": datetime_str
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print(f"\n📥 Response Status: {response.status_code}")
    
    data = response.json()
    
    # Pretty print full response
    print(f"\n📋 FULL API RESPONSE:")
    print("-" * 50)
    print(json.dumps(data, indent=2)[:3000])  # First 3000 chars
    print("-" * 50)
    
    # Try to extract key fields
    if "data" in data:
        chart = data["data"]
        
        print(f"\n🔍 EXTRACTED FIELDS:")
        print(f"   Keys in data: {list(chart.keys())}")
        
        # Check different possible field names
        possible_rashi_fields = ["rasi", "rashi", "moon_sign", "moon_rasi", "chandra_rasi"]
        possible_nakshatra_fields = ["nakshatra", "birth_nakshatra", "chandra_nakshatra"]
        possible_ascendant_fields = ["ascendant", "lagna", "rising_sign"]
        
        print(f"\n🌙 Looking for Moon Sign (Rashi):")
        for field in possible_rashi_fields:
            if field in chart:
                print(f"   Found '{field}': {chart[field]}")
        
        print(f"\n⭐ Looking for Nakshatra:")
        for field in possible_nakshatra_fields:
            if field in chart:
                print(f"   Found '{field}': {chart[field]}")
        
        print(f"\n🌅 Looking for Ascendant:")
        for field in possible_ascendant_fields:
            if field in chart:
                print(f"   Found '{field}': {chart[field]}")
        
        # Also check nested structures
        print(f"\n📊 Checking for nested 'nakshatra_details' or similar:")
        for key, value in chart.items():
            if isinstance(value, dict):
                print(f"   {key} (dict): {list(value.keys()) if value else 'empty'}")
            elif isinstance(value, list) and value:
                print(f"   {key} (list): {value[0] if value else 'empty'}")

# Run test
test_birth_chart()