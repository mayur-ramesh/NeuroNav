"""
Geometry utilities for NeuroNav.
"""
import math
from models import Coordinate, RouteOption

# Approximate bounds for Singapore
SG_BBOX = {
    "min_lat": 1.15,
    "max_lat": 1.48,
    "min_lng": 103.58,
    "max_lng": 104.05
}


def is_in_singapore(coord: Coordinate) -> bool:
    """Check if a given coordinate is within Singapore bounds."""
    return (SG_BBOX["min_lat"] <= coord.lat <= SG_BBOX["max_lat"] and
            SG_BBOX["min_lng"] <= coord.lng <= SG_BBOX["max_lng"])


def haversine_distance(c1: Coordinate, c2: Coordinate) -> float:
    """Haversine distance in meters between two coordinates."""
    R = 6371000
    lat1, lat2 = math.radians(c1.lat), math.radians(c2.lat)
    dlat = math.radians(c2.lat - c1.lat)
    dlng = math.radians(c2.lng - c1.lng)
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def max_segment_gap(path: list) -> float:
    """
    Find the maximum gap (in degrees) between consecutive path points.
    Large gaps indicate potential water or restricted area crossings.
    """
    max_gap = 0.0
    for i in range(len(path) - 1):
        dlat = abs(path[i + 1].lat - path[i].lat)
        dlng = abs(path[i + 1].lng - path[i].lng)
        gap = math.sqrt(dlat ** 2 + dlng ** 2)
        max_gap = max(max_gap, gap)
    return max_gap


def calculate_overlap_ratio(route1: RouteOption, route2: RouteOption) -> float:
    """
    Calculate corridor overlap between two routes using buffered coordinate matching.
    Returns the proportion of route2's path that overlaps with route1.
    Uses 4-decimal rounding (~11m resolution) for proximity matching.
    """
    if not route1.path or not route2.path:
        return 0.0

    # Build a set of "cells" for route1 at ~11m resolution
    set1 = set()
    for p in route1.path:
        set1.add((round(p.lat, 4), round(p.lng, 4)))
        # Also add neighboring cells for a ~30m buffer
        for dlat in [-0.0001, 0, 0.0001]:
            for dlng in [-0.0001, 0, 0.0001]:
                set1.add((round(p.lat + dlat, 4), round(p.lng + dlng, 4)))

    # Count how many of route2's points fall within route1's buffer
    matches = 0
    total = len(route2.path)
    for p in route2.path:
        cell = (round(p.lat, 4), round(p.lng, 4))
        if cell in set1:
            matches += 1

    return matches / total if total > 0 else 0.0
