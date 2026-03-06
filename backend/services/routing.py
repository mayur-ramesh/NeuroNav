"""
NeuroNav Routing Engine — OSRM-based, road-snapped, mode-specific routing.
All route geometry comes from OSRM (foot/car/bike profiles).
No mathematical curve generation. Every route stays on the real road/path network.
"""
import httpx
import polyline
import math
from typing import List
from models import RouteRequest, RouteOption, RouteSegment, Coordinate, RouteMode
from utils.cache import route_cache
from utils.config import settings
from utils.validation import validate_route, ValidationResult

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Speed models (m/s) and penalty constants
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WALKING_SPEED_MPS = 1.25       # ~4.5 km/h
CYCLING_SPEED_MPS = 4.17       # ~15 km/h
BUS_ROAD_SPEED_MPS = 5.56      # ~20 km/h (bus average including stop-and-go)
MRT_SPEED_MPS = 12.5           # ~45 km/h (MRT average between stations)

# Penalties in seconds
WALKING_CROSSING_PENALTY = 15.0     # Per crossing/traffic light
WALKING_PENALTY_PER_KM = 30.0      # General penalty for intersections per km
BUS_WAIT_TIME_S = 240.0            # Average bus wait (4 minutes)
BUS_DWELL_PER_STOP_S = 25.0        # Bus dwell time per stop
BUS_STOPS_PER_KM = 2.5             # Average bus stops per km
BUS_WALK_SPEED_MPS = 1.25          # Walking to/from bus stop
BUS_WALK_DIST_M = 400.0            # Average walk to nearest bus stop
MRT_WAIT_TIME_S = 120.0            # Average MRT wait (2 minutes)
MRT_TRANSFER_PENALTY_S = 240.0     # Transfer between lines (4 minutes)
MRT_WALK_SPEED_MPS = 1.25          # Walking to/from station
MRT_STATION_DWELL_S = 30.0         # Dwell per intermediate station

# Intermediate waypoints for generating diverse OSRM routes in Singapore
# These are real Singapore locations used as via-points to force different corridors
DIVERSITY_WAYPOINTS = [
    Coordinate(lat=1.3521, lng=103.8198),   # Central — Ang Mo Kio area
    Coordinate(lat=1.3191, lng=103.8455),   # Toa Payoh
    Coordinate(lat=1.3073, lng=103.7904),   # Buona Vista
    Coordinate(lat=1.3326, lng=103.7422),   # Jurong East
    Coordinate(lat=1.3498, lng=103.8734),   # Serangoon
    Coordinate(lat=1.3164, lng=103.8826),   # Aljunied
    Coordinate(lat=1.2944, lng=103.8060),   # Queenstown
    Coordinate(lat=1.3114, lng=103.8716),   # Kallang
]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Main entry point
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def fetch_routing_candidates(request: RouteRequest) -> List[RouteOption]:
    """
    Fetch route candidates for the given request. All geometry is road-snapped via OSRM.
    Returns validated candidates ready for scoring and selection.
    """
    cache_key = f"route:{request.mode.value}:{request.origin.lat:.5f},{request.origin.lng:.5f}:{request.destination.lat:.5f},{request.destination.lng:.5f}"
    cached = route_cache.get(cache_key)
    if cached:
        return cached

    routes = []

    if request.mode in [RouteMode.walking, RouteMode.driving, RouteMode.cycling]:
        routes = await _fetch_osrm_candidates(request)
    elif request.mode == RouteMode.bus:
        routes = await _fetch_bus_candidates(request)
    elif request.mode == RouteMode.mrt:
        routes = await _fetch_mrt_candidates(request)

    # Validate all candidates — reject invalid ones
    valid_routes = []
    for route in routes:
        result = validate_route(route, request.mode)
        if result:
            valid_routes.append(route)
        else:
            print(f"[VALIDATION] Rejected route {route.id}: {result.reason}")

    if valid_routes:
        route_cache.set(cache_key, valid_routes, settings.ROUTE_CACHE_TTL)

    return valid_routes


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# OSRM routing for walk / drive / cycle
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

