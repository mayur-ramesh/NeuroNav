import httpx
import os
import polyline
from models import RouteRequest, RouteOption, RouteSegment, Coordinate
from typing import List

# OSRM (Open Source Routing Machine) API - No key required for demo usage
# OSRM_BASE_URL = "http://router.project-osrm.org/route/v1/foot" # This constant is no longer needed as the profile is dynamic

async def get_base_routes(request: RouteRequest) -> List[RouteOption]:
    """
    Queries OSRM to get a walking route between origin and destination.
    """
    
    # OSRM format: {longitude},{latitude};{longitude},{latitude}
    coords = f"{request.origin.lng},{request.origin.lat};{request.destination.lng},{request.destination.lat}"
    
    # Use the appropriate routing profile based on transport mode from the request
    # OSRM profiles: foot, car, bike
    osrm_profile = request.mode.value if hasattr(request.mode, 'value') else request.mode # Assuming request.mode is an Enum or string
    url = f"http://router.project-osrm.org/route/v1/{osrm_profile}/{coords}"
    
    params = {
        "alternatives": "true",
        "steps": "true",
        "geometries": "polyline",
        "overview": "full"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            routes = []
            for i, route_data in enumerate(data.get("routes", [])):
                route_id = f"osrm-{i}"
                distance = route_data.get("distance", 0.0)
                duration = route_data.get("duration", 0.0)
                
                # Decode the polyline points into a list of Coordinates
                geometry_str = route_data.get("geometry", "")
                if geometry_str:
                    # polyline.decode returns (lat, lng) tuples
                    points = polyline.decode(geometry_str)
                    path_coords = [Coordinate(lat=p[0], lng=p[1]) for p in points]
                else:
                    path_coords = [request.origin, request.destination]
                
                segments = []
                # OSRM groups steps into 'legs' (usually just 1 leg for A->B)
                legs = route_data.get("legs", [])
                if legs:
                    for step in legs[0].get("steps", []):
                        step_dist = step.get("distance", 0.0)
                        step_dur = step.get("duration", 0.0)
                        instruction = step.get("maneuver", {}).get("type", "Walk")
                        
                        # Just grab the starting point of the step from the intersection
                        intersections = step.get("intersections", [])
                        if intersections and len(intersections) > 0:
                            loc = intersections[0].get("location", [request.origin.lng, request.origin.lat])
                            start_coord = Coordinate(lat=loc[1], lng=loc[0])
                        else:
                            start_coord = request.origin
                            
                        # It's hard to get the exact end coord of a step without parsing the next step, 
                        # so we approximate that the start and end of the segment are the same for scoring purposes.
                        end_coord = start_coord
                        
                        seg = RouteSegment(
                            start=start_coord,
                            end=end_coord,
                            distance=step_dist,
                            duration=step_dur,
                            instruction=instruction,
                            sensory_score=0.0
                        )
                        segments.append(seg)
                
                # Fallback if no steps are present or parsing fails:
                if not segments:
                     segments = [
                         RouteSegment(
                             start=request.origin,
                             end=request.destination,
                             distance=distance,
                             duration=duration,
                             instruction="Walk towards destination",
                             sensory_score=0.0
                         )
                     ]

                opt = RouteOption(
                    id=route_id,
                    total_distance=distance,
                    total_duration=duration,
                    total_sensory_score=0.0,  # Will be calculated by scoring.py
                    segments=segments,
                    path=path_coords
                )
                routes.append(opt)
                
            # If OSRM returns routes, return them!
            if routes:
                return routes
    except Exception as e:
        print(f"Error calling OSRM API: {e}")
        
    # If the API fails, fall back to the mock route generator
    return _generate_mock_routes(request)

def _generate_mock_routes(request: RouteRequest) -> List[RouteOption]:
     # Very simple mock generating 3 artificial routes 
     # with slightly varied distances and durations, using the 
     # origin and destination as a 2-point polyline.
     options = []
     for i in range(3):
         distance = (i+1) * 1000.0 # 1km, 2km, 3km
         duration = distance / 1.4 # ~1.4 m/s walking speed
         
         # Mock steps
         seg1 = RouteSegment(
             start=request.origin,
             end=request.destination,
             distance=distance,
             duration=duration,
             instruction=f"Walk straight via Route {i+1}",
             sensory_score=0.0
         )
         
         opt = RouteOption(
             id=f"mock-route-{i+1}",
             total_distance=distance,
             total_duration=duration,
             total_sensory_score=0.0,
             segments=[seg1],
             path=[request.origin, request.destination]
         )
         options.append(opt)
     return options
