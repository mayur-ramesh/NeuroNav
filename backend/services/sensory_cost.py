from models import RouteOption, SensoryProfile
from services.external_data import get_lta_traffic_data, get_onemap_crowd_data
import asyncio

async def calculate_sensory_cost(route: RouteOption, profile: SensoryProfile) -> RouteOption:
    \"\"\"
    Iterates through a route's segments, fetches live environmental data,
    and applies the user's sensory profile weights to calculate a total sensory cost.
    \"\"\"
    total_sensory_score = 0.0
    
    # Optional: We could sample points along the path instead of just the segment start/end
    # For Hackathon speed, we'll evaluate the start coordinate of each segment
    
    for segment in route.segments:
        # 1. Fetch live data (concurrently for speed, or sequentially)
        # In a real app we'd batch these requests
        noise_level = await get_lta_traffic_data(segment.start.lat, segment.start.lng)
        crowd_level = await get_onemap_crowd_data(segment.start.lat, segment.start.lng)
        
        # 2. Apply Custom Weights (Sensory Cost Function)
        # Cost = (Noise_Level * Noise_Sensitivity) + (Crowd_Level * Crowd_Sensitivity)
        # We can also factor in segment distance/duration so longer segments contribute more to the total cost.
        
        segment_cost = (noise_level * profile.noise_sensitivity) + (crowd_level * profile.crowd_sensitivity)
        
        # Normalize by segment distance (meters) so long noisy streets are penalized more than short ones
        # Adding a small base cost for distance itself
        distance_weight = segment.distance / 1000.0 # km
        
        weighted_segment_cost = segment_cost * distance_weight
        
        # 3. Update segment and running total
        segment.sensory_score = weighted_segment_cost
        total_sensory_score += weighted_segment_cost

    route.total_sensory_score = total_sensory_score
    return route

async def rank_routes_by_sensory_cost(routes: list[RouteOption], profile: SensoryProfile) -> list[RouteOption]:
    \"\"\"
    Takes a list of raw route options, calculates their sensory cost,
    and returns them sorted from lowest cost (calmest) to highest.
    \"\"\"
    # Calculate costs concurrently
    tasks = [calculate_sensory_cost(route, profile) for route in routes]
    scored_routes = await asyncio.gather(*tasks)
    
    # Sort by total sensory score (ascending)
    # If scores are identical, fallback to distance
    sorted_routes = sorted(scored_routes, key=lambda r: (r.total_sensory_score, r.total_distance))
    
    return sorted_routes
