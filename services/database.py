"""
Nakshatra Database Service
Supabase REST API for users, charts, and cities
"""
import httpx
from datetime import date, time, datetime
from typing import Optional, Dict, Any, List
from config import SUPABASE_URL, SUPABASE_KEY

# =============================================================================
# CONFIGURATION
# =============================================================================

BASE_URL = f"{SUPABASE_URL}/rest/v1"
TIMEOUT = 30


def get_headers():
    """Get Supabase REST API headers"""
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }


# =============================================================================
# CITIES TABLE (Geocoding Cache)
# =============================================================================

async def get_cached_city(city_name: str) -> Optional[Dict[str, Any]]:
    """Get city coordinates from cache"""
    try:
        normalized = city_name.lower().strip()
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(
                f"{BASE_URL}/cities",
                headers=get_headers(),
                params={"name": f"eq.{normalized}"}
            )
            if response.status_code == 200:
                data = response.json()
                if data:
                    return {
                        "lat": float(data[0]["lat"]),
                        "lng": float(data[0]["lng"]),
                        "formatted_address": data[0].get("formatted_address")
                    }
            return None
    except Exception as e:
        print(f"❌ DB Error (get_cached_city): {e}")
        return None


async def cache_city(
    city_name: str,
    lat: float,
    lng: float,
    formatted_address: str = None
) -> bool:
    """Save city coordinates to cache"""
    try:
        normalized = city_name.lower().strip()
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.post(
                f"{BASE_URL}/cities",
                headers=get_headers(),
                json={
                    "name": normalized,
                    "lat": lat,
                    "lng": lng,
                    "formatted_address": formatted_address
                }
            )
            return response.status_code in [200, 201]
    except Exception as e:
        print(f"❌ DB Error (cache_city): {e}")
        return False


# =============================================================================
# USERS TABLE
# =============================================================================

async def get_user_by_phone(phone: str) -> Optional[Dict[str, Any]]:
    """Get user by phone number"""
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(
                f"{BASE_URL}/users",
                headers=get_headers(),
                params={"phone": f"eq.{phone}"}
            )
            if response.status_code == 200:
                data = response.json()
                return data[0] if data else None
            return None
    except Exception as e:
        print(f"❌ DB Error (get_user_by_phone): {e}")
        return None


async def get_user_by_telegram_id(telegram_id: int) -> Optional[Dict[str, Any]]:
    """Get user by Telegram ID"""
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(
                f"{BASE_URL}/users",
                headers=get_headers(),
                params={"telegram_id": f"eq.{telegram_id}"}
            )
            if response.status_code == 200:
                data = response.json()
                return data[0] if data else None
            return None
    except Exception as e:
        print(f"❌ DB Error (get_user_by_telegram_id): {e}")
        return None


async def create_user(
    phone: str = None,
    telegram_id: int = None,
    telegram_username: str = None,
    name: str = None
) -> Optional[Dict[str, Any]]:
    """Create a new user"""
    try:
        user_data = {"state": "NEW"}
        
        if phone:
            user_data["phone"] = phone
        if telegram_id:
            user_data["telegram_id"] = telegram_id
        if telegram_username:
            user_data["telegram_username"] = telegram_username
        if name:
            user_data["name"] = name

        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.post(
                f"{BASE_URL}/users",
                headers=get_headers(),
                json=user_data
            )
            if response.status_code in [200, 201]:
                data = response.json()
                return data[0] if data else user_data
            else:
                print(f"❌ Create user failed: {response.status_code} - {response.text}")
                return None
    except Exception as e:
        print(f"❌ DB Error (create_user): {e}")
        return None


async def get_or_create_user_by_telegram(
    telegram_id: int,
    telegram_username: str = None,
    name: str = None
) -> Dict[str, Any]:
    """Get existing user by Telegram ID or create new one"""
    user = await get_user_by_telegram_id(telegram_id)
    if not user:
        user = await create_user(
            telegram_id=telegram_id,
            telegram_username=telegram_username,
            name=name
        )
    return user or {"telegram_id": telegram_id, "state": "NEW"}


