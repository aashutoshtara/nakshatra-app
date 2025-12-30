"""
Geocoding Service
Converts city names to coordinates using Google Maps API with caching
"""

import httpx
from typing import Dict, List, Optional
from config import GOOGLE_MAPS_API_KEY
from services.database import get_cached_city, cache_city

# In-memory cache
_city_cache: Dict[str, Dict[str, float]] = {}


async def search_cities(query: str) -> List[Dict]:
    """
    Search for cities and return multiple options
    
    Returns:
        List of dicts with name, lat, lng
    """
    if not GOOGLE_MAPS_API_KEY:
        # Fallback - just return single result using get_coordinates
        coords = await get_coordinates(query)
        if coords:
            return [{"name": query, "lat": coords["lat"], "lng": coords["lng"]}]
        return []
    
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


async def get_coordinates(city: str) -> Optional[Dict[str, float]]:
    """
    Get lat/lng for a city with caching
    
    Returns:
        Dict with lat, lng or None
    """
    city_key = city.lower().strip()
    
    # Check memory cache
    if city_key in _city_cache:
        return _city_cache[city_key]
    
    # Check database cache
    try:
        cached = await get_cached_city(city_key)
        if cached:
            _city_cache[city_key] = cached
            return cached
    except Exception as e:
        print(f"Cache lookup error: {e}")
    
    # Call Google API
    if GOOGLE_MAPS_API_KEY:
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
                
                # Cache it
                _city_cache[city_key] = coords
                try:
                    await cache_city(city_key, coords["lat"], coords["lng"])
                except:
                    pass  # Cache failure is non-critical
                
                return coords
        
        except Exception as e:
            print(f"Google geocoding error: {e}")
    
    # Fallback to free Nominatim
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": f"{city}, India",
            "format": "json",
            "limit": 1
        }
        headers = {"User-Agent": "NakshatraApp/1.0"}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=headers)
            data = response.json()
        
        if data:
            coords = {"lat": float(data[0]["lat"]), "lng": float(data[0]["lon"])}
            _city_cache[city_key] = coords
            try:
                await cache_city(city_key, coords["lat"], coords["lng"])
            except:
                pass
            return coords
    
    except Exception as e:
        print(f"Nominatim geocoding error: {e}")
    
    # Default to Delhi if everything fails
    return {"lat": 28.6139, "lng": 77.2090}


# =============================================================================
# COMMON INDIAN CITIES (Fallback)
# =============================================================================

INDIAN_CITIES = {
    "delhi": {"lat": 28.6139, "lng": 77.2090},
    "new delhi": {"lat": 28.6139, "lng": 77.2090},
    "mumbai": {"lat": 19.0760, "lng": 72.8777},
    "bombay": {"lat": 19.0760, "lng": 72.8777},
    "bangalore": {"lat": 12.9716, "lng": 77.5946},
    "bengaluru": {"lat": 12.9716, "lng": 77.5946},
    "chennai": {"lat": 13.0827, "lng": 80.2707},
    "madras": {"lat": 13.0827, "lng": 80.2707},
    "kolkata": {"lat": 22.5726, "lng": 88.3639},
    "calcutta": {"lat": 22.5726, "lng": 88.3639},
    "hyderabad": {"lat": 17.3850, "lng": 78.4867},
    "pune": {"lat": 18.5204, "lng": 73.8567},
    "ahmedabad": {"lat": 23.0225, "lng": 72.5714},
    "jaipur": {"lat": 26.9124, "lng": 75.7873},
    "lucknow": {"lat": 26.8467, "lng": 80.9462},
    "kanpur": {"lat": 26.4499, "lng": 80.3319},
    "nagpur": {"lat": 21.1458, "lng": 79.0882},
    "indore": {"lat": 22.7196, "lng": 75.8577},
    "bhopal": {"lat": 23.2599, "lng": 77.4126},
    "patna": {"lat": 25.5941, "lng": 85.1376},
    "vadodara": {"lat": 22.3072, "lng": 73.1812},
    "baroda": {"lat": 22.3072, "lng": 73.1812},
    "surat": {"lat": 21.1702, "lng": 72.8311},
    "coimbatore": {"lat": 11.0168, "lng": 76.9558},
    "kochi": {"lat": 9.9312, "lng": 76.2673},
    "cochin": {"lat": 9.9312, "lng": 76.2673},
    "visakhapatnam": {"lat": 17.6868, "lng": 83.2185},
    "vizag": {"lat": 17.6868, "lng": 83.2185},
    "agra": {"lat": 27.1767, "lng": 78.0081},
    "varanasi": {"lat": 25.3176, "lng": 82.9739},
    "banaras": {"lat": 25.3176, "lng": 82.9739},
    "chandigarh": {"lat": 30.7333, "lng": 76.7794},
    "gurgaon": {"lat": 28.4595, "lng": 77.0266},
    "gurugram": {"lat": 28.4595, "lng": 77.0266},
    "noida": {"lat": 28.5355, "lng": 77.3910},
    "ghaziabad": {"lat": 28.6692, "lng": 77.4538},
    "faridabad": {"lat": 28.4089, "lng": 77.3178},
    "thane": {"lat": 19.2183, "lng": 72.9781},
    "navi mumbai": {"lat": 19.0330, "lng": 73.0297},
}


def get_city_from_fallback(city: str) -> Optional[Dict[str, float]]:
    """Get coordinates from fallback list"""
    city_lower = city.lower().strip()
    return INDIAN_CITIES.get(city_lower)