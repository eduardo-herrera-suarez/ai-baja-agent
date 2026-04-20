from backend.state.bajastate import BajaState
from backend.nodes.map_tool import get_route

LOCATIONS = {
    "Tijuana": [-117.0382, 32.5149],
    "Rosarito": [-117.0550, 32.3661],
    "Puerto Nuevo": [-116.8750, 32.2470],
    "Ensenada": [-116.6000, 31.8667],
    "Valle de Guadalupe": [-116.5800, 32.1000],
    "San Quintin": [-115.9800, 30.5500],
    "San Felipe": [-114.8500, 31.0250],
}

def classify_segment(distance_km):
    if distance_km < 50:
        return "short_drive"
    elif distance_km < 150:
        return "medium_drive"
    else:
        return "long_drive"

def humanize_duration(minutes):
    if minutes < 60:
        return f"{int(minutes)} min"
    hours = minutes // 60
    mins = int(minutes % 60)
    return f"{int(hours)}h {mins}m"

def humanize_distance(km):
    return f"{km} km"

def detect_trip_style(total_km):
    if total_km < 100:
        return "local_exploration"
    elif total_km < 300:
        return "road_trip"
    else:
        return "long_distance"

def map_enrichment_node(state: BajaState):

    travel = state.get("travel", {})

    if not travel:
        return state

    ordered_locations = []

    for day in ["day_1", "day_2", "day_3"]:
        for item in travel.get(day, []):
            loc = item.get("location")
            if loc and loc not in ordered_locations:
                ordered_locations.append(loc)

    if len(ordered_locations) < 2:
        return {
            "enriched_plan": {"route": None},
            "route_failed": True,
            "failed_segments": [],
        }

    total_distance = 0
    total_duration = 0
    segments = []

    route_failed = False
    failed_segments = []

    try:
        for i in range(len(ordered_locations) - 1):
            start = ordered_locations[i]
            end = ordered_locations[i + 1]

            start_coords = LOCATIONS.get(start)
            end_coords = LOCATIONS.get(end)

            if not start_coords or not end_coords:
                route_failed = True

                error_data = {
                    "from": start,
                    "to": end,
                    "error": "Missing coordinates"
                }

                failed_segments.append(error_data)
                segments.append(error_data)
                continue

            route = get_route(start_coords, end_coords)
            print("DEBUG ROUTE:", route)

            # HANDLE ERROR
            if route.get("error"):
                route_failed = True

                error_data = {
                    "from": start,
                    "to": end,
                    "error": route["error"]
                }

                failed_segments.append(error_data)
                segments.append(error_data)
                continue

            # SUCCESS PATH ONLY
            distance = route.get("distance_km")
            duration = route.get("duration_min")

            # Defensive check (still good)
            if distance is None or duration is None:
                route_failed = True

                error_data = {
                    "from": start,
                    "to": end,
                    "error": "Missing distance/duration"
                }

                failed_segments.append(error_data)
                segments.append(error_data)
                continue

            # AGGREGATION
            total_distance += distance
            total_duration += duration

            segments.append({
                "from": start,
                "to": end,
                "distance_km": distance,
                "duration_min": duration,
                "distance_human": humanize_distance(distance),
                "duration_human": humanize_duration(duration),
                "category": classify_segment(distance)
            })

        route_summary = {
            "summary": {
                "total_distance_km": round(total_distance, 2),
                "total_duration_min": round(total_duration, 1),
                "total_distance_human": humanize_distance(round(total_distance, 2)),
                "total_duration_human": humanize_duration(round(total_duration, 1)),
                "travel_style": detect_trip_style(total_distance)
            },
            "segments": segments
        }

    except Exception as e:
        route_failed = True
        route_summary = {
            "error": str(e)
        }

    return {
        "enriched_plan": {
            "route": route_summary
        },
        "route_failed": route_failed,
        "failed_segments": failed_segments
    }