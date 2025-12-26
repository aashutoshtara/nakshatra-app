import httpx
from datetime import datetime, timezone, timedelta
from config import PROKERALA_CLIENT_ID, PROKERALA_CLIENT_SECRET
from typing import Dict, Any

# Token cache
_token_cache = {"token": None, "expires_at": None}

# Panchang cache (shared across all users)
_panchang_cache = {"date": None, "data": None}

# Indian Standard Time
IST = timezone(timedelta(hours=5, minutes=30))


async def get_token() -> str:
    """Get Prokerala access token (cached for ~50 mins)"""
    
    if _token_cache["token"] and _token_cache["expires_at"]:
        if datetime.now().timestamp() < _token_cache["expires_at"]:
            return _token_cache["token"]
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.prokerala.com/token",
            data={
                "grant_type": "client_credentials",
                "client_id": PROKERALA_CLIENT_ID,
                "client_secret": PROKERALA_CLIENT_SECRET
            }
        )
        result = response.json()
    
    _token_cache["token"] = result["access_token"]
    _token_cache["expires_at"] = datetime.now().timestamp() + 3000
    
    return result["access_token"]


def _default_chart() -> Dict[str, Any]:
    """Return default chart on error"""
    return {
        "moon_sign": "Mesha",
        "sun_sign": "Mesha",
        "nakshatra": "Ashwini",
        "nakshatra_pada": 1,
        "nakshatra_lord": "Ketu",
        "ascendant": "Mesha",
        "mangal_dosha": False,
        "mangal_dosha_desc": "",
        "current_dasha": "Unknown",
        "current_antardasha": "Unknown",
        "dasha_end_date": "Unknown",
        "antardasha_end_date": "Unknown",
        "deity": "Unknown",
        "gana": "Unknown",
        "lucky_color": "Unknown",
        "birth_stone": "Unknown",
        "lucky_direction": "Unknown",
        "syllables": "Unknown",
    }


def _default_panchang() -> Dict[str, Any]:
    """Return default panchang on error"""
    now = datetime.now(IST)
    return {
        "tithi": "Unknown",
        "tithi_paksha": "",
        "nakshatra": "Unknown",
        "nakshatra_lord": "Unknown",
        "yoga": "Unknown",
        "karana": "Unknown",
        "day": now.strftime("%A"),
        "date": now.strftime("%d %B %Y"),
        "sunrise": "",
        "sunset": "",
    }


