import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ROUTING_PROVIDER: str = "osrm"  # valhalla|graphhopper|osrm|ors
    VALHALLA_URL: str = "http://localhost:8002"
    GRAPHHOPPER_KEY: str = ""
    OSRM_BASE_URL: str = "http://router.project-osrm.org"
    OPENROUTESERVICE_KEY: str = ""
    ONEMAP_API_KEY: str = ""
    LTA_DATAMALL_KEY: str = ""
    HERE_API_KEY: str = ""
    
    SIGNAL_CACHE_TTL: int = 120
    ROUTE_CACHE_TTL: int = 120
    MAX_LONGEST_RATIO: float = 2.0
    OVERLAP_THRESHOLD: float = 0.70
    TIME_WEIGHT: float = 0.15

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        extra = "allow" # allow extra fields without error

settings = Settings()
