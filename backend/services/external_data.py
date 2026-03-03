import httpx
import os
import random
from typing import Dict, Any

# TODO: Replace with actual API keys for Hackathon
LTA_API_KEY = os.environ.get("LTA_API_KEY", "MOCK")
ONEMAP_API_KEY = os.environ.get("ONEMAP_API_KEY", "MOCK")

async def get_lta_traffic_data(lat: float, lng: float) -> float:
    """
    Fetches real-time traffic volume data serving as a proxy for street-level noise pollution.
    Returns a normalized noise score between 0.0 (quiet) and 1.0 (very loud).
    """
    if LTA_API_KEY == "MOCK":
        # Hackathon Mock: generate a random noise score
        return random.uniform(0.1, 0.9)
        
    # TODO: Implement actual LTA DataMall Traffic API call
    # url = "http://datamall2.mytransport.sg/ltaodataservice/TrafficIncidents"
    # headers = {"AccountKey": LTA_API_KEY}
    # async with httpx.AsyncClient() as client:
    #     response = await client.get(url, headers=headers)
    #     data = response.json()
    #     return calculate_noise_from_traffic(data, lat, lng)
    return 0.5

async def get_onemap_crowd_data(lat: float, lng: float) -> float:
    """
    Pulls real-time crowd density data at transit hubs and shopping districts.
    Returns a normalized crowd score between 0.0 (empty) and 1.0 (packed).
    """
    if ONEMAP_API_KEY == "MOCK":
         # Hackathon Mock: generate a random crowd score
        return random.uniform(0.1, 0.9)
        
    # TODO: Implement actual OneMap API call
    # url = f"https://www.onemap.gov.sg/api/public/themesvc/getThemeInfo?queryName=...&x={lng}&y={lat}"
    # async with httpx.AsyncClient() as client:
    #     response = await client.get(url)
    #     data = response.json()
    #     return calculate_crowd_density(data)
    return 0.5

async def get_green_space_data(lat: float, lng: float) -> float:
    """
    Pulls data to determine proximity to parks, nature reserves, or water bodies.
    Returns a normalized greenery score between 0.0 (concrete jungle) and 1.0 (lush park).
    """
    if LTA_API_KEY == "MOCK":
        # Hackathon Mock: generate a random greenery score
        return random.uniform(0.1, 0.9)
    return 0.5