OSRM_PROFILE_MAP = {
    RouteMode.walking: "foot",
    RouteMode.driving: "car",
    RouteMode.cycling: "bike",
}

async def _fetch_osrm_candidates(request: RouteRequest) -> List[RouteOption]:
    """
    Fetch candidates from OSRM with correct profile.
    Step 1: Direct OSRM query with alternatives=true (gets 1-3 road-snapped routes).
    Step 2: Generate additional candidates by routing via intermediate waypoints.
    All geometry is guaranteed road-snapped by OSRM.
    """
    profile = OSRM_PROFILE_MAP[request.mode]
    routes = []

    # Step 1: Direct route with alternatives
    direct_routes = await _osrm_query(request.origin, request.destination, profile, alternatives=3)
    for i, r in enumerate(direct_routes):
        r.id = f"osrm-direct-{i}"
        # Adjust duration for walking/cycling penalties
        r.duration_s = _apply_mode_penalties(r.distance_m, r.duration_s, request.mode)
        routes.append(r)

    # Step 2: Waypoint-diversified routes (via different Singapore corridors)
    # Only try waypoints that are roughly between origin and destination
    mid_lat = (request.origin.lat + request.destination.lat) / 2
    mid_lng = (request.origin.lng + request.destination.lng) / 2
    straight_dist = _haversine(request.origin, request.destination)

    wp_tried = 0
    for wp in DIVERSITY_WAYPOINTS:
        if wp_tried >= 3:  # Limit to 3 waypoint attempts
            break

        # Only use waypoints that are within reasonable detour range
        wp_to_mid = math.sqrt((wp.lat - mid_lat) ** 2 + (wp.lng - mid_lng) ** 2)
        if wp_to_mid > 0.06:  # Too far from the corridor
            continue

        # Skip waypoints too close to origin or destination
        wp_to_origin = _haversine(wp, request.origin)
        wp_to_dest = _haversine(wp, request.destination)
        if wp_to_origin < 500 or wp_to_dest < 500:
            continue

        wp_tried += 1
        via_routes = await _osrm_query_via(request.origin, wp, request.destination, profile)
        for j, r in enumerate(via_routes):
            r.id = f"osrm-via-{wp_tried}-{j}"
            r.duration_s = _apply_mode_penalties(r.distance_m, r.duration_s, request.mode)
            # Only keep if distance is within 2x the shortest direct route
            if routes and r.distance_m > routes[0].distance_m * settings.MAX_LONGEST_RATIO:
                continue
            routes.append(r)

    if not routes:
        print("[ROUTING] No OSRM routes returned — all attempts failed")

    return routes


async def _osrm_query(origin: Coordinate, dest: Coordinate, profile: str, alternatives: int = 3) -> List[RouteOption]:
    """Query OSRM for routes between two points."""
    coords_str = f"{origin.lng},{origin.lat};{dest.lng},{dest.lat}"
    url = f"{settings.OSRM_BASE_URL}/route/v1/{profile}/{coords_str}"
    params = {
        "alternatives": str(alternatives),
        "steps": "true",
        "geometries": "polyline",
        "overview": "full"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=8.0)
            response.raise_for_status()
            data = response.json()
            return _parse_osrm_routes(data, origin, dest)
    except Exception as e:
        print(f"[OSRM] Query failed for {profile}: {e}")
        return []


async def _osrm_query_via(origin: Coordinate, via: Coordinate, dest: Coordinate, profile: str) -> List[RouteOption]:
    """Query OSRM for a route via an intermediate waypoint."""
    coords_str = f"{origin.lng},{origin.lat};{via.lng},{via.lat};{dest.lng},{dest.lat}"
    url = f"{settings.OSRM_BASE_URL}/route/v1/{profile}/{coords_str}"
    params = {
        "alternatives": "false",
        "steps": "true",
        "geometries": "polyline",
        "overview": "full"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=8.0)
            response.raise_for_status()
            data = response.json()
            return _parse_osrm_routes(data, origin, dest)
    except Exception as e:
        print(f"[OSRM] Via-query failed: {e}")
        return []


