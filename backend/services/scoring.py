import asyncio
from models import RouteOption, SensoryProfile
from services.external_data import get_lta_traffic_data, get_onemap_crowd_data, get_green_space_data

async def score_route(route: RouteOption, profile: SensoryProfile) -> RouteOption:
    """
    Calculates a sensory cost for the route based on environmental data
    and the user's specific sensitivities. Mutates the route in-place
    to add segment scores and total score.
    """
    total_score = 0.0
    
    for segment in route.segments:
        # Use segment midpoint or start for data querying
        lat = (segment.start.lat + segment.end.lat) / 2
        lng = (segment.start.lng + segment.end.lng) / 2
        
        # Fetch real-time (or mock) external data
        # To speed this up, we would ideally batch these queries or cache them
        noise_level = await get_lta_traffic_data(lat, lng)
        crowd_level = await get_onemap_crowd_data(lat, lng)
        greenery_level = await get_green_space_data(lat, lng)
        
        # Calculate penalty based on user's sensitivity profile
        # Both levels are 0-1, sensitivities are 0-1.
        noise_penalty = noise_level * profile.noise_sensitivity
        crowd_penalty = crowd_level * profile.crowd_sensitivity
        
        # Predictability Metric:
        # A route that requires constant turning or complex maneuvers can be stressful.
        # "Walk" is generally simple. "Turn right", "Slight left" etc add complexity.
        is_complex_turn = segment.instruction.lower() not in ["walk", "depart", "arrive", "continue"]
        maneuver_penalty = 1.0 if is_complex_turn else 0.0 
        predictability_penalty = maneuver_penalty * profile.predictability_preference
        
        # Nature Metric:
        # Reward routes that go through parks/nature (decreases the score)
        nature_reward = greenery_level * profile.nature_preference
        
        # We weigh the standard environmental penalties by the distance (in 100s of meters).
        # A 1km walk through a high-penalty zone is worse than 100m.
        distance_weight = segment.distance / 100.0 if segment.distance > 0 else 0.1
        
        # The maneuver penalty is a fixed point cost, independent of distance
        # The nature reward is distance dependent (more time in a park is better)
        
        # Combine into a single segment score.
        # Ensure the score never goes negative even if the nature reward is high
        environmental_cost = (noise_penalty + crowd_penalty - nature_reward) * distance_weight
        segment_score = max(0.0, environmental_cost) + predictability_penalty
        
        # Update the segment with new fields and score
        segment.maneuver_complexity = predictability_penalty
        segment.nature_bonus = nature_reward
        segment.sensory_score = segment_score
        total_score += segment_score
        
    # Apply total score to the route option
    route.total_sensory_score = total_score
    return route
