import requests
import json

data = {
    "origin": {"lat": 1.3048, "lng": 103.8318},
    "destination": {"lat": 1.2834, "lng": 103.8607},
    "mode": "walking",
    "profile": {
        "noise_sensitivity": 0.5,
        "crowd_sensitivity": 0.5,
        "predictability_preference": 0.5,
        "nature_preference": 0.5,
        "shelter_preference": 0.5
    }
}

r = requests.post("http://localhost:8000/api/route", json=data, headers={"X-Diagnostics": "true"})
print("Status:", r.status_code)
d = r.json()
routes = d.get("routes", [])
print("Route count:", len(routes))
for i, rt in enumerate(routes):
    path = rt.get("path", [])
    print(f"\nRoute {i}:")
    print(f"  name={rt.get('name')}")
    print(f"  role={rt.get('role')}")
    print(f"  color={rt.get('color')}")
    print(f"  path length={len(path)}")
    print(f"  distance_m={rt.get('distance_m')}")
    print(f"  duration_s={rt.get('duration_s')}")
    print(f"  score={rt.get('total_sensory_score')}")
    print(f"  debug={rt.get('debug')}")
    if path:
        print(f"  first point={path[0]}")
        print(f"  last point={path[-1]}")
        if len(path) > 2:
            print(f"  sample mid={path[len(path)//2]}")
