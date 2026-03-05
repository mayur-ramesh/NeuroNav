from fastapi import FastAPI, HTTPException, Request, Header
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from models import RouteRequest, RouteResponse
from services.routing import fetch_routing_candidates
from services.scoring import score_route
from utils.geometry import is_in_singapore, calculate_overlap_ratio
from utils.config import settings

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
    We enforce Singapore Bounding Box, evaluate sensory costs, 
    and pick exactly 2 routes strictly adhering to constraints.
    """
    try:
        # 1. Enforce Singapore Bounds
        if not is_in_singapore(request.origin) or not is_in_singapore(request.destination):
            raise HTTPException(status_code=400, detail="Origin and destination must be strictly within Singapore bounds.")
            
        # 2. Fetch Base Routes with retry resilient capability
        base_routes = []
        for attempt in range(3):
            try:
                base_routes = await fetch_routing_candidates(request)
                if base_routes: break
            except Exception as e:
                if attempt == 2: raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                
        if not base_routes:
            raise HTTPException(status_code=404, detail="No routes found")
            
        # 3. Score Each Route Asynchronously
        scoring_tasks = [score_route(route, request.profile, mode=request.mode) for route in base_routes]
        scored_routes = await asyncio.gather(*scoring_tasks)
        
        if len(scored_routes) == 0:
            raise HTTPException(status_code=404, detail="No routes could be scored.")
            
        # 4. Route Selection Logic
        
        # Set Preferred Route (minimum sensory score)
        scored_routes.sort(key=lambda r: r.total_sensory_score)
        preferred_route = scored_routes[0]
        preferred_route.name = "Preferred Route"
        preferred_route.color = "#1d4ed8"  # requested blue
        preferred_route.role = "preferred"
        
        # Candidate array minus preferred route
        shortest_dist = min([r.distance_m for r in scored_routes])
        max_dist_allowed = shortest_dist * settings.MAX_LONGEST_RATIO
        
        # Sort rest by distance descending
        dist_ranked = sorted(scored_routes, key=lambda r: r.distance_m, reverse=True)
        
        longest_route = None
        for candidate in dist_ranked:
            if candidate.id == preferred_route.id: continue
            
            if candidate.distance_m <= max_dist_allowed:
                overlap = calculate_overlap_ratio(preferred_route, candidate)
                if overlap <= settings.OVERLAP_THRESHOLD:
                    longest_route = candidate
                    longest_route.debug = {"overlap": overlap, "dist": candidate.distance_m, "max_allowed": max_dist_allowed}
                    break
                    
        # Fallback if no specific overlap constraint matched
        if not longest_route and len(scored_routes) > 1:
            for candidate in dist_ranked:
                if candidate.id != preferred_route.id:
                    longest_route = candidate
                    break
                    
        # Ultimate fallback (duplicate if only 1 route was generated somehow)
        if not longest_route:
            import copy
            longest_route = copy.deepcopy(preferred_route)
            longest_route.id = longest_route.id + "-alt"
            
        longest_route.name = "Longest Route"
        longest_route.color = "#dc2626"    # requested red
        longest_route.role = "longest"
        
        # 5. Attach Diagnostics
        if x_diagnostics:
            preferred_route.debug = preferred_route.debug or {}
            preferred_route.debug["provider"] = settings.ROUTING_PROVIDER
            preferred_route.debug["candidate_count"] = len(base_routes)
            preferred_route.debug["selection_reason"] = "Lowest sensory cost"
            
            longest_route.debug = longest_route.debug or {}
            longest_route.debug["selection_reason"] = "Maximum allowed diverse distance"
            
        return RouteResponse(routes=[preferred_route, longest_route])
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
