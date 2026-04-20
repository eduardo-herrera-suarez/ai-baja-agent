from backend.state.bajastate import BajaState
import json
import re

def final_compiler_node(state: BajaState):

    route = (state.get("enriched_plan") or {}).get("route")

    structured_output = {
        "travel": state.get("travel", {}),
        "food": state.get("food", {}),
        "budget": state.get("budget", {}),
        "route": route
    }

    return {
        "messages": [
            {
                "role": "assistant",
                "content": structured_output
            }
        ]
    }
