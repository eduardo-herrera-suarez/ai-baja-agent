from backend.state.bajastate import BajaState

def confidence_node(state: BajaState):

    travel = state.get("travel")
    food = state.get("food")
    budget = state.get("budget")
    route = state.get("enriched_plan", {}).get("route")

    score = 0.9

    # 🔎 STRUCTURE VALIDATION (most important)
    if not travel or travel == {}:
        score -= 0.4

    if not food or food == {}:
        score -= 0.3

    if not budget:
        score -= 0.2

    # 🔎 REAL-WORLD VALIDATION
    if not route:
        score -= 0.2
    elif route.get("distance_km", 0) == 0:
        score -= 0.1

    if not route or "error" in route:
        score -= 0.3

    # 🔎 OPTIONAL TEXT CHECK (secondary)
    combined_text = f"{travel} {food} {budget}".lower()

    if "day 1" not in combined_text:
        score -= 0.1

    score = max(0.0, min(score, 1.0))

    return {
        "confidence": score
    }