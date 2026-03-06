from fastapi import FastAPI, HTTPException, Request, Header
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from models import RouteRequest, RouteResponse
from services.routing import fetch_routing_candidates
from services.scoring import score_route
from utils.geometry import is_in_singapore, calculate_overlap_ratio
from utils.config import settings
from utils.validation import validate_route

app = FastAPI(title="NeuroNav API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to NeuroNav API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/api/route", response_model=RouteResponse)
async def get_route(request: RouteRequest, x_diagnostics: bool = Header(False, alias="X-Diagnostics")):
    """
    Main endpoint returning exactly two routes: Preferred and Longest.
    All routes are validated for geometry, speed, and network correctness.
    """
    try:
        # 1. Enforce Singapore Bounds
        if not is_in_singapore(request.origin) or not is_in_singapore(request.destination):
            raise HTTPException(status_code=400, detail="Origin and destination must be within Singapore bounds.")

        # 2. Fetch route candidates (already validated inside routing engine)
        base_routes = []
        for attempt in range(3):
            try:
                base_routes = await fetch_routing_candidates(request)
                if base_routes:
                    break
            except Exception as e:
                if attempt == 2:
                    raise
                await asyncio.sleep(2 ** attempt)

        if not base_routes:
            raise HTTPException(status_code=404, detail="No valid routes found. The routing engine could not generate road-snapped routes for this origin/destination.")

        # 3. Score each route
        scoring_tasks = [score_route(route, request.profile, mode=request.mode) for route in base_routes]
        scored_routes = await asyncio.gather(*scoring_tasks)

        if not scored_routes:
            raise HTTPException(status_code=404, detail="No routes could be scored.")

        # 4. Final validation pass — reject any route that became invalid after scoring
        valid_scored = []
        rejected_reasons = []
        for route in scored_routes:
            result = validate_route(route, request.mode)
            if result:
                valid_scored.append(route)
            else:
                rejected_reasons.append(f"{route.id}: {result.reason}")

        if rejected_reasons:
            print(f"[SELECTION] Rejected {len(rejected_reasons)} routes: {rejected_reasons}")

        if not valid_scored:
            raise HTTPException(status_code=404, detail="All route candidates failed validation.")

        # 5. Route Selection
        # Preferred = lowest sensory score
        valid_scored.sort(key=lambda r: r.total_sensory_score)
        preferred_route = valid_scored[0]
        preferred_route.name = "Preferred Route"
        preferred_route.color = "#1d4ed8"
        preferred_route.role = "preferred"

        # Longest = maximum distance with acceptable overlap
        shortest_dist = min(r.distance_m for r in valid_scored)
        max_dist_allowed = shortest_dist * settings.MAX_LONGEST_RATIO

        dist_ranked = sorted(valid_scored, key=lambda r: r.distance_m, reverse=True)

        longest_route = None
        for candidate in dist_ranked:
            if candidate.id == preferred_route.id:
                continue
            if candidate.distance_m <= max_dist_allowed:
                overlap = calculate_overlap_ratio(preferred_route, candidate)
                if overlap <= settings.OVERLAP_THRESHOLD:
                    longest_route = candidate
                    longest_route.debug = {
                        "overlap": round(overlap, 3),
                        "dist": round(candidate.distance_m, 1),
                        "max_allowed": round(max_dist_allowed, 1),
                        "selection_reason": f"Longest diverse corridor (overlap {overlap:.1%})"
                    }
                    break

        # Fallback: pick any non-preferred route
        if not longest_route and len(valid_scored) > 1:
            for candidate in dist_ranked:
                if candidate.id != preferred_route.id:
                    longest_route = candidate
                    longest_route.debug = {"selection_reason": "Fallback — best available alternative"}
                    break

        # Ultimate fallback: duplicate preferred
        if not longest_route:
            import copy
            longest_route = copy.deepcopy(preferred_route)
            longest_route.id = preferred_route.id + "-alt"
            longest_route.debug = {"selection_reason": "Duplicated preferred (no alternatives available)"}

        longest_route.name = "Longest Route"
        longest_route.color = "#dc2626"
        longest_route.role = "longest"

        # 6. Attach diagnostics
        if x_diagnostics:
            preferred_route.debug = preferred_route.debug or {}
            preferred_route.debug.update({
                "provider": "osrm",
                "candidate_count": len(base_routes),
                "valid_count": len(valid_scored),
                "rejected_count": len(rejected_reasons),
                "selection_reason": "Lowest sensory cost",
                "speed_kmh": round((preferred_route.distance_m / max(1, preferred_route.duration_s)) * 3.6, 1),
            })

        return RouteResponse(routes=[preferred_route, longest_route])

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Signals endpoint (for map overlays)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

from pydantic import BaseModel as PydanticBaseModel
from typing import List as TypingList

class SignalPoint(PydanticBaseModel):
    lat: float
    lng: float
    noise: float
    crowd: float
    nature: float

class SignalsResponse(PydanticBaseModel):
    points: TypingList[SignalPoint]

@app.get("/api/signals", response_model=SignalsResponse)
async def get_signals(
    min_lat: float = 1.25,
    max_lat: float = 1.45,
    min_lng: float = 103.65,
    max_lng: float = 104.0,
    resolution: int = 12
):
    """
    Returns a grid of environmental signal data (noise, crowd, nature)
    for overlay visualization on the map. Uses simulated Singapore data.
    """
    from services.signals import SimulatedSignalProvider
    from models import Coordinate

    provider = SimulatedSignalProvider()
    points = []

    lat_step = (max_lat - min_lat) / resolution
    lng_step = (max_lng - min_lng) / resolution

    for i in range(resolution + 1):
        for j in range(resolution + 1):
            lat = min_lat + i * lat_step
            lng = min_lng + j * lng_step
            coord = Coordinate(lat=lat, lng=lng)

            noise = await provider.get_noise(coord)
            crowd = await provider.get_crowd(coord)
            nature = await provider.get_nature(coord)

            points.append(SignalPoint(
                lat=lat, lng=lng,
                noise=round(noise, 3),
                crowd=round(crowd, 3),
                nature=round(nature, 3)
            ))

    return SignalsResponse(points=points)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
