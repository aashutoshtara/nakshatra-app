import httpx
from config import SUPABASE_URL, SUPABASE_KEY
from typing import Optional, Dict, Any, List

# Supabase REST API headers
def get_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

BASE_URL = f"{SUPABASE_URL}/rest/v1"


async def get_user(phone: str) -> Optional[Dict[str, Any]]:
    """Get user by phone number"""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{BASE_URL}/users?phone=eq.{phone}",
                headers=get_headers()
            )
            if response.status_code == 200:
                data = response.json()
                return data[0] if data else None
            return None
    except Exception as e:
        print(f"❌ DB Error (get_user): {e}")
        return None


async def create_user(phone: str) -> Dict[str, Any]:
    """Create new user"""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{BASE_URL}/users",
                headers=get_headers(),
                json={"phone": phone, "state": "NEW"}
            )
            if response.status_code in [200, 201]:
                data = response.json()
                return data[0] if data else {"phone": phone, "state": "NEW"}
            return {"phone": phone, "state": "NEW"}
    except Exception as e:
        print(f"❌ DB Error (create_user): {e}")
        return {"phone": phone, "state": "NEW"}


async def update_user(phone: str, updates: Dict[str, Any]) -> bool:
    """Update user data"""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.patch(
                f"{BASE_URL}/users?phone=eq.{phone}",
                headers=get_headers(),
                json=updates
            )
            
            if response.status_code in [200, 204]:
                print(f"✅ Updated {phone}: state={updates.get('state', 'N/A')}")
                return True
            else:
                print(f"❌ Update failed: {response.status_code} - {response.text}")
                return False
    except Exception as e:
        print(f"❌ DB Error (update_user): {e}")
        return False


async def get_or_create_user(phone: str) -> Dict[str, Any]:
    """Get existing user or create new one"""
    user = await get_user(phone)
    if not user:
        user = await create_user(phone)
    return user


async def get_all_ready_users() -> List[Dict[str, Any]]:
    """Get all users who completed onboarding"""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{BASE_URL}/users?state=eq.READY",
                headers=get_headers()
            )
            if response.status_code == 200:
                return response.json()
            return []
    except Exception as e:
        print(f"❌ DB Error (get_all_ready): {e}")
        return []


async def get_cached_city(city_name: str) -> Optional[Dict[str, float]]:
    """Get city from cache"""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{BASE_URL}/cities?name=eq.{city_name.lower().strip()}",
                headers=get_headers()
            )
            if response.status_code == 200:
                data = response.json()
                if data:
                    return {"lat": float(data[0]["lat"]), "lng": float(data[0]["lng"])}
            return None
    except Exception as e:
        print(f"❌ DB Error (get_cached_city): {e}")
        return None


async def cache_city(city_name: str, lat: float, lng: float) -> None:
    """Save city to cache"""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            await client.post(
                f"{BASE_URL}/cities",
                headers=get_headers(),
                json={"name": city_name.lower().strip(), "lat": lat, "lng": lng}
            )
    except Exception:
        pass