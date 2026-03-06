import httpx
import polyline
import math
from typing import List, Optional
from models import RouteRequest, RouteOption, RouteSegment, Coordinate, RouteMode
from utils.cache import route_cache
from utils.config import settings

async def fetch_routing_candidates(request: RouteRequest) -> List[RouteOption]:
    """
    Fetch raw routing candidates. Will return at least 5 candidates for walk/drive/cycle,
    and at least 3 for bus/mrt to ensure diversity for selection.
    """
    cache_key = f"route:{request.mode.value}:{request.origin.lat},{request.origin.lng}:{request.destination.lat},{request.destination.lng}"
    cached = route_cache.get(cache_key)
    if cached:
        return cached

    routes = []
    
    if request.mode in [RouteMode.walking, RouteMode.driving, RouteMode.cycling]:
        osrm_profile = "foot"
        if request.mode == RouteMode.driving:
            osrm_profile = "car"
        elif request.mode == RouteMode.cycling:
            osrm_profile = "bike"
            
        try:
            coords = f"{request.origin.lng},{request.origin.lat};{request.destination.lng},{request.destination.lat}"
            url = f"{settings.OSRM_BASE_URL}/route/v1/{osrm_profile}/{coords}"
            
            params = {
                "alternatives": "3",
                "steps": "true",
                "geometries": "polyline",
                "overview": "full"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=5.0)
                response.raise_for_status()
                data = response.json()
                
                for i, route_data in enumerate(data.get("routes", [])):
                    dist = route_data.get("distance", 0.0)
                    dur = route_data.get("duration", 0.0)
                    
                    geo_str = route_data.get("geometry", "")
                    path_coords = []
                    if geo_str:
                        pts = polyline.decode(geo_str)
                        path_coords = [Coordinate(lat=p[0], lng=p[1]) for p in pts]
                    else:
                        path_coords = [request.origin, request.destination]
                        
                    segments = _parse_osrm_legs(route_data.get("legs", []), request.origin)
                    
                    if not segments:
                        segments = [
                            RouteSegment(
                                start=request.origin, end=request.destination,
                                distance_m=dist, duration_s=dur, instruction="Proceed to destination"
                            )
                        ]
                        
                    opt = RouteOption(
                        id=f"osrm-{i}",
                        name="Candidate",
                        color="#000000",
                        role="candidate",
                        distance_m=dist,
                        duration_s=dur,
                        total_sensory_score=0.0, # Filled in later
                        segments=segments,
                        path=path_coords
                    )
                    routes.append(opt)
        except Exception as e:
            print(f"OSRM Routing failed: {e}")
            
        # Ensure we have at least 5 variants for walk/drive/cycle
        if len(routes) < 5:
            routes.extend(_generate_mock_routes(request, count=5 - len(routes), start_idx=len(routes)))
            
    else:
        # Transit modes prototype
        routes = _generate_transit_prototype(request)
        
    route_cache.set(cache_key, routes, settings.ROUTE_CACHE_TTL)
    return routes

def _parse_osrm_legs(legs: list, origin: Coordinate) -> List[RouteSegment]:
    segments = []
    if not legs: return segments
    for step in legs[0].get("steps", []):
        dist = step.get("distance", 0.0)
        dur = step.get("duration", 0.0)
        instruction = step.get("maneuver", {}).get("type", "Proceed")
        
        intersections = step.get("intersections", [])
        if intersections:
            loc = intersections[0].get("location", [origin.lng, origin.lat])
            start_coord = Coordinate(lat=loc[1], lng=loc[0])
        else:
            start_coord = origin
            
        segments.append(RouteSegment(
            start=start_coord,
            end=start_coord,
            distance_m=dist,
            duration_s=dur,
            instruction=instruction
        ))
    return segments

