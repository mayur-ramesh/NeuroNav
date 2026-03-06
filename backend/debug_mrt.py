"""Direct MRT routing debug — bypass API to see exact error."""
import asyncio
import sys
sys.path.insert(0, '.')

from models import RouteRequest, Coordinate, SensoryProfile, RouteMode
from services.routing import _fetch_mrt_candidates
from utils.validation import validate_route

async def main():
    req = RouteRequest(
        origin=Coordinate(lat=1.3048, lng=103.8318),
        destination=Coordinate(lat=1.2834, lng=103.8607),
        mode=RouteMode.mrt,
        profile=SensoryProfile()
    )
    
    print("Fetching MRT candidates...")
    routes = await _fetch_mrt_candidates(req)
    print(f"Generated {len(routes)} MRT candidates")
    
    for rt in routes:
        print(f"\n  Route {rt.id}:")
        print(f"    distance_m: {rt.distance_m:.1f}")
        print(f"    duration_s: {rt.duration_s:.1f} ({rt.duration_s/60:.1f} min)")
        print(f"    path points: {len(rt.path)}")
        print(f"    segments: {len(rt.segments)}")
        speed = rt.distance_m / max(1, rt.duration_s) * 3.6
        print(f"    implied speed: {speed:.1f} km/h")
        
        for seg in rt.segments:
            print(f"    seg: {seg.instruction} | {seg.distance_m:.0f}m | {seg.duration_s:.0f}s")
        
        # Validate
        result = validate_route(rt, RouteMode.mrt)
        print(f"    validation: {result}")

asyncio.run(main())
