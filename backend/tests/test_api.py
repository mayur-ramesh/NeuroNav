import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def get_base_payload(mode: str):
    return {
        "origin": {"lat": 1.3048, "lng": 103.8318},
        "destination": {"lat": 1.2834, "lng": 103.8607},
        "mode": mode,
        "profile": {
            "noise_sensitivity": 0.5,
            "crowd_sensitivity": 0.5,
            "predictability_preference": 0.5,
            "nature_preference": 0.5,
            "shelter_preference": 0.5
        }
    }

def test_walking_route():
    response = client.post("/api/route", json=get_base_payload("walking"))
    assert response.status_code == 200
    data = response.json()
    assert len(data["routes"]) == 2
    assert data["routes"][0]["role"] == "preferred"
    assert data["routes"][1]["role"] == "longest"

def test_driving_route():
    response = client.post("/api/route", json=get_base_payload("driving"))
    assert response.status_code == 200
    data = response.json()
    assert len(data["routes"]) == 2

def test_cycling_route():
    response = client.post("/api/route", json=get_base_payload("cycling"))
    assert response.status_code == 200
    data = response.json()
    assert len(data["routes"]) == 2

def test_bus_route():
    response = client.post("/api/route", json=get_base_payload("bus"))
    assert response.status_code == 200
    data = response.json()
    assert len(data["routes"]) == 2

def test_mrt_route():
    response = client.post("/api/route", json=get_base_payload("mrt"))
    assert response.status_code == 200
    data = response.json()
    assert len(data["routes"]) == 2

def test_out_of_bounds_rejection():
    payload = get_base_payload("walking")
    payload["origin"] = {"lat": 1.49, "lng": 103.76} # Johor Bahru
    response = client.post("/api/route", json=payload)
    assert response.status_code == 400

def test_sanity_check_walking_vs_driving():
    walk_resp = client.post("/api/route", json=get_base_payload("walking"))
    drive_resp = client.post("/api/route", json=get_base_payload("driving"))
    
    assert walk_resp.status_code == 200
    assert drive_resp.status_code == 200
    
    walk_data = walk_resp.json()
    drive_data = drive_resp.json()
    
    walk_dur = walk_data["routes"][0]["duration_s"]
    drive_dur = drive_data["routes"][0]["duration_s"]
    
    # Walking should inherently take longer than driving
    assert walk_dur > drive_dur
