import requests
import json

BASE = "http://localhost:8000"
ORIGIN = {"lat": 1.3048, "lng": 103.8318}
DEST = {"lat": 1.2834, "lng": 103.8607}
PROFILE = {"noise_sensitivity": 0.5, "crowd_sensitivity": 0.5, "predictability_preference": 0.5, "nature_preference": 0.5, "shelter_preference": 0.5}
results = []

for mode in ["walking", "driving", "cycling", "bus", "mrt"]:
    r = requests.post(f"{BASE}/api/route", json={"origin": ORIGIN, "destination": DEST, "mode": mode, "profile": PROFILE}, headers={"X-Diagnostics": "true"}, timeout=30)
    line = f"[{mode:8s}] status={r.status_code}"
    if r.status_code == 200:
        for rt in r.json()["routes"]:
            km = rt["distance_m"]/1000
            mins = rt["duration_s"]/60
            pts = len(rt.get("path", []))
            speed = (rt["distance_m"]/max(1,rt["duration_s"]))*3.6
            line += f"\n  {rt['role']:12s} {mins:6.1f}min {km:6.2f}km {speed:5.1f}km/h {pts:4d}pts"
    else:
        detail = r.json().get('detail', 'unknown')
        line += f"\n  ERROR: {detail}"
    results.append(line)

with open("test_results.txt", "w") as f:
    f.write("NeuroNav Route Test: Orchard Road -> Marina Bay\n\n")
    for r in results:
        f.write(r + "\n")
    f.write("\nDone.\n")

print("Results written to test_results.txt")
