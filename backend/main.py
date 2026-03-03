from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from models import RouteRequest, RouteResponse
from services.routing import get_base_routes
from services.scoring import score_route

app = FastAPI(title="NeuroNav API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with actual frontend origin
    allow_credentials=True,
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
async def get_route(request: RouteRequest):
    """
    Main endpoint to get sensory-scored routes.
    """
    try:
        # 1. Fetch base routes from external routing engine
        base_routes = await get_base_routes(request)
        
        if not base_routes:
            raise HTTPException(status_code=404, detail="No routes found")
            
        # 2. Score each route asynchronously
        scoring_tasks = [score_route(route, request.profile) for route in base_routes]
        scored_routes = await asyncio.gather(*scoring_tasks)
        
        # 3. Sort by overall sensory score (lowest cost first)
        scored_routes.sort(key=lambda r: r.total_sensory_score)
        
        # 4. Assign Specialized Categories
        if scored_routes:
            # The lowest overall score is always the Recommended Calm Route
            scored_routes[0].category = "Recommended Calm Route"
            
            # Look for other specialties in the alternatives
            for i in range(1, len(scored_routes)):
                route = scored_routes[i]
                route.category = f"Alternative {i}" # Default
                
                # Feature extraction for categorization
                total_nature = sum([seg.nature_bonus for seg in route.segments])
                total_complexity = sum([seg.maneuver_complexity for seg in route.segments])
                
                # If nature bonus is particularly high (e.g. > 1.0)
                if total_nature > 1.0 and not any(r.category == "Most Nature Oriented" for r in scored_routes):
                    route.category = "Most Nature Oriented"
                
                # If complexity is extremely low (meaning it's mostly a straight path)
                elif total_complexity < 0.5 and not any(r.category == "Most Predictable" for r in scored_routes):
                    route.category = "Most Predictable"
                    
        return RouteResponse(routes=scored_routes)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
