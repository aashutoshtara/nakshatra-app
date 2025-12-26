import httpx
from config import SUPABASE_URL, SUPABASE_KEY
from typing import Optional, Dict, Any

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
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/users?phone=eq.{phone}",
            headers=get_headers()
        )
        
        if response.status_code == 200:
            data = response.json()
            return data[0] if data else None
        return None


async def create_user(phone: str) -> Dict[str, Any]:
    """Create new user"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/users",
            headers=get_headers(),
            json={"phone": phone, "state": "NEW"} 
        )

        if response.status_code in [200, 201]:
            data = response.json()
            return data[0] if data else {"phone": phone, "state": "AWAITING_NAME"}
        return {"phone": phone, "state": "AWAITING_NAME"}


async def update_user(phone: str, updates: Dict[str, Any]) -> None:
    """Update user data"""
    async with httpx.AsyncClient() as client:
        await client.patch(
            f"{BASE_URL}/users?phone=eq.{phone}",
            headers=get_headers(),
            json=updates
        )


async def get_or_create_user(phone: str) -> Dict[str, Any]:
    """Get existing user or create new one"""
    user = await get_user(phone)
    if not user:
        user = await create_user(phone)
    return user


async def get_all_ready_users() -> list:
    """Get all users who completed onboarding"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/users?state=eq.READY",
            headers=get_headers()
        )
        
        if response.status_code == 200:
            return response.json()
        return []


async def get_cached_city(city_name: str) -> Optional[Dict[str, float]]:
    """Get city from cache"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/cities?name=eq.{city_name.lower().strip()}",
            headers=get_headers()
        )
        
        if response.status_code == 200:
            data = response.json()
            if data:
                return {"lat": float(data[0]["lat"]), "lng": float(data[0]["lng"])}
        return None


async def cache_city(city_name: str, lat: float, lng: float) -> None:
    """Save city to cache"""
    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{BASE_URL}/cities",
                headers=get_headers(),
                json={"name": city_name.lower().strip(), "lat": lat, "lng": lng}
            )
    except Exception:
        pass