async def calculate_birth_chart(
    dob: str,
    birth_time: str,
    lat: float = 28.6139,
    lng: float = 77.2090
) -> Dict[str, Any]:
    """
    Calculate complete birth chart with ONE API call.
    Uses /v2/astrology/kundli/advanced (300 credits)
    """
    
    try:
        token = await get_token()
        datetime_str = f"{dob}T{birth_time}+05:30"
        coordinates = f"{lat},{lng}"
        
        print(f"🔮 Calculating birth chart: {datetime_str}")
        
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                "https://api.prokerala.com/v2/astrology/kundli/advanced",
                params={
                    "ayanamsa": 1,
                    "coordinates": coordinates,
                    "datetime": datetime_str
                },
                headers={"Authorization": f"Bearer {token}"}
            )
            data = response.json()
        
        if data.get("status") != "ok" or "data" not in data:
            print(f"❌ API Error: {data}")
            return _default_chart()
        
        d = data["data"]
        nd = d.get("nakshatra_details", {})
        
        # Build chart object
        chart = {
            # Core Info
            "moon_sign": nd.get("chandra_rasi", {}).get("name", "Mesha"),
            "moon_sign_lord": nd.get("chandra_rasi", {}).get("lord", {}).get("vedic_name", "Unknown"),
            "sun_sign": nd.get("soorya_rasi", {}).get("name", "Mesha"),
            "nakshatra": nd.get("nakshatra", {}).get("name", "Ashwini"),
            "nakshatra_pada": nd.get("nakshatra", {}).get("pada", 1),
            "nakshatra_lord": nd.get("nakshatra", {}).get("lord", {}).get("vedic_name", "Ketu"),
            "western_zodiac": nd.get("zodiac", {}).get("name", "Unknown"),
            "ascendant": nd.get("chandra_rasi", {}).get("name", "Mesha"),
            
            # Additional Info
            "deity": nd.get("additional_info", {}).get("deity", "Unknown"),
            "gana": nd.get("additional_info", {}).get("ganam", "Unknown"),
            "animal_sign": nd.get("additional_info", {}).get("animal_sign", "Unknown"),
            "nadi": nd.get("additional_info", {}).get("nadi", "Unknown"),
            "lucky_color": nd.get("additional_info", {}).get("color", "Unknown"),
            "lucky_direction": nd.get("additional_info", {}).get("best_direction", "Unknown"),
            "birth_stone": nd.get("additional_info", {}).get("birth_stone", "Unknown"),
            "syllables": nd.get("additional_info", {}).get("syllables", "Unknown"),
            
            # Mangal Dosha
            "mangal_dosha": d.get("mangal_dosha", {}).get("has_dosha", False),
            "mangal_dosha_desc": d.get("mangal_dosha", {}).get("description", ""),
            
            # Yogas
            "yogas": d.get("yoga_details", []),
        }
        
        # Parse Dasha Balance
        dasha_balance = d.get("dasha_balance", {})
        chart["dasha_balance_lord"] = dasha_balance.get("lord", {}).get("name", "Unknown")
        chart["dasha_balance_remaining"] = dasha_balance.get("description", "Unknown")
        
        # Parse Dasha Periods - Find current
        dasha_periods = d.get("dasha_periods", [])
        now = datetime.now(IST)
        
        chart["current_dasha"] = "Unknown"
        chart["current_antardasha"] = "Unknown"
        chart["dasha_end_date"] = "Unknown"
        chart["antardasha_end_date"] = "Unknown"
        
        for dasha in dasha_periods:
            try:
                start = datetime.fromisoformat(dasha.get("start", "2000-01-01T00:00:00+05:30"))
                end = datetime.fromisoformat(dasha.get("end", "2100-01-01T00:00:00+05:30"))
                
                if start <= now <= end:
                    chart["current_dasha"] = dasha.get("name", "Unknown")
                    chart["dasha_end_date"] = end.strftime("%B %Y")
                    
                    # Find current Antardasha
                    for antar in dasha.get("antardasha", []):
                        a_start = datetime.fromisoformat(antar.get("start", "2000-01-01T00:00:00+05:30"))
                        a_end = datetime.fromisoformat(antar.get("end", "2100-01-01T00:00:00+05:30"))
                        
                        if a_start <= now <= a_end:
                            chart["current_antardasha"] = antar.get("name", "Unknown")
                            chart["antardasha_end_date"] = a_end.strftime("%B %Y")
                            break
                    break
            except Exception as e:
                print(f"   ⚠️ Dasha parse error: {e}")
        
        print(f"   ✅ Moon: {chart['moon_sign']} | Nakshatra: {chart['nakshatra']}")
        print(f"   ✅ Dasha: {chart['current_dasha']}/{chart['current_antardasha']}")
        
        return chart
    
    except Exception as e:
        print(f"❌ Birth chart error: {e}")
        return _default_chart()


async def get_today_panchang(lat: float = 28.6139, lng: float = 77.2090) -> Dict[str, Any]:
    """
    Get today's Panchang with ONE API call.
    Uses /v2/astrology/panchang (10 credits)
    Cached for the entire day.
    """
    
    now = datetime.now(IST)
    cache_key = now.strftime("%Y-%m-%d")
    
    # Return cached if same day
    if _panchang_cache["date"] == cache_key and _panchang_cache["data"]:
        return _panchang_cache["data"]
    
    try:
        token = await get_token()
        datetime_str = now.strftime("%Y-%m-%dT%H:%M:%S+05:30")
        
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                "https://api.prokerala.com/v2/astrology/panchang",
                params={
                    "ayanamsa": 1,
                    "coordinates": f"{lat},{lng}",
                    "datetime": datetime_str
                },
                headers={"Authorization": f"Bearer {token}"}
            )
            data = response.json()
        
        if data.get("status") != "ok" or "data" not in data:
            return _default_panchang()
        
        p = data["data"]
        
        # Extract first item from lists
        tithi = p.get("tithi", [{}])
        nakshatra = p.get("nakshatra", [{}])
        yoga = p.get("yoga", [{}])
        karana = p.get("karana", [{}])
        
        # Build result
        result = {
            "tithi": tithi[0].get("name", "Unknown") if tithi else "Unknown",
            "tithi_paksha": tithi[0].get("paksha", "") if tithi else "",
            "nakshatra": nakshatra[0].get("name", "Unknown") if nakshatra else "Unknown",
            "nakshatra_lord": nakshatra[0].get("lord", {}).get("vedic_name", "Unknown") if nakshatra else "Unknown",
            "yoga": yoga[0].get("name", "Unknown") if yoga else "Unknown",
            "karana": karana[0].get("name", "Unknown") if karana else "Unknown",
            "day": now.strftime("%A"),
            "date": now.strftime("%d %B %Y"),
            "sunrise": p.get("sunrise", ""),
            "sunset": p.get("sunset", ""),
            "moonrise": p.get("moonrise", ""),
        }
        
        # Cache the result
        _panchang_cache["date"] = cache_key
        _panchang_cache["data"] = result
        
        return result
        
    except Exception as e:
        print(f"❌ Panchang error: {e}")
        return _default_panchang()