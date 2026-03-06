"""
Singapore MRT station data for NeuroNav transit routing.
Contains coordinates and line assignments for key MRT stations.
Used for: finding nearest station, computing rail travel, generating valid geometry.
"""
from models import Coordinate

# Each station: (name, lat, lng, lines[])
# Lines: NSL=North-South, EWL=East-West, NEL=North-East, CCL=Circle, DTL=Downtown, TEL=Thomson-East Coast
MRT_STATIONS = [
    # North-South Line (NSL)
    ("Jurong East", 1.3329, 103.7422, ["NSL", "EWL"]),
    ("Bukit Batok", 1.3490, 103.7496, ["NSL"]),
    ("Bukit Gombak", 1.3586, 103.7519, ["NSL"]),
    ("Choa Chu Kang", 1.3853, 103.7445, ["NSL"]),
    ("Yishun", 1.4293, 103.8350, ["NSL"]),
    ("Ang Mo Kio", 1.3700, 103.8496, ["NSL"]),
    ("Bishan", 1.3512, 103.8483, ["NSL", "CCL"]),
    ("Toa Payoh", 1.3326, 103.8471, ["NSL"]),
    ("Novena", 1.3204, 103.8439, ["NSL"]),
    ("Newton", 1.3138, 103.8379, ["NSL", "DTL"]),
    ("Orchard", 1.3042, 103.8322, ["NSL", "TEL"]),
    ("Somerset", 1.3006, 103.8389, ["NSL"]),
    ("Dhoby Ghaut", 1.2993, 103.8455, ["NSL", "NEL", "CCL"]),
    ("City Hall", 1.2930, 103.8520, ["NSL", "EWL"]),
    ("Raffles Place", 1.2837, 103.8516, ["NSL", "EWL"]),
    ("Marina Bay", 1.2764, 103.8546, ["NSL", "CCL", "TEL"]),
    ("Marina South Pier", 1.2714, 103.8632, ["NSL"]),

    # East-West Line (EWL) — unique stations only
    ("Pasir Ris", 1.3731, 103.9493, ["EWL"]),
    ("Tampines", 1.3534, 103.9452, ["EWL", "DTL"]),
    ("Simei", 1.3432, 103.9531, ["EWL"]),
    ("Tanah Merah", 1.3272, 103.9464, ["EWL"]),
    ("Bedok", 1.3240, 103.9300, ["EWL"]),
    ("Kembangan", 1.3209, 103.9128, ["EWL"]),
    ("Eunos", 1.3199, 103.9030, ["EWL"]),
    ("Paya Lebar", 1.3177, 103.8927, ["EWL", "CCL"]),
    ("Aljunied", 1.3164, 103.8826, ["EWL"]),
    ("Kallang", 1.3114, 103.8716, ["EWL"]),
    ("Lavender", 1.3071, 103.8630, ["EWL"]),
    ("Bugis", 1.3009, 103.8559, ["EWL", "DTL"]),
    ("Tanjong Pagar", 1.2764, 103.8467, ["EWL"]),
    ("Outram Park", 1.2803, 103.8394, ["EWL", "NEL", "TEL"]),
    ("Tiong Bahru", 1.2862, 103.8271, ["EWL"]),
    ("Redhill", 1.2892, 103.8166, ["EWL"]),
    ("Queenstown", 1.2944, 103.8060, ["EWL"]),
    ("Commonwealth", 1.3023, 103.7983, ["EWL"]),
    ("Buona Vista", 1.3073, 103.7904, ["EWL", "CCL"]),
    ("Dover", 1.3114, 103.7786, ["EWL"]),
    ("Clementi", 1.3152, 103.7652, ["EWL"]),
    ("Chinese Garden", 1.3425, 103.7326, ["EWL"]),
    ("Lakeside", 1.3443, 103.7210, ["EWL"]),
    ("Boon Lay", 1.3387, 103.7058, ["EWL"]),
    ("Pioneer", 1.3376, 103.6973, ["EWL"]),
    ("Joo Koon", 1.3278, 103.6782, ["EWL"]),
    ("Changi Airport", 1.3574, 103.9884, ["EWL"]),
    ("Expo", 1.3351, 103.9614, ["EWL", "DTL"]),

    # North-East Line (NEL) — unique stations only
    ("HarbourFront", 1.2654, 103.8215, ["NEL", "CCL"]),
    ("Chinatown", 1.2844, 103.8446, ["NEL", "DTL"]),
    ("Clarke Quay", 1.2886, 103.8465, ["NEL"]),
    ("Little India", 1.3064, 103.8493, ["NEL", "DTL"]),
    ("Farrer Park", 1.3124, 103.8547, ["NEL"]),
    ("Boon Keng", 1.3195, 103.8617, ["NEL"]),
    ("Potong Pasir", 1.3313, 103.8689, ["NEL"]),
    ("Woodleigh", 1.3389, 103.8706, ["NEL"]),
    ("Serangoon", 1.3498, 103.8734, ["NEL", "CCL"]),
    ("Hougang", 1.3713, 103.8923, ["NEL"]),
    ("Buangkok", 1.3829, 103.8929, ["NEL"]),
    ("Sengkang", 1.3916, 103.8953, ["NEL"]),
    ("Punggol", 1.4053, 103.9023, ["NEL"]),

    # Circle Line (CCL) — unique stations only
    ("Bayfront", 1.2815, 103.8594, ["CCL", "DTL"]),
    ("Promenade", 1.2934, 103.8611, ["CCL", "DTL"]),
    ("Nicoll Highway", 1.2997, 103.8637, ["CCL"]),
    ("Stadium", 1.3028, 103.8753, ["CCL"]),
    ("Mountbatten", 1.3065, 103.8825, ["CCL"]),
    ("Dakota", 1.3083, 103.8886, ["CCL"]),
    ("MacPherson", 1.3267, 103.8900, ["CCL", "DTL"]),
    ("Tai Seng", 1.3358, 103.8879, ["CCL"]),
    ("Bartley", 1.3423, 103.8796, ["CCL"]),
    ("Lorong Chuan", 1.3515, 103.8643, ["CCL"]),
    ("Marymount", 1.3491, 103.8394, ["CCL"]),
    ("Caldecott", 1.3374, 103.8395, ["CCL", "TEL"]),
    ("Botanic Gardens", 1.3225, 103.8153, ["CCL", "DTL"]),
    ("Farrer Road", 1.3174, 103.8078, ["CCL"]),
    ("Holland Village", 1.3117, 103.7959, ["CCL"]),
    ("one-north", 1.2997, 103.7876, ["CCL"]),
    ("Kent Ridge", 1.2934, 103.7847, ["CCL"]),
    ("Haw Par Villa", 1.2826, 103.7820, ["CCL"]),
    ("Pasir Panjang", 1.2762, 103.7908, ["CCL"]),
    ("Labrador Park", 1.2723, 103.8029, ["CCL"]),
    ("Telok Blangah", 1.2706, 103.8098, ["CCL"]),

    # Downtown Line (DTL) — unique stations only
    ("Bukit Panjang", 1.3784, 103.7620, ["DTL"]),
    ("Cashew", 1.3690, 103.7643, ["DTL"]),
    ("Hillview", 1.3625, 103.7677, ["DTL"]),
    ("Beauty World", 1.3413, 103.7760, ["DTL"]),
    ("King Albert Park", 1.3353, 103.7835, ["DTL"]),
    ("Sixth Avenue", 1.3305, 103.7972, ["DTL"]),
    ("Tan Kah Kee", 1.3259, 103.8073, ["DTL"]),
    ("Stevens", 1.3200, 103.8266, ["DTL", "TEL"]),
    ("Rochor", 1.3035, 103.8526, ["DTL"]),
    ("Downtown", 1.2793, 103.8527, ["DTL"]),
    ("Telok Ayer", 1.2822, 103.8487, ["DTL"]),
    ("Fort Canning", 1.2923, 103.8445, ["DTL"]),
    ("Bencoolen", 1.2987, 103.8502, ["DTL"]),
    ("Jalan Besar", 1.3054, 103.8553, ["DTL"]),
    ("Bendemeer", 1.3138, 103.8628, ["DTL"]),
    ("Geylang Bahru", 1.3213, 103.8716, ["DTL"]),
    ("Mattar", 1.3268, 103.8832, ["DTL"]),
    ("Ubi", 1.3299, 103.8992, ["DTL"]),
    ("Kaki Bukit", 1.3350, 103.9085, ["DTL"]),
    ("Bedok North", 1.3346, 103.9164, ["DTL"]),
    ("Bedok Reservoir", 1.3368, 103.9320, ["DTL"]),
    ("Tampines West", 1.3457, 103.9385, ["DTL"]),
    ("Tampines East", 1.3563, 103.9545, ["DTL"]),
    ("Upper Changi", 1.3417, 103.9614, ["DTL"]),
]


