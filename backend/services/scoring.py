from models import RouteOption, SensoryProfile, RouteMode, Coordinate
from services.signals import get_signal_provider
from utils.config import settings

async def score_route(route: RouteOption, profile: SensoryProfile, use_live_signals: bool = False, mode: RouteMode = RouteMode.walking) -> RouteOption:
    """
    Calculates a sensory cost for the route based on user profile and environmental signals.
    Formula: cost = timeWeight*time + envWeight*(noise*n_sens + crowd*c_sens + pred*p_pref - nature*n_pref - shelter*s_pref)
    """
    signal_provider = get_signal_provider(use_live_signals)
    total_score = 0.0
    
    for segment in route.segments:
        # Midpoint for querying context
        mid_lat = (segment.start.lat + segment.end.lat) / 2.0
        mid_lng = (segment.start.lng + segment.end.lng) / 2.0
        mid_coord = Coordinate(lat=mid_lat, lng=mid_lng)
        
        noise_level = await signal_provider.get_noise(mid_coord)
        crowd_level = await signal_provider.get_crowd(mid_coord)
        nature_level = await signal_provider.get_nature(mid_coord)
        shelter_level = await signal_provider.get_shelter(mid_coord)
        
        noise_cost = noise_level * profile.noise_sensitivity
        crowd_cost = crowd_level * profile.crowd_sensitivity
        nature_reward = nature_level * profile.nature_preference
        shelter_reward = shelter_level * profile.shelter_preference
        
        # Predictability penalty (more complex instructions = higher penalty)
        instruction = segment.instruction.lower()
        is_complex = instruction not in ["walk", "depart", "arrive", "continue", "straight", "proceed"]
        maneuver_complexity = 1.0 if is_complex else 0.0
        pred_cost = maneuver_complexity * profile.predictability_preference
        
        # Core environmental score
        env_score = noise_cost + crowd_cost + pred_cost - (nature_reward + shelter_reward)
        
        # Normalize weighting via duration limits (assuming constant proxy for distance/time ratio)
        weight_s = max(1.0, segment.duration_s)
        time_cost = settings.TIME_WEIGHT * weight_s
        
        # Distribute the environmental scale factor per minute of exposure
        segment_score = time_cost + env_score * (weight_s / 60.0)
        segment_score = max(0.0, segment_score) # Lower bound at zero
        
        segment.maneuver_complexity = maneuver_complexity
        segment.nature_bonus = nature_reward
        segment.sensory_score = segment_score
        
        total_score += segment_score
        
    route.total_sensory_score = total_score
    return route
