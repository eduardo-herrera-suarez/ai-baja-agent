from database.database import save_agent_state
from backend.nodes.travel_node import travel_node
from backend.nodes.food_node import food_node
from backend.nodes.budget_node import budget_node
from backend.nodes.map_enrichment_node import map_enrichment_node
from backend.nodes.critic_node import critic_node
from backend.nodes.final_compiler_node import final_compiler_node

TOOLS = {
    "travel": travel_node,
    "food": food_node,
    "budget": budget_node,
    "map": map_enrichment_node,
    "critic": critic_node
}

def planner(state):

    if not state.get("travel"):
        return ["travel"]

    if not state.get("food"):
        return ["food"]

    if not state.get("budget"):
        return ["budget"]

    if not state.get("enriched_plan"):
        return ["map"]

    return ["critic"]


def agent_orchestrator(state):

    session_id = state["session_id"]
    memory = state.get("memory", {})

    while True:
        steps = planner(state)

        print("🧠 PLAN:", steps)

        if steps == ["critic"]:
            break

        for step in steps:
            tool_fn = TOOLS.get(step)

            if not tool_fn:
                continue

            print(f"⚙️ Executing: {step}")

            result = tool_fn(state)
            state.update(result)

            memory.update({
                "travel": state.get("travel"),
                "food": state.get("food"),
                "budget": state.get("budget"),
                "route": (state.get("enriched_plan") or {}).get("route")
            })

            save_agent_state(session_id, memory)

    # final step
    result = TOOLS["critic"](state)
    state.update(result)

    return final_compiler_node(state)