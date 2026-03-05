from models import Coordinate, RouteOption

# Approximate bounds for mainland Singapore
SG_BBOX = {
    "min_lat": 1.15,
    "max_lat": 1.48,
    "min_lng": 103.58,
    "max_lng": 104.05
}

def is_in_singapore(coord: Coordinate) -> bool:
    """Check if a given coordinate is strictly within Singapore bounds."""
    return (SG_BBOX["min_lat"] <= coord.lat <= SG_BBOX["max_lat"] and
            SG_BBOX["min_lng"] <= coord.lng <= SG_BBOX["max_lng"])

def calculate_overlap_ratio(route1: RouteOption, route2: RouteOption) -> float:
    """
    Calculate the overlap ratio between two routes.
    It returns the proportion of route2's coordinates that are shared with route1.
    We use coordinate sets rounded to 4 decimal places (~11m resolution) to quickly identify overlaps.
    """
    if not route1.path or not route2.path:
        return 0.0

    set1 = set((round(p.lat, 4), round(p.lng, 4)) for p in route1.path)
    set2 = set((round(p.lat, 4), round(p.lng, 4)) for p in route2.path)
    
    if not set2:
        return 0.0
        
    intersection = set1.intersection(set2)
    return len(intersection) / len(set2)
