from backend.state.bajastate import BajaState
from math import radians, sin, cos, sqrt, atan2

# Same coordinates as map node (keep consistent)
LOCATIONS = {
    "Tijuana": [-117.0382, 32.5149],
    "Rosarito": [-117.0550, 32.3661],
    "Puerto Nuevo": [-116.8750, 32.2470],
    "Ensenada": [-116.6000, 31.8667],
    "Valle de Guadalupe": [-116.5800, 32.1000],
    "San Quintin": [-115.9800, 30.5500],
    "San Felipe": [-114.8500, 31.0250],
}

MAX_DISTANCE_KM = 150  # 🔥 constraint


# 🌍 Haversine distance (no API needed)
def haversine(coord1, coord2):
    lon1, lat1 = coord1
    lon2, lat2 = coord2

    R = 6371  # Earth radius (km)

    dlon = radians(lon2 - lon1)
    dlat = radians(lat2 - lat1)

    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c


def extract_locations(travel: dict):
    ordered = []

    for day in ["day_1", "day_2", "day_3"]:
        for item in travel.get(day, []):
            loc = item.get("location")
            if loc and loc not in ordered:
                ordered.append(loc)

    return ordered


def travel_validator_node(state: BajaState):

    travel = state.get("travel", {})

    # 🔴 1. Structure validation
    if not travel or not isinstance(travel, dict):
        return {"valid_travel": False}

    locations = extract_locations(travel)

    # 🔴 2. Minimum locations
    if len(locations) < 2:
        return {"valid_travel": False}

    # 🔴 3. Unknown locations
    for loc in locations:
        if loc not in LOCATIONS:
            return {"valid_travel": False}

    # 🔴 4. Distance validation
    for i in range(len(locations) - 1):
        start = LOCATIONS[locations[i]]
        end = LOCATIONS[locations[i + 1]]

        distance = haversine(start, end)

        if distance > MAX_DISTANCE_KM:
            return {
                "valid_travel": False,
                "invalid_segment": {
                    "from": locations[i],
                    "to": locations[i + 1],
                    "distance_km": round(distance, 2)
                }
            }

    # ✅ Passed all checks
    return {
        "valid_travel": True
    }