async def get_or_create_user_by_phone(phone: str) -> Dict[str, Any]:
    """Get existing user by phone or create new one"""
    user = await get_user_by_phone(phone)
    if not user:
        user = await create_user(phone=phone)
    return user or {"phone": phone, "state": "NEW"}


async def update_user_by_telegram_id(
    telegram_id: int,
    updates: Dict[str, Any]
) -> bool:
    """Update user data by Telegram ID"""
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.patch(
                f"{BASE_URL}/users",
                headers=get_headers(),
                params={"telegram_id": f"eq.{telegram_id}"},
                json=updates
            )
            if response.status_code in [200, 204]:
                print(f"✅ Updated user {telegram_id}")
                return True
            else:
                print(f"❌ Update failed: {response.status_code} - {response.text}")
                return False
    except Exception as e:
        print(f"❌ DB Error (update_user): {e}")
        return False


async def update_user_by_phone(phone: str, updates: Dict[str, Any]) -> bool:
    """Update user data by phone"""
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.patch(
                f"{BASE_URL}/users",
                headers=get_headers(),
                params={"phone": f"eq.{phone}"},
                json=updates
            )
            if response.status_code in [200, 204]:
                print(f"✅ Updated user {phone}")
                return True
            else:
                print(f"❌ Update failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ DB Error (update_user_by_phone): {e}")
        return False


async def save_user_birth_details(
    telegram_id: int = None,
    phone: str = None,
    name: str = None,
    gender: str = None,           # "male" or "female"
    birth_date: str = None,       # "YYYY-MM-DD"
    birth_time: str = None,       # "HH:MM:SS" or "HH:MM"
    birth_place: str = None,
    birth_lat: float = None,
    birth_lng: float = None,
    birth_timezone: str = None,
    # Basic chart data
    moon_sign: str = None,
    sun_sign: str = None,
    ascendant: str = None,
    nakshatra: str = None,
    nakshatra_pada: int = None,
    current_dasha: str = None
) -> bool:
    """Save user's birth details and basic chart after onboarding"""
    updates = {"state": "READY", "last_active_at": datetime.utcnow().isoformat()}
    
    if name:
        updates["name"] = name
    if gender:
        updates["gender"] = gender
    if birth_date:
        updates["birth_date"] = birth_date
    if birth_time:
        # Ensure HH:MM:SS format
        if len(birth_time) == 5:
            birth_time += ":00"
        updates["birth_time"] = birth_time
    if birth_place:
        updates["birth_place"] = birth_place
    if birth_lat is not None:
        updates["birth_lat"] = birth_lat
    if birth_lng is not None:
        updates["birth_lng"] = birth_lng
    if birth_timezone:
        updates["birth_timezone"] = birth_timezone
    if moon_sign:
        updates["moon_sign"] = moon_sign
    if sun_sign:
        updates["sun_sign"] = sun_sign
    if ascendant:
        updates["ascendant"] = ascendant
    if nakshatra:
        updates["nakshatra"] = nakshatra
    if nakshatra_pada:
        updates["nakshatra_pada"] = nakshatra_pada
    if current_dasha:
        updates["current_dasha"] = current_dasha

    if telegram_id:
        return await update_user_by_telegram_id(telegram_id, updates)
    elif phone:
        return await update_user_by_phone(phone, updates)
    else:
        print("❌ No identifier provided for save_user_birth_details")
        return False


async def get_all_ready_users() -> List[Dict[str, Any]]:
    """Get all users who completed onboarding (for notifications)"""
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(
                f"{BASE_URL}/users",
                headers=get_headers(),
                params={"state": "eq.READY"}
            )
            if response.status_code == 200:
                return response.json()
            return []
    except Exception as e:
        print(f"❌ DB Error (get_all_ready_users): {e}")
        return []


# =============================================================================
# CHARTS TABLE (Full Calculations)
# =============================================================================

