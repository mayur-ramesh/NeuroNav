from abc import ABC, abstractmethod
import math
from utils.cache import signal_cache
from utils.config import settings
from models import Coordinate
from services.external_data import get_lta_traffic_data, get_onemap_crowd_data, get_green_space_data

class BaseSignalProvider(ABC):
    @abstractmethod
    async def get_noise(self, coord: Coordinate) -> float: pass
    @abstractmethod
    async def get_crowd(self, coord: Coordinate) -> float: pass
    @abstractmethod
    async def get_nature(self, coord: Coordinate) -> float: pass
    @abstractmethod
    async def get_shelter(self, coord: Coordinate) -> float: pass

class SimulatedSignalProvider(BaseSignalProvider):
    """
    Generates realistic simulated environmental signals for Singapore.
    Uses proximity to known hotspots rather than random hashing,
    so overlays look meaningful and location-aware.
    """
    
    # Known Singapore hotspots with (lat, lng, intensity)
    NOISE_HOTSPOTS = [
        (1.3048, 103.8318, 0.9),   # Orchard Road - very noisy
        (1.2834, 103.8607, 0.85),  # Marina Bay - busy
        (1.2796, 103.8546, 0.8),   # CBD / Raffles Place
        (1.3331, 103.7422, 0.7),   # Jurong East - industrial
        (1.3533, 103.9452, 0.6),   # Tampines - suburban busy  
        (1.3191, 103.8455, 0.65),  # Toa Payoh
        (1.3520, 103.8198, 0.5),   # Ang Mo Kio
        (1.3644, 103.9915, 0.4),   # Changi - moderate
    ]
    
    CROWD_HOTSPOTS = [
        (1.3048, 103.8318, 0.95),  # Orchard - peak crowd
        (1.2834, 103.8607, 0.9),   # MBS
        (1.2796, 103.8546, 0.85),  # CBD
        (1.3331, 103.7422, 0.75),  # Jurong East MRT
        (1.3533, 103.9452, 0.65),  # Tampines MRT
        (1.4368, 103.7862, 0.5),   # Woodlands
        (1.3521, 103.8198, 0.55),  # Central
    ]
    
    NATURE_HOTSPOTS = [
        (1.3138, 103.8159, 0.95),  # Botanic Gardens
        (1.3435, 103.8341, 0.9),   # MacRitchie Reservoir
        (1.3600, 103.8200, 0.85),  # Bishan-Ang Mo Kio Park
        (1.2966, 103.7764, 0.8),   # NUS / Kent Ridge Park
        (1.3816, 103.9550, 0.7),   # Pasir Ris Park
        (1.2483, 103.8296, 0.75),  # Gardens by the Bay
        (1.3772, 103.7475, 0.65),  # Bukit Timah Nature Reserve
    ]
    
    def _proximity_score(self, coord: Coordinate, hotspots: list) -> float:
        """Calculate signal strength based on proximity to known hotspots."""
        max_score = 0.0
        for h_lat, h_lng, h_intensity in hotspots:
            # Distance in degrees (rough, ~111km per degree)
            d = math.sqrt((coord.lat - h_lat)**2 + (coord.lng - h_lng)**2)
            
            # Influence radius ~0.02 deg ≈ 2.2km
            influence = 0.025
            if d < influence:
                # Smooth falloff: 1.0 at center, 0.0 at edge
                falloff = (1.0 - (d / influence)) ** 2
                score = h_intensity * falloff
                max_score = max(max_score, score)
        
        return min(max_score, 1.0)

    async def get_noise(self, coord: Coordinate) -> float:
        return self._proximity_score(coord, self.NOISE_HOTSPOTS)
    
    async def get_crowd(self, coord: Coordinate) -> float:
        return self._proximity_score(coord, self.CROWD_HOTSPOTS)
        
    async def get_nature(self, coord: Coordinate) -> float:
        return self._proximity_score(coord, self.NATURE_HOTSPOTS)
        
    async def get_shelter(self, coord: Coordinate) -> float:
        # Shelter roughly correlates with urban density
        return self._proximity_score(coord, self.CROWD_HOTSPOTS) * 0.7

class LiveSignalProvider(BaseSignalProvider):
    async def _get_cached_or_fetch(self, coord: Coordinate, cache_suffix: str, fetch_func) -> float:
        lat_r = round(coord.lat, 3)
        lng_r = round(coord.lng, 3)
        cache_key = f"sig:{lat_r}:{lng_r}:{cache_suffix}"
        
        val = signal_cache.get(cache_key)
        if val is not None:
            return val
            
        try:
            val = await fetch_func(lat_r, lng_r)
            signal_cache.set(cache_key, val, settings.SIGNAL_CACHE_TTL)
            return val
        except Exception as e:
            print(f"Live signal fetch failed for {cache_suffix}: {e}")
            return SimulatedSignalProvider()._hash_coord(coord, float(len(cache_suffix)))

    async def get_noise(self, coord: Coordinate) -> float:
        return await self._get_cached_or_fetch(coord, "noise", get_lta_traffic_data)
        
    async def get_crowd(self, coord: Coordinate) -> float:
        return await self._get_cached_or_fetch(coord, "crowd", get_onemap_crowd_data)
        
    async def get_nature(self, coord: Coordinate) -> float:
        return await self._get_cached_or_fetch(coord, "nature", get_green_space_data)
        
    async def get_shelter(self, coord: Coordinate) -> float:
        return SimulatedSignalProvider()._hash_coord(coord, 4.0)

# Factory function to get the current provider
def get_signal_provider(use_live: bool = False) -> BaseSignalProvider:
    if use_live:
        return LiveSignalProvider()
    return SimulatedSignalProvider()
