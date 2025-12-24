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
    lat: Optional[float] = None,
    lng: Optional[float] = None
) -> Dict[str, str]:
    """Calculate birth chart"""
    
    try:
        # Use provided coordinates or default
        if lat is None or lng is None:
            lat, lng = 28.6139, 77.2090  # Delhi default
        
        token = await get_token()
        datetime_str = f"{dob}T{birth_time}+05:30"
        
        async with httpx.AsyncClient() as client:
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
        
        if "data" in data:
            chart = data["data"]
            
            nakshatra = chart.get("nakshatra", {})
            rasi = chart.get("rasi", {})
            ascendant = chart.get("ascendant", {})
            
            return {
                "moon_sign": rasi.get("name", "Mesha") if isinstance(rasi, dict) else "Mesha",
                "nakshatra": nakshatra.get("name", "Ashwini") if isinstance(nakshatra, dict) else "Ashwini",
                "ascendant": ascendant.get("name", "Mesha") if isinstance(ascendant, dict) else "Mesha"
            }
    
    except Exception as e:
        print(f"Birth chart error: {e}")
    
    return {"moon_sign": "Mesha", "nakshatra": "Ashwini", "ascendant": "Mesha"}


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
        
        if "data" in data:
            p = data["data"]
            return {
                "tithi": safe_get_first(p.get("tithi", [])),
                "nakshatra": safe_get_first(p.get("nakshatra", [])),
                "yoga": safe_get_first(p.get("yoga", [])),
                "day": datetime.now().strftime("%A")
            }
    
    except Exception as e:
        print(f"Panchang error: {e}")
    
    return {
        "tithi": "Shukla Panchami",
        "nakshatra": "Rohini",
        "yoga": "Shubha",
        "day": datetime.now().strftime("%A")
    }