async def save_chart(
    user_id: str,
    birth_date: str,              # "YYYY-MM-DD"
    birth_time: str,              # "HH:MM:SS"
    birth_lat: float,
    birth_lng: float,
    birth_timezone: str,
    birth_place: str = None,
    chart_type: str = "birth",
    chart_name: str = None,
    # Chart data
    ascendant: Dict = None,
    planets: Dict = None,
    dasha_periods: List = None,
    current_mahadasha: str = None,
    current_antardasha: str = None,
    # Panchanga
    birth_tithi: str = None,
    birth_nakshatra: str = None,
    birth_yoga: str = None,
    birth_karana: str = None,
    # Advanced
    navamsa: Dict = None,
    houses: Dict = None
) -> Optional[Dict[str, Any]]:
    """Save a full chart calculation"""
    try:
        chart_data = {
            "user_id": user_id,
            "chart_type": chart_type,
            "birth_date": birth_date,
            "birth_time": birth_time,
            "birth_lat": birth_lat,
            "birth_lng": birth_lng,
            "birth_timezone": birth_timezone
        }
        
        if birth_place:
            chart_data["birth_place"] = birth_place
        if chart_name:
            chart_data["chart_name"] = chart_name
        if ascendant:
            chart_data["ascendant"] = ascendant
        if planets:
            chart_data["planets"] = planets
        if dasha_periods:
            chart_data["dasha_periods"] = dasha_periods
        if current_mahadasha:
            chart_data["current_mahadasha"] = current_mahadasha
        if current_antardasha:
            chart_data["current_antardasha"] = current_antardasha
        if birth_tithi:
            chart_data["birth_tithi"] = birth_tithi
        if birth_nakshatra:
            chart_data["birth_nakshatra"] = birth_nakshatra
        if birth_yoga:
            chart_data["birth_yoga"] = birth_yoga
        if birth_karana:
            chart_data["birth_karana"] = birth_karana
        if navamsa:
            chart_data["navamsa"] = navamsa
        if houses:
            chart_data["houses"] = houses

        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.post(
                f"{BASE_URL}/charts",
                headers=get_headers(),
                json=chart_data
            )
            if response.status_code in [200, 201]:
                data = response.json()
                print(f"✅ Chart saved for user {user_id}")
                return data[0] if data else chart_data
            else:
                print(f"❌ Save chart failed: {response.status_code} - {response.text}")
                return None
    except Exception as e:
        print(f"❌ DB Error (save_chart): {e}")
        return None


async def get_user_charts(user_id: str) -> List[Dict[str, Any]]:
    """Get all charts for a user"""
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(
                f"{BASE_URL}/charts",
                headers=get_headers(),
                params={
                    "user_id": f"eq.{user_id}",
                    "order": "created_at.desc"
                }
            )
            if response.status_code == 200:
                return response.json()
            return []
    except Exception as e:
        print(f"❌ DB Error (get_user_charts): {e}")
        return []


async def get_latest_chart(user_id: str) -> Optional[Dict[str, Any]]:
    """Get the most recent chart for a user"""
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(
                f"{BASE_URL}/charts",
                headers=get_headers(),
                params={
                    "user_id": f"eq.{user_id}",
                    "order": "created_at.desc",
                    "limit": "1"
                }
            )
            if response.status_code == 200:
                data = response.json()
                return data[0] if data else None
            return None
    except Exception as e:
        print(f"❌ DB Error (get_latest_chart): {e}")
        return None


async def delete_chart(chart_id: str) -> bool:
    """Delete a chart"""
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.delete(
                f"{BASE_URL}/charts",
                headers=get_headers(),
                params={"id": f"eq.{chart_id}"}
            )
            return response.status_code in [200, 204]
    except Exception as e:
        print(f"❌ DB Error (delete_chart): {e}")
        return False


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

async def update_last_active(telegram_id: int = None, phone: str = None) -> bool:
    """Update user's last active timestamp"""
    updates = {"last_active_at": datetime.utcnow().isoformat()}
    
    if telegram_id:
        return await update_user_by_telegram_id(telegram_id, updates)
    elif phone:
        return await update_user_by_phone(phone, updates)
    return False