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
    def _hash_coord(self, coord: Coordinate, salt: float) -> float:
        val = (round(coord.lat, 3) * 123.45 + round(coord.lng, 3) * 678.90 + salt)
        return abs(math.sin(val))

    async def get_noise(self, coord: Coordinate) -> float:
        return self._hash_coord(coord, 1.0)
    
    async def get_crowd(self, coord: Coordinate) -> float:
        return self._hash_coord(coord, 2.0)
        
    async def get_nature(self, coord: Coordinate) -> float:
        return self._hash_coord(coord, 3.0)
        
    async def get_shelter(self, coord: Coordinate) -> float:
        return self._hash_coord(coord, 4.0)

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
