import httpx
from typing import Dict, Any

GEOAPIFY_API_KEY = "8f4fd888c11e47209c28305f7e6cb425"

# Simple in-memory cache to prevent redundant API calls for nearby segments
_geoapify_cache = {}

async def _count_geoapify_places(lat: float, lng: float, categories: str, radius=150) -> int:
    """
    Helper function to query Geoapify Places API for specific categories around a coordinate.
    Caches the result using rounded coordinates (approx 111m resolution at 3 decimal places)
    to drastically reduce API rate limits and timeouts during route scoring.
    """
    cache_key = f"{round(lat, 3)}_{round(lng, 3)}_{categories}"
    if cache_key in _geoapify_cache:
        return _geoapify_cache[cache_key]

    url = f"https://api.geoapify.com/v2/places?categories={categories}&filter=circle:{lng},{lat},{radius}&limit=20&apiKey={GEOAPIFY_API_KEY}"
    try:
        # Reduced timeout to prevent route hanging
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=2.0)
            if response.status_code == 200:
                data = response.json()
                count = len(data.get("features", []))
                _geoapify_cache[cache_key] = count
                return count
            else:
                print(f"Geoapify Status {response.status_code}: {response.text}")
    except Exception as e:
        print(f"Geoapify Exception: {e}")
        
    # Cache failures too so we don't spam the API when it's down or rate limited
    _geoapify_cache[cache_key] = 0
    return 0

async def get_lta_traffic_data(lat: float, lng: float) -> float:
    """
    Uses Geoapify Places API to count noisy infrastructure (public transport, parking)
    as a proxy for street-level noise pollution.
    Returns a normalized noise score between 0.0 (quiet) and 1.0 (very loud).
    """
    # Categories that imply noise: roads, parking, generic transport
    count = await _count_geoapify_places(lat, lng, "commercial,building.transportation")
    # Normalize: 0 places = low noise (0.1), >5 places = high noise (1.0)
    score = min(1.0, count / 5.0)
    return max(0.1, score)

async def get_onemap_crowd_data(lat: float, lng: float) -> float:
    """
    Uses Geoapify Places API to count crowd-drawing locations (retail, catering, leisure).
    Returns a normalized crowd score between 0.0 (empty) and 1.0 (packed).
    """
    # Categories that imply crowds: shopping malls, retail, catering, leisure
    count = await _count_geoapify_places(lat, lng, "commercial,catering,leisure")
    # Normalize: 0 places = low crowd (0.1), >10 places = high crowd (1.0)
    score = min(1.0, count / 10.0)
    return max(0.1, score)

async def get_green_space_data(lat: float, lng: float) -> float:
    """
    Uses Geoapify Places API to determine proximity to parks, nature reserves, or water bodies.
    Returns a normalized greenery score between 0.0 (concrete jungle) and 1.0 (lush park).
    """
    # Categories that imply nature: parks, forests, nature reserves, water bodies
    count = await _count_geoapify_places(lat, lng, "natural,leisure.park")
    # Normalize: 0 places = no nature (0.0), >3 places = lots of nature (1.0)
    return min(1.0, count / 3.0)
