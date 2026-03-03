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
async def calculate_route(request: RouteRequest):
    # 1. Get base alternative routes
    base_routes = await get_base_routes(request)
    
    # 2. Score each route in parallel
    scored_routes = await asyncio.gather(
        *(score_route(route, request.profile) for route in base_routes)
    )
    
    # 3. Sort by total_sensory_score ascending (lowest cost is best)
    ranked_routes = sorted(scored_routes, key=lambda r: r.total_sensory_score)
    
    return RouteResponse(routes=ranked_routes)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
