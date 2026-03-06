"""
Route validation utilities for NeuroNav.
Every route candidate must pass validation before being sent to the frontend.
"""
import math
from typing import List, Tuple, Optional
from models import RouteOption, RouteMode, Coordinate


class ValidationResult:
    """Result of route validation with pass/fail and reason."""
    def __init__(self, valid: bool, reason: str = ""):
        self.valid = valid
        self.reason = reason

    def __bool__(self):
        return self.valid

    def __repr__(self):
        return f"ValidationResult(valid={self.valid}, reason='{self.reason}')"


# Singapore bounding box (tight — excludes water surrounding the island)
SG_LAND_BOUNDS = {
    "min_lat": 1.22,
    "max_lat": 1.47,
    "min_lng": 103.60,
    "max_lng": 104.05
}

# Maximum realistic speeds by mode (m/s)
MAX_SPEED = {
    RouteMode.walking: 2.5,    # ~9.0 km/h (very fast walk / light jog)
    RouteMode.driving: 35.0,   # ~126 km/h (expressway speed)
    RouteMode.cycling: 8.5,    # ~30.6 km/h (fast cyclist)
    RouteMode.bus: 20.0,       # ~72 km/h (express bus on expressway)
    RouteMode.mrt: 25.0,       # ~90 km/h (MRT top speed)
}

# Minimum realistic speeds by mode (m/s)
MIN_SPEED = {
    RouteMode.walking: 0.5,    # ~1.8 km/h (very slow crawl)
    RouteMode.driving: 1.0,    # ~3.6 km/h (stuck in jam)
    RouteMode.cycling: 1.0,    # ~3.6 km/h
    RouteMode.bus: 0.5,        # includes wait time
    RouteMode.mrt: 1.0,        # includes walk + wait
}

# Maximum gap between consecutive path points (degrees)
# For road modes: ~0.02 degrees ≈ 2.2 km — allows bridges and long road segments
# For MRT: ~0.04 degrees ≈ 4.4 km — stations can be far apart
MAX_POINT_GAP_DEG = 0.025
MAX_POINT_GAP_DEG_MRT = 0.05


def _haversine(c1: Coordinate, c2: Coordinate) -> float:
    """Haversine distance in meters between two coordinates."""
    R = 6371000  # Earth radius in meters
    lat1, lat2 = math.radians(c1.lat), math.radians(c2.lat)
    dlat = math.radians(c2.lat - c1.lat)
    dlng = math.radians(c2.lng - c1.lng)
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def validate_route(route: RouteOption, mode: RouteMode) -> ValidationResult:
    """
    Run all validation checks on a route candidate.
    Returns ValidationResult with detailed rejection reason if invalid.
    """
    # 1. Path must have enough points for a real route
    if not route.path or len(route.path) < 2:
        return ValidationResult(False, "Route has fewer than 2 path points")

    # 2. All points must be within Singapore bounds
    for i, pt in enumerate(route.path):
        if not (SG_LAND_BOUNDS["min_lat"] <= pt.lat <= SG_LAND_BOUNDS["max_lat"] and
                SG_LAND_BOUNDS["min_lng"] <= pt.lng <= SG_LAND_BOUNDS["max_lng"]):
            return ValidationResult(False, f"Path point {i} ({pt.lat:.4f}, {pt.lng:.4f}) is outside Singapore")

    # 3. Check for large gaps between consecutive points (water/restricted crossing)
    # Skip for transit modes — their paths combine walk + rail segments with natural gaps
    if mode not in [RouteMode.mrt, RouteMode.bus]:
        gap_result = _check_geometry_gaps(route.path, MAX_POINT_GAP_DEG)
        if not gap_result:
            return gap_result

    # 4. Distance must be positive and reasonable
    if route.distance_m <= 0:
        return ValidationResult(False, "Route distance is zero or negative")
    if route.distance_m > 100000:  # 100km — unreasonable for Singapore
        return ValidationResult(False, f"Route distance {route.distance_m:.0f}m exceeds Singapore maximum")

    # 5. Duration must be positive
    if route.duration_s <= 0:
        return ValidationResult(False, "Route duration is zero or negative")

    # 6. Speed sanity check
    speed_result = validate_speed(route.distance_m, route.duration_s, mode)
    if not speed_result:
        return speed_result

    # 7. Distance must be at least as far as crow-flies distance
    crow_flies = _haversine(route.path[0], route.path[-1])
    if route.distance_m < crow_flies * 0.8:  # Allow 20% tolerance for coordinate precision
        return ValidationResult(False, f"Route distance {route.distance_m:.0f}m is less than crow-flies {crow_flies:.0f}m")

    return ValidationResult(True, "All checks passed")


def validate_speed(distance_m: float, duration_s: float, mode: RouteMode) -> ValidationResult:
    """Check that the implied speed is physically possible for the given mode."""
    if duration_s <= 0:
        return ValidationResult(False, "Duration is zero — cannot calculate speed")

    speed_mps = distance_m / duration_s
    max_spd = MAX_SPEED.get(mode, 30.0)
    min_spd = MIN_SPEED.get(mode, 0.3)

    if speed_mps > max_spd:
        return ValidationResult(False,
            f"Speed {speed_mps * 3.6:.1f} km/h exceeds max {max_spd * 3.6:.1f} km/h for {mode.value}")

    if speed_mps < min_spd:
        return ValidationResult(False,
            f"Speed {speed_mps * 3.6:.1f} km/h below min {min_spd * 3.6:.1f} km/h for {mode.value}")

    return ValidationResult(True)


def _check_geometry_gaps(path: List[Coordinate], threshold: float = None) -> ValidationResult:
    """Detect unreasonably large gaps between consecutive points (indicates water/building crossing)."""
    if threshold is None:
        threshold = MAX_POINT_GAP_DEG
    for i in range(len(path) - 1):
        dlat = abs(path[i + 1].lat - path[i].lat)
        dlng = abs(path[i + 1].lng - path[i].lng)
        gap = math.sqrt(dlat ** 2 + dlng ** 2)
        if gap > threshold:
            return ValidationResult(False,
                f"Large gap ({gap:.4f}°) between points {i} and {i+1} — possible water/restricted crossing")
    return ValidationResult(True)
