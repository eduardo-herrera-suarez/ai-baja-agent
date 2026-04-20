from backend.state.bajastate import BajaState

def trip_planner_router_node(state: BajaState) -> BajaState:
    
    # Decide where to route next
    if state["intent"] == "trip_planner":
        state["route"] = "trip_pipeline"
    
    return state