def _generate_mock_routes(request: RouteRequest, count: int = 5, start_idx: int = 0) -> List[RouteOption]:
    speed_mps = 1.4
    if request.mode == RouteMode.driving: speed_mps = 12.0
    elif request.mode == RouteMode.cycling: speed_mps = 4.0
    
    lat_diff = request.destination.lat - request.origin.lat
    lng_diff = request.destination.lng - request.origin.lng
    base_dist = math.sqrt(lat_diff**2 + lng_diff**2) * 111000
    base_dist = max(100.0, base_dist)
    
    import random
    random.seed(42 + start_idx)  # Deterministic but varied
    
    options = []
    for i in range(count):
        dist = base_dist * (1.1 + (i * 0.15))
        dur = dist / speed_mps
        
        # Generate a realistic multi-waypoint path (10-15 intermediate points)
        num_points = 12 + i * 2  
        path_coords = [request.origin]
        
        # Create perpendicular offset for route diversity
        perp_lat = -lng_diff  
        perp_lng = lat_diff
        perp_len = math.sqrt(perp_lat**2 + perp_lng**2) or 1.0
        perp_lat /= perp_len
        perp_lng /= perp_len
        
        # Each route has a different primary curve direction
        curve_direction = (1 if i % 2 == 0 else -1) * (0.3 + i * 0.15)
        
        for j in range(1, num_points):
            t = j / num_points  # Progress along route 0..1
            
            # Base position along direct line
            lat = request.origin.lat + lat_diff * t
            lng = request.origin.lng + lng_diff * t
            
            # Add smooth curve (sine wave along perpendicular)
            curve_factor = math.sin(t * math.pi) * curve_direction * 0.008
            lat += perp_lat * curve_factor
            lng += perp_lng * curve_factor
            
            # Add small random jitter to simulate road following
            jitter = 0.0008  
            lat += random.uniform(-jitter, jitter)
            lng += random.uniform(-jitter, jitter)
            
            path_coords.append(Coordinate(lat=round(lat, 6), lng=round(lng, 6)))
        
        path_coords.append(request.destination)
        
        # Create segments from consecutive path points
        segments = []
        for k in range(len(path_coords) - 1):
            seg_dist = dist / (len(path_coords) - 1)
            seg_dur = dur / (len(path_coords) - 1)
            instruction = "Proceed" if k < len(path_coords) - 2 else "Arrive at destination"
            segments.append(RouteSegment(
                start=path_coords[k], end=path_coords[k+1],
                distance_m=seg_dist, duration_s=seg_dur,
                instruction=instruction
            ))
        
        opt = RouteOption(
            id=f"mock-{request.mode.value}-{start_idx+i}",
            name="Candidate",
            color="#888888",
            role="candidate",
            distance_m=dist,
            duration_s=dur,
            total_sensory_score=0.0,
            segments=segments,
            path=path_coords
        )
        options.append(opt)
    return options

def _generate_transit_prototype(request: RouteRequest) -> List[RouteOption]:
    import random
    random.seed(99)
    
    options = []
    lat_diff = request.destination.lat - request.origin.lat
    lng_diff = request.destination.lng - request.origin.lng
    base_dist = math.sqrt(lat_diff**2 + lng_diff**2) * 111000
    base_dist = max(500.0, base_dist)
    
    speed_mps = 5.0 if request.mode == RouteMode.bus else 10.0
    
    # Perpendicular direction for route diversity
    perp_lat = -lng_diff
    perp_lng = lat_diff
    perp_len = math.sqrt(perp_lat**2 + perp_lng**2) or 1.0
    perp_lat /= perp_len
    perp_lng /= perp_len
    
    for i in range(3):
        dist = base_dist * (1.2 + (i * 0.1))
        waiting_time = 300 + (i * 120)
        moving_time = dist / speed_mps
        transfer_penalty = 0 if i == 0 else 300
        total_time = waiting_time + moving_time + transfer_penalty
        
        # Generate multi-waypoint path
        num_points = 10 + i * 3
        path_coords = [request.origin]
        curve_dir = (1 if i % 2 == 0 else -1) * (0.4 + i * 0.2)
        
        for j in range(1, num_points):
            t = j / num_points
            lat = request.origin.lat + lat_diff * t
            lng = request.origin.lng + lng_diff * t
            
            curve_factor = math.sin(t * math.pi) * curve_dir * 0.006
            lat += perp_lat * curve_factor
            lng += perp_lng * curve_factor
            lat += random.uniform(-0.0006, 0.0006)
            lng += random.uniform(-0.0006, 0.0006)
            
            path_coords.append(Coordinate(lat=round(lat, 6), lng=round(lng, 6)))
        
        path_coords.append(request.destination)
        
        # Station is roughly at midpoint
        station = path_coords[len(path_coords) // 2]
        
        seg1 = RouteSegment(start=request.origin, end=station, distance_m=dist*0.2, duration_s=waiting_time + moving_time*0.2, instruction="Walk to Station/Stop")
        seg2 = RouteSegment(start=station, end=request.destination, distance_m=dist*0.8, duration_s=moving_time*0.8 + transfer_penalty, instruction=f"Take {request.mode.value} to destination")
        
        opt = RouteOption(
            id=f"transit-{request.mode.value}-{i}",
            name="Transit Itinerary",
            color="#000000",
            role="candidate",
            distance_m=dist,
            duration_s=total_time,
            total_sensory_score=0.0,
            segments=[seg1, seg2],
            path=path_coords
        )
        options.append(opt)
    return options