def find_nearest_station(coord: Coordinate, line_filter: str = None) -> tuple:
    """
    Find the nearest MRT station to a coordinate.
    Returns (name, Coordinate, distance_m, lines[]).
    """
    import math
    best = None
    best_dist = float('inf')
    for name, lat, lng, lines in MRT_STATIONS:
        if line_filter and line_filter not in lines:
            continue
        # Quick Euclidean approximation for ranking
        d = math.sqrt((coord.lat - lat) ** 2 + (coord.lng - lng) ** 2)
        if d < best_dist:
            best_dist = d
            best = (name, Coordinate(lat=lat, lng=lng), lines)

    if best is None:
        return ("Unknown", coord, 0.0, [])

    # Accurate distance
    R = 6371000
    lat1, lat2 = math.radians(coord.lat), math.radians(best[1].lat)
    dlat = math.radians(best[1].lat - coord.lat)
    dlng = math.radians(best[1].lng - coord.lng)
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng / 2) ** 2
    dist_m = R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return (best[0], best[1], dist_m, best[2])


def find_stations_on_line(line: str) -> list:
    """Return all stations on a given line, in order."""
    return [(name, Coordinate(lat=lat, lng=lng), lines)
            for name, lat, lng, lines in MRT_STATIONS
            if line in lines]


