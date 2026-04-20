from backend.state.bajastate import BajaState

def route_intent(state):
    intent = state["intent"]

    if intent == "trip_planner":
        return "trip_planner"

    return intent
   
