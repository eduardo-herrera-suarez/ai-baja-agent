import os
import requests

ORS_API_KEY = os.getenv("ORS_API_KEY")
ORS_URL = "https://api.openrouteservice.org/v2/directions/driving-car"

HEADERS = {
    "Authorization": ORS_API_KEY,
    "Content-Type": "application/json"
}

def get_route(start_coords, end_coords):

    body = {
        "coordinates": [start_coords, end_coords]
    }

    response = requests.post(ORS_URL, json=body, headers=HEADERS)

    if response.status_code != 200:
        return {"error": f"HTTP {response.status_code}: {response.text}"}

    data = response.json()

    # ✅ FIXED
    if "routes" not in data:
        return {
            "error": f"Invalid ORS response: {data}"
        }

    try:
        summary = data["routes"][0]["summary"]

        return {
            "distance_km": round(summary["distance"] / 1000, 2),
            "duration_min": round(summary["duration"] / 60, 1)
        }

    except Exception as e:
        return {"error": str(e)}