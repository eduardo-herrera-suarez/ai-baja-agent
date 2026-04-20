from langgraph.graph import StateGraph, END
from backend.state.bajastate import BajaState
from backend.nodes.intent_classifier import classify_intent
from backend.nodes.travel_node import travel_node
from backend.nodes.food_node import food_node
from backend.nodes.history_node import history_node
from backend.nodes.budget_node import budget_node
from backend.nodes.trip_planner_router_node import trip_planner_router_node
from backend.nodes.final_compiler_node import final_compiler_node
from backend.routing.routes import route_intent
from backend.nodes.preference_extractor import preference_extractor
from backend.nodes.confidence_node import confidence_node
from backend.nodes.map_enrichment_node import map_enrichment_node
from backend.nodes.travel_validator_node import travel_validator_node

def is_trip_planner(state):
    return state["intent"] == "trip_planner"

def travel_validation_router(state):
    if not state.get("valid_travel"):
        retries = state.get("retry_count", 0)

        if retries >= 2:
            return "continue"  # fail-safe

        return "retry"

    return "continue"

def route_replanner(state):
    if state.get("route_failed"):
        retries = state.get("replan_count", 0)

        if retries >= 2:
            return "continue"

        return "replan"

    return "continue"

def build_graph():
    builder = StateGraph(BajaState)

    # Nodes
    builder.add_node("PreferenceExtractor", preference_extractor)
    builder.add_node("IntentClassifier", classify_intent)
    builder.add_node("TripPlannerRouterNode", trip_planner_router_node)

    builder.add_node("TravelNode", travel_node)
    builder.add_node("TravelValidatorNode", travel_validator_node)
    builder.add_node("MapEnrichmentNode", map_enrichment_node)
    builder.add_node("FoodNode", food_node)
    builder.add_node("BudgetNode", budget_node)

    builder.add_node("FinalCompilerNode", final_compiler_node)
    builder.add_node("ConfidenceNode", confidence_node)

    builder.set_entry_point("PreferenceExtractor")

    # Entry flow
    builder.add_edge("PreferenceExtractor", "IntentClassifier")

    # Intent routing
    builder.add_conditional_edges(
        "IntentClassifier",
        route_intent,
        {
            "travel": "TravelNode",
            "food": "FoodNode",
            "budget": "BudgetNode",
            "trip_planner": "TripPlannerRouterNode"
        }
    )

    # Trip planner pipeline (STRICTLY LINEAR)
    builder.add_edge("TripPlannerRouterNode", "TravelNode")
    builder.add_edge("TravelNode", "TravelValidatorNode")
    builder.add_edge("FoodNode", "BudgetNode")
    builder.add_edge("BudgetNode", "FinalCompilerNode")

    # Confidence → Conditional Critic (ONLY path after compiler)
    builder.add_edge("FinalCompilerNode", "ConfidenceNode")

    builder.add_conditional_edges(
        "MapEnrichmentNode",
        route_replanner,
        {
            "replan": "TravelNode",    
            "continue": "FoodNode"
        }
    )

    builder.add_conditional_edges(
        "TravelValidatorNode",
        travel_validation_router,
        {
            "retry": "TravelNode",
            "continue": "MapEnrichmentNode"
        }
    )

    builder.add_conditional_edges(
        "FoodNode",
        lambda state: "continue" if is_trip_planner(state) else "end",
        {
            "continue": "BudgetNode",
            "end": END
        }
    )

    builder.add_conditional_edges(
        "BudgetNode",
        lambda state: "continue" if is_trip_planner(state) else "end",
        {
            "continue": "FinalCompilerNode",
            "end": END
        }
    )    

    builder.add_edge("ConfidenceNode", END)

    return builder.compile()