def get_station_path(origin_station: Coordinate, dest_station: Coordinate) -> list:
    """
    Generate a path between two MRT stations by finding the best line connecting them.
    Returns a list of Coordinate representing the rail route geometry.
    """
    # Find which lines serve origin and destination
    origin_lines = set()
    dest_lines = set()
    origin_name = ""
    dest_name = ""

    for name, lat, lng, lines in MRT_STATIONS:
        if abs(lat - origin_station.lat) < 0.001 and abs(lng - origin_station.lng) < 0.001:
            origin_lines.update(lines)
            origin_name = name
        if abs(lat - dest_station.lat) < 0.001 and abs(lng - dest_station.lng) < 0.001:
            dest_lines.update(lines)
            dest_name = name

    # Try direct line first (no transfer)
    common_lines = origin_lines & dest_lines
    if common_lines:
        line = list(common_lines)[0]
        return _stations_between(line, origin_station, dest_station)

    # Find transfer: check all lines from origin, see if any station connects to dest line
    best_path = None
    best_len = float('inf')

    for o_line in origin_lines:
        o_stations = find_stations_on_line(o_line)
        for d_line in dest_lines:
            # Find transfer stations (stations serving both lines)
            for s_name, s_coord, s_lines in o_stations:
                if d_line in s_lines:
                    # Transfer at this station
                    leg1 = _stations_between(o_line, origin_station, s_coord)
                    leg2 = _stations_between(d_line, s_coord, dest_station)
                    full_path = leg1 + leg2[1:]  # Avoid duplicate transfer station
                    if len(full_path) < best_len:
                        best_len = len(full_path)
                        best_path = full_path

    if best_path:
        return best_path

    # Fallback: straight line between stations (shouldn't happen with good data)
    return [origin_station, dest_station]


def _stations_between(line: str, start: Coordinate, end: Coordinate) -> list:
    """Get ordered station coordinates between start and end on a given line."""
    stations = find_stations_on_line(line)
    coords = [s[1] for s in stations]

    # Find indices closest to start and end
    def closest_idx(target):
        return min(range(len(coords)),
                   key=lambda i: (coords[i].lat - target.lat) ** 2 + (coords[i].lng - target.lng) ** 2)

    start_idx = closest_idx(start)
    end_idx = closest_idx(end)

    if start_idx <= end_idx:
        return coords[start_idx:end_idx + 1]
    else:
        return list(reversed(coords[end_idx:start_idx + 1]))


def count_stations_between(origin_coord: Coordinate, dest_coord: Coordinate) -> int:
    """Count the number of stations on the rail path between two points."""
    path = get_station_path(origin_coord, dest_coord)
    return max(0, len(path) - 1)
