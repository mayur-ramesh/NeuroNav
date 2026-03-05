from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class RouteMode(str, Enum):
    walking = "walking"
    driving = "driving"
    cycling = "cycling"
    bus = "bus"
    mrt = "mrt"

class Coordinate(BaseModel):
    lat: float = Field(..., description="Latitude")
    lng: float = Field(..., description="Longitude")

class SensoryProfile(BaseModel):
    noise_sensitivity: float = Field(default=0.5, ge=0.0, le=1.0)
    crowd_sensitivity: float = Field(default=0.5, ge=0.0, le=1.0)
    predictability_preference: float = Field(default=0.5, ge=0.0, le=1.0)
    nature_preference: float = Field(default=0.5, ge=0.0, le=1.0)
    shelter_preference: float = Field(default=0.5, ge=0.0, le=1.0)

class RouteRequest(BaseModel):
    origin: Coordinate
    destination: Coordinate
    profile: SensoryProfile
    mode: RouteMode = Field(default=RouteMode.walking, description="Transportation mode")

class RouteSegment(BaseModel):
    start: Coordinate
    end: Coordinate
    distance_m: float = Field(..., description="Distance in meters")
    duration_s: float = Field(..., description="Expected duration in seconds")
    instruction: str = Field(..., description="Navigation instruction (e.g., 'Turn left')")
    maneuver_complexity: float = Field(default=0.0, description="Penalty for complex turns/intersections in this segment (0.0 to 1.0)")
    nature_bonus: float = Field(default=0.0, description="Reward for greenery/parks near segment (0.0 to 1.0)")
    sensory_score: float = Field(default=0.0, description="Calculated sensory cost for this segment")
    step_metadata: Optional[Dict[str, Any]] = Field(default=None, description="Metadata for transit, waiting, etc.")

class RouteOption(BaseModel):
    id: str = Field(..., description="Unique identifier for this route option")
    name: str = Field(..., description="Route name (e.g. 'Preferred Route' or 'Longest Route')")
    color: str = Field(..., description="Hex color code for rendering")
    role: str = Field(..., description="Route role (e.g. 'preferred' or 'longest')")
    distance_m: float = Field(..., description="Total distance in meters")
    duration_s: float = Field(..., description="Total expected duration in seconds")
    total_sensory_score: float = Field(..., description="Total aggregated sensory cost for the entire route")
    segments: List[RouteSegment]
    path: List[Coordinate] = Field(..., description="List of coordinates for rendering the polyline on a map")
    debug: Optional[Dict[str, Any]] = Field(default=None, description="Developer diagnostic info")

class RouteResponse(BaseModel):
    routes: List[RouteOption] = Field(..., description="Exactly two route options: Preferred and Longest")
