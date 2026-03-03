from pydantic import BaseModel, Field
from typing import List, Optional

class Coordinate(BaseModel):
    lat: float = Field(..., description="Latitude")
    lng: float = Field(..., description="Longitude")

class SensoryProfile(BaseModel):
    noise_sensitivity: float = Field(default=0.5, ge=0.0, le=1.0, description="Sensitivity to noise (0.0 to 1.0)")
    crowd_sensitivity: float = Field(default=0.5, ge=0.0, le=1.0, description="Sensitivity to crowds (0.0 to 1.0)")
    predictability_preference: float = Field(default=0.5, ge=0.0, le=1.0, description="Preference for straightforward, low-turn paths (0.0 to 1.0)")
    nature_preference: float = Field(default=0.5, ge=0.0, le=1.0, description="Preference for parks/greenery (0.0 to 1.0)")

class RouteRequest(BaseModel):
    origin: Coordinate
    destination: Coordinate
    profile: SensoryProfile
    mode: str = Field(default="foot", description="Transportation mode: 'foot', 'bike', or 'driving'")

class RouteSegment(BaseModel):
    start: Coordinate
    end: Coordinate
    distance: float = Field(..., description="Distance in meters")
    duration: float = Field(..., description="Expected duration in seconds")
    instruction: str = Field(..., description="Navigation instruction (e.g., 'Turn left')")
    maneuver_complexity: float = Field(default=0.0, description="Penalty for complex turns/intersections in this segment (0.0 to 1.0)")
    nature_bonus: float = Field(default=0.0, description="Reward for greenery/parks near segment (0.0 to 1.0)")
    sensory_score: float = Field(default=0.0, description="Calculated sensory cost for this segment")

class RouteOption(BaseModel):
    id: str = Field(..., description="Unique identifier for this route option")
    category: str = Field(default="Normal Route", description="Specialized label like 'Nature Oriented'")
    total_distance: float = Field(..., description="Total distance in meters")
    total_duration: float = Field(..., description="Total expected duration in seconds")
    total_sensory_score: float = Field(..., description="Total aggregated sensory cost for the entire route")
    segments: List[RouteSegment]
    path: List[Coordinate] = Field(..., description="List of coordinates for rendering the polyline on a map")

class RouteResponse(BaseModel):
    routes: List[RouteOption] = Field(..., description="Ranked list of route options")
    
