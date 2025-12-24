import httpx
from config import GOOGLE_MAPS_API_KEY
from services.database import get_cached_city, cache_city
from typing import Dict, List, Optional

# In-memory cache
_city_cache: Dict[str, Dict[str, float]] = {}


async def search_cities(query: str) -> List[Dict]:
    """Search for cities and return options"""
    
    try:
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "address": f"{query}, India",
            "key": GOOGLE_MAPS_API_KEY,
            "region": "in"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            data = response.json()
        
        if data.get("status") != "OK":
            return []
        
        results = []
        for result in data.get("results", [])[:5]:
            formatted = result.get("formatted_address", "")
            location = result["geometry"]["location"]
            
            results.append({
                "name": formatted,
                "lat": location["lat"],
                "lng": location["lng"]
            })
        
        return results
    
    except Exception as e:
        print(f"Geocoding search error: {e}")
        return []


async def get_coordinates(city: str) -> Dict[str, float]:
    """Get lat/lng for a city (legacy function)"""
    
    city_key = city.lower().strip()
    
    # Check memory cache
    if city_key in _city_cache:
        return _city_cache[city_key]
    
    # Check database cache
    cached = await get_cached_city(city_key)
    if cached:
        _city_cache[city_key] = cached
        return cached
    
    # Call Google API
    try:
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "address": f"{city}, India",
            "key": GOOGLE_MAPS_API_KEY
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            data = response.json()
        
        if data.get("results"):
            location = data["results"][0]["geometry"]["location"]
            coords = {"lat": location["lat"], "lng": location["lng"]}
            
            _city_cache[city_key] = coords
            await cache_city(city_key, coords["lat"], coords["lng"])
            
            return coords
    
    except Exception as e:
        print(f"Geocoding error: {e}")
    
    # Default to Delhi
    return {"lat": 28.6139, "lng": 77.2090}