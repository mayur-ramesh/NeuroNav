"""Test all 5 transport modes and verify realistic timing."""
import requests
import json

BASE = "http://localhost:8000"
HEADERS = {"Content-Type": "application/json", "X-Diagnostics": "true"}

# Orchard Road to Marina Bay (~3km)
ORIGIN = {"lat": 1.3048, "lng": 103.8318}
DEST = {"lat": 1.2834, "lng": 103.8607}
PROFILE = {
    "noise_sensitivity": 0.5,
    "crowd_sensitivity": 0.5,
    "predictability_preference": 0.5,
    "nature_preference": 0.5,
    "shelter_preference": 0.5
}

MODES = ["walking", "driving", "cycling", "bus", "mrt"]

print("=" * 70)
print("NeuroNav Routing Test — Orchard Road → Marina Bay")
print("=" * 70)

for mode in MODES:
    data = {
        "origin": ORIGIN,
        "destination": DEST,
        "mode": mode,
        "profile": PROFILE
    }
    try:
        r = requests.post(f"{BASE}/api/route", json=data, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            print(f"\n[{mode.upper()}] FAILED — Status {r.status_code}: {r.text[:200]}")
            continue
            
        routes = r.json().get("routes", [])
        print(f"\n{'─' * 50}")
        print(f"  MODE: {mode.upper()} — {len(routes)} routes returned")
        print(f"{'─' * 50}")
        
        for rt in routes:
            dist_km = rt["distance_m"] / 1000
            dur_min = rt["duration_s"] / 60
            speed_kmh = (rt["distance_m"] / max(1, rt["duration_s"])) * 3.6
            path_len = len(rt.get("path", []))
            segments = len(rt.get("segments", []))
            
            print(f"  {rt['role']:12s} | {dur_min:5.1f} min | {dist_km:5.2f} km | {speed_kmh:5.1f} km/h | {path_len} pts | {segments} segs")
            
            debug = rt.get("debug", {})
            if debug:
                for k, v in debug.items():
                    print(f"               | debug.{k}: {v}")
                    
    except Exception as e:
        print(f"\n[{mode.upper()}] ERROR: {e}")

print(f"\n{'=' * 70}")
print("Test complete.")