def _parse_osrm_routes(data: dict, origin: Coordinate, dest: Coordinate) -> List[RouteOption]:
    """Parse OSRM JSON response into RouteOption list."""
    routes = []
    for i, route_data in enumerate(data.get("routes", [])):
        dist = route_data.get("distance", 0.0)
        dur = route_data.get("duration", 0.0)

        # Decode geometry — this is real road-snapped geometry from OSRM
        geo_str = route_data.get("geometry", "")
        path_coords = []
        if geo_str:
            pts = polyline.decode(geo_str)
            path_coords = [Coordinate(lat=p[0], lng=p[1]) for p in pts]
        else:
            path_coords = [origin, dest]

        # Parse step-by-step segments
        segments = _parse_osrm_legs(route_data.get("legs", []), origin)
        if not segments:
            segments = [RouteSegment(
                start=origin, end=dest,
                distance_m=dist, duration_s=dur,
                instruction="Proceed to destination"
            )]

        opt = RouteOption(
            id=f"osrm-{i}",
            name="Candidate",
            color="#000000",
            role="candidate",
            distance_m=dist,
            duration_s=dur,
            total_sensory_score=0.0,
            segments=segments,
            path=path_coords
        )
        routes.append(opt)

    return routes


def _parse_osrm_legs(legs: list, origin: Coordinate) -> List[RouteSegment]:
    """Parse OSRM leg steps into RouteSegment list."""
    segments = []
    if not legs:
        return segments
    for leg in legs:
        for step in leg.get("steps", []):
            dist = step.get("distance", 0.0)
            dur = step.get("duration", 0.0)
            maneuver = step.get("maneuver", {})
            instruction = maneuver.get("type", "Proceed")
            modifier = maneuver.get("modifier", "")
            if modifier:
                instruction = f"{instruction} {modifier}"

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


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Bus routing — OSRM car profile + bus-specific penalties
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def _fetch_bus_candidates(request: RouteRequest) -> List[RouteOption]:
    """
    Bus routing: OSRM car profile (buses use roads) + bus-specific penalties.
    Adds walk-to-stop, wait time, dwell time, and slower speed.
    """
    # Get road-snapped routes via OSRM car profile
    road_routes = await _osrm_query(request.origin, request.destination, "car", alternatives=3)

    bus_routes = []
    for i, route in enumerate(road_routes):
        # Calculate bus-specific timing
        road_dist = route.distance_m
        num_stops = max(1, int(road_dist / 1000 * BUS_STOPS_PER_KM))

        # Walk to bus stop + wait
        walk_to_stop_time = BUS_WALK_DIST_M / BUS_WALK_SPEED_MPS
        wait_time = BUS_WAIT_TIME_S

        # Bus travel time (slower than car due to stops, traffic, acceleration/deceleration)
        bus_travel_time = road_dist / BUS_ROAD_SPEED_MPS

        # Dwell time at stops
        dwell_time = num_stops * BUS_DWELL_PER_STOP_S

        # Walk from last stop to destination
        walk_from_stop_time = BUS_WALK_DIST_M / BUS_WALK_SPEED_MPS

        total_duration = walk_to_stop_time + wait_time + bus_travel_time + dwell_time + walk_from_stop_time
        total_distance = road_dist + (BUS_WALK_DIST_M * 2)

        # Build segments
        segments = [
            RouteSegment(
                start=request.origin, end=route.path[0] if route.path else request.origin,
                distance_m=BUS_WALK_DIST_M, duration_s=walk_to_stop_time,
                instruction="Walk to bus stop",
                step_metadata={"type": "walk"}
            ),
            RouteSegment(
                start=route.path[0] if route.path else request.origin,
                end=route.path[0] if route.path else request.origin,
                distance_m=0, duration_s=wait_time,
                instruction="Wait for bus (~4 min)",
                step_metadata={"type": "wait", "wait_minutes": round(wait_time / 60, 1)}
            ),
            RouteSegment(
                start=route.path[0] if route.path else request.origin,
                end=route.path[-1] if route.path else request.destination,
                distance_m=road_dist, duration_s=bus_travel_time + dwell_time,
                instruction=f"Ride bus ({num_stops} stops)",
                step_metadata={"type": "ride", "stops": num_stops}
            ),
            RouteSegment(
                start=route.path[-1] if route.path else request.destination,
                end=request.destination,
                distance_m=BUS_WALK_DIST_M, duration_s=walk_from_stop_time,
                instruction="Walk to destination",
                step_metadata={"type": "walk"}
            ),
        ]

        bus_route = RouteOption(
            id=f"bus-{i}",
            name="Bus Itinerary",
            color="#000000",
            role="candidate",
            distance_m=total_distance,
            duration_s=total_duration,
            total_sensory_score=0.0,
            segments=segments,
            path=route.path,  # Use the OSRM road-snapped geometry
        )
        bus_routes.append(bus_route)

    return bus_routes


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MRT routing — station-based with walk legs via OSRM foot
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def _fetch_mrt_candidates(request: RouteRequest) -> List[RouteOption]:
    """
    MRT routing: walk to nearest station → ride MRT along real line geometry → walk to destination.
    Uses actual Singapore MRT station coordinates for valid rail geometry.
    """
    from data.mrt_stations import find_nearest_station, get_station_path, count_stations_between

    # Find nearest stations to origin and destination
    o_name, o_station, o_walk_dist, o_lines = find_nearest_station(request.origin)
    d_name, d_station, d_walk_dist, d_lines = find_nearest_station(request.destination)

    # Generate up to 3 MRT candidates using different destination-area stations
    candidates = [(o_name, o_station, o_walk_dist, d_name, d_station, d_walk_dist)]

    # Try a second origin station for diversity
    from data.mrt_stations import MRT_STATIONS
    for name, lat, lng, lines in MRT_STATIONS:
        if name == o_name:
            continue
        alt_dist = _haversine(request.origin, Coordinate(lat=lat, lng=lng))
        if alt_dist < 2000 and alt_dist > o_walk_dist * 1.3:
            candidates.append((name, Coordinate(lat=lat, lng=lng), alt_dist, d_name, d_station, d_walk_dist))
            break

    mrt_routes = []
    for idx, (on, os, owd, dn, ds, dwd) in enumerate(candidates):
        # Walk to origin station (via OSRM foot, for road-snapped walk path)
        walk_to = await _osrm_query(request.origin, os, "foot", alternatives=1)
        walk_to_path = walk_to[0].path if walk_to else [request.origin, os]
        walk_to_dist = walk_to[0].distance_m if walk_to else owd
        walk_to_dur = walk_to_dist / MRT_WALK_SPEED_MPS

        # MRT ride: get station path (real station coordinates)
        rail_path = get_station_path(os, ds)
        num_stations = max(1, len(rail_path) - 1)

        # Calculate rail distance from station coordinates
        rail_dist = 0.0
        for j in range(len(rail_path) - 1):
            rail_dist += _haversine(rail_path[j], rail_path[j + 1])

        # MRT timing: ride + dwell + possible transfer
        ride_time = rail_dist / MRT_SPEED_MPS
        dwell_time = num_stations * MRT_STATION_DWELL_S
        # Detect transfer using known line data from station lookup
        o_station_lines = set(find_nearest_station(request.origin)[3])
        d_station_lines = set(find_nearest_station(request.destination)[3])
        needs_transfer = not bool(o_station_lines & d_station_lines)
        transfer_time = MRT_TRANSFER_PENALTY_S if needs_transfer else 0

        # Walk from destination station (via OSRM foot)
        walk_from = await _osrm_query(ds, request.destination, "foot", alternatives=1)
        walk_from_path = walk_from[0].path if walk_from else [ds, request.destination]
        walk_from_dist = walk_from[0].distance_m if walk_from else dwd
        walk_from_dur = walk_from_dist / MRT_WALK_SPEED_MPS

        total_duration = walk_to_dur + MRT_WAIT_TIME_S + ride_time + dwell_time + transfer_time + walk_from_dur
        total_distance = walk_to_dist + rail_dist + walk_from_dist

        # Combine path: walk → rail → walk
        full_path = walk_to_path + rail_path[1:] + walk_from_path[1:]

        segments = [
            RouteSegment(
                start=request.origin, end=os,
                distance_m=walk_to_dist, duration_s=walk_to_dur,
                instruction=f"Walk to {on} MRT ({walk_to_dist:.0f}m)",
                step_metadata={"type": "walk"}
            ),
            RouteSegment(
                start=os, end=os,
                distance_m=0, duration_s=MRT_WAIT_TIME_S,
                instruction="Wait for train (~2 min)",
                step_metadata={"type": "wait", "wait_minutes": 2}
            ),
            RouteSegment(
                start=os, end=ds,
                distance_m=rail_dist, duration_s=ride_time + dwell_time,
                instruction=f"Ride MRT ({num_stations} stations)",
                step_metadata={"type": "ride", "stations": num_stations, "from": on, "to": dn}
            ),
        ]

        if needs_transfer:
            segments.append(RouteSegment(
                start=ds, end=ds,
                distance_m=0, duration_s=transfer_time,
                instruction="Transfer between lines (~4 min)",
                step_metadata={"type": "transfer"}
            ))

        segments.append(RouteSegment(
            start=ds, end=request.destination,
            distance_m=walk_from_dist, duration_s=walk_from_dur,
            instruction=f"Walk to destination ({walk_from_dist:.0f}m)",
            step_metadata={"type": "walk"}
        ))

        mrt_route = RouteOption(
            id=f"mrt-{idx}",
            name="MRT Itinerary",
            color="#000000",
            role="candidate",
            distance_m=total_distance,
            duration_s=total_duration,
            total_sensory_score=0.0,
            segments=segments,
            path=full_path,
        )
        mrt_routes.append(mrt_route)

    return mrt_routes


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Utility functions
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _haversine(c1: Coordinate, c2: Coordinate) -> float:
    """Haversine distance in meters."""
    R = 6371000
    lat1, lat2 = math.radians(c1.lat), math.radians(c2.lat)
    dlat = math.radians(c2.lat - c1.lat)
    dlng = math.radians(c2.lng - c1.lng)
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _apply_mode_penalties(distance_m: float, osrm_duration_s: float, mode: RouteMode) -> float:
    """
    Adjust OSRM duration with mode-specific real-world penalties.
    OSRM tends to underestimate walking time and overestimate cycling.
    """
    if mode == RouteMode.walking:
        # OSRM foot profile is often optimistic — add crossing and intersection penalties
        crossing_penalties = (distance_m / 1000) * WALKING_PENALTY_PER_KM
        # Ensure minimum walking speed of ~4.5 km/h
        min_walking_time = distance_m / WALKING_SPEED_MPS
        return max(osrm_duration_s + crossing_penalties, min_walking_time)

    elif mode == RouteMode.cycling:
        # Ensure realistic cycling speed ~15 km/h average
        min_cycling_time = distance_m / CYCLING_SPEED_MPS
        return max(osrm_duration_s, min_cycling_time)

    elif mode == RouteMode.driving:
        # Add signal/intersection delays: ~10s per km
        signal_delays = (distance_m / 1000) * 10.0
        return osrm_duration_s + signal_delays

    return osrm_duration_s
