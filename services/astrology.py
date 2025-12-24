import httpx
from datetime import datetime
from config import PROKERALA_CLIENT_ID, PROKERALA_CLIENT_SECRET
from typing import Dict, Any, Optional

# Token cache
_token_cache = {"token": None, "expires_at": None}


async def get_token() -> str:
    """Get Prokerala access token"""
    
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
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        result = response.json()
    
    _token_cache["token"] = result["access_token"]
    _token_cache["expires_at"] = datetime.now().timestamp() + 3000
    
    return result["access_token"]


def safe_get_first(data_list, key="name", default="Unknown"):
    """Safely get first item from list"""
    if data_list and isinstance(data_list, list) and len(data_list) > 0:
        return data_list[0].get(key, default)
    return default


async def calculate_birth_chart(
    dob: str, 
    birth_time: str, 
    city: str,
    lat: float = None,
    lng: float = None
) -> Dict[str, str]:
    """Calculate birth chart"""
    
    try:
        if lat is None or lng is None:
            lat, lng = 28.6139, 77.2090
        
        token = await get_token()
        datetime_str = f"{dob}T{birth_time}+05:30"
        
        print(f"🔮 Calculating chart: {datetime_str} at {lat},{lng}")
        
        async with httpx.AsyncClient() as client:
            # Get Kundli
            response = await client.get(
                "https://api.prokerala.com/v2/astrology/kundli",
                params={
                    "ayanamsa": 1,
                    "coordinates": f"{lat},{lng}",
                    "datetime": datetime_str
                },
                headers={"Authorization": f"Bearer {token}"}
            )
            data = response.json()
        
        # Default values
        moon_sign = "Mesha"
        nakshatra = "Ashwini"
        ascendant = "Mesha"
        nakshatra_pada = 1
        nakshatra_lord = "Ketu"
        
        if data.get("status") == "ok" and "data" in data:
            chart_data = data["data"]
            nakshatra_details = chart_data.get("nakshatra_details", {})
            
            # Moon Sign (Chandra Rasi)
            chandra_rasi = nakshatra_details.get("chandra_rasi", {})
            if chandra_rasi:
                moon_sign = chandra_rasi.get("name", "Mesha")
            
            # Nakshatra
            nakshatra_info = nakshatra_details.get("nakshatra", {})
            if nakshatra_info:
                nakshatra = nakshatra_info.get("name", "Ashwini")
                nakshatra_pada = nakshatra_info.get("pada", 1)
                nakshatra_lord_info = nakshatra_info.get("lord", {})
                if nakshatra_lord_info:
                    nakshatra_lord = nakshatra_lord_info.get("vedic_name", "Ketu")
            
            print(f"   🌙 Moon Sign: {moon_sign}")
            print(f"   ⭐ Nakshatra: {nakshatra} (Pada {nakshatra_pada})")
            print(f"   🪐 Nakshatra Lord: {nakshatra_lord}")
        
        # Now get Ascendant from chart endpoint
        async with httpx.AsyncClient() as client:
            chart_response = await client.get(
                "https://api.prokerala.com/v2/astrology/chart",
                params={
                    "ayanamsa": 1,
                    "coordinates": f"{lat},{lng}",
                    "datetime": datetime_str,
                    "chart_type": "rasi"
                },
                headers={"Authorization": f"Bearer {token}"}
            )
            chart_result = chart_response.json()
        
        if chart_result.get("status") == "ok" and "data" in chart_result:
            chart_info = chart_result["data"]
            
            # Try to find ascendant
            ascendant_info = chart_info.get("ascendant", {})
            if ascendant_info and isinstance(ascendant_info, dict):
                ascendant = ascendant_info.get("name", moon_sign)
            elif "lagna" in chart_info:
                lagna_info = chart_info.get("lagna", {})
                if isinstance(lagna_info, dict):
                    ascendant = lagna_info.get("name", moon_sign)
            
            print(f"   🌅 Ascendant: {ascendant}")
        else:
            # If chart endpoint fails, use moon sign as fallback
            ascendant = moon_sign
            print(f"   🌅 Ascendant (fallback): {ascendant}")
        
        return {
            "moon_sign": moon_sign,
            "nakshatra": nakshatra,
            "ascendant": ascendant,
            "nakshatra_pada": nakshatra_pada,
            "nakshatra_lord": nakshatra_lord
        }
    
    except Exception as e:
        print(f"❌ Birth chart error: {e}")
        return {
            "moon_sign": "Mesha", 
            "nakshatra": "Ashwini", 
            "ascendant": "Mesha",
            "nakshatra_pada": 1,
            "nakshatra_lord": "Ketu"
        }


async def get_today_panchang() -> Dict[str, Any]:
    """Get today's Panchang"""
    
    try:
        token = await get_token()
        today = datetime.now().strftime("%Y-%m-%dT12:00:00+05:30")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.prokerala.com/v2/astrology/panchang",
                params={
                    "ayanamsa": 1,
                    "coordinates": "28.6139,77.2090",
                    "datetime": today
                },
                headers={"Authorization": f"Bearer {token}"}
            )
            data = response.json()
        
        if data.get("status") == "ok" and "data" in data:
            p = data["data"]
            return {
                "tithi": safe_get_first(p.get("tithi", [])),
                "nakshatra": safe_get_first(p.get("nakshatra", [])),
                "yoga": safe_get_first(p.get("yoga", [])),
                "day": datetime.now().strftime("%A")
            }
    
    except Exception as e:
        print(f"❌ Panchang error: {e}")
    
    return {
        "tithi": "Shukla Panchami",
        "nakshatra": "Rohini",
        "yoga": "Shubha",
        "day": datetime.now().strftime("%A")
    }