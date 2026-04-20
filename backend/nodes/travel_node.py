from langchain_core.prompts import ChatPromptTemplate
from backend.state.bajastate import BajaState
from backend.llm.provider import get_llm
from database.database import get_preferences
import json
import re

llm = get_llm("travel")

prompt = ChatPromptTemplate.from_messages([
("system", """
You are a travel planner specialized in Baja California, Mexico.

====================
TASK
====================
Generate a structured 3-day itinerary in JSON format ONLY.

====================
DESTINATION RULES
====================
- Locations must be in Baja California, Mexico.
- Allowed areas ONLY:
  Tijuana, Rosarito, Ensenada, Valle de Guadalupe, Puerto Nuevo, San Felipe, San Quintin.
- Do NOT include destinations outside these areas.

====================
GEOGRAPHIC CONSTRAINTS (CRITICAL)
====================
- Consecutive locations MUST be geographically close.
- Maximum distance between consecutive locations: 150 km.
- Prefer logical travel flow (north → south OR clustered areas).
- Avoid zig-zag or cross-peninsula routes.
- Example of GOOD flow:
  Rosarito → Puerto Nuevo → Ensenada → Valle de Guadalupe
- Example of BAD flow:
  Valle → San Felipe → San Quintin

====================
RETRY AWARENESS
====================
- If the previous itinerary failed validation:
  - Avoid long-distance jumps
  - Keep locations within the same region
  - Prefer fewer unique cities

====================
CONTENT RULES
====================
- Do NOT include budget.
- Do NOT include food.
- Do NOT include explanations.
- Focus only on activities and locations.

====================
OUTPUT FORMAT (STRICT)
====================
Return ONLY valid JSON with this exact structure:

{{ 
  "travel": {{
    "day_1": [
      {{
        "time": "HH:MM",
        "activity": "string",
        "location": "string"
      }}
    ],
    "day_2": [...],
    "day_3": [...]
  }}
}}

====================
VALIDATION RULES
====================
- Each day MUST have at least 2 activities.
- Time must be valid (HH:MM).
- Locations must be from the allowed list.
- Output MUST be valid JSON.
- No markdown.
- No extra text.
"""),
    ("human", "{input}")
])

chain = prompt | llm


def travel_node(state: BajaState):

    memory = state.get("memory", {})

    if memory.get("travel") and not state.get("failed_segments"):
        print("⚠️ Skipping travel (already exists)")
        return {
            **state,
            "travel": memory.get("travel")
        }

    session_id = state["session_id"]
    prefs = get_preferences(session_id)

    # Limit context
    messages = state.get("messages", [])[-5:]

    context = "\n\n".join([
        f"{msg.get('role', '').upper()}: {msg.get('content', '')}"
        for msg in messages
        if isinstance(msg, dict)
    ])

    # Replanning feedback
    failed_segments = state.get("failed_segments", [])

    failure_context = ""
    if failed_segments:
        failure_context = f"""
Previous route failed between these locations:
{failed_segments}

Fix the itinerary by avoiding these routes.
Keep locations closer together.
"""

    full_input = f"""
User Preferences:
{prefs}

Conversation:
{context}

{failure_context}
"""

    response = chain.invoke({
        "input": full_input
    })

    raw_output = response.content

    try:
        clean = re.search(r"\{.*\}", raw_output, re.DOTALL)
        parsed = json.loads(clean.group())
        travel_data = parsed.get("travel", {})
    except Exception:
        print("⚠️ Failed to parse travel JSON")
        return state  # 🔥 safer fallback

    return {
        **state,
        "messages": state.get("messages", []) + [
            {
                "role": "assistant",
                "content": raw_output
            }
        ],
        "travel": travel_data,
        "retry_count": state.get("retry_count", 0) + 1,
        "replan_count": state.get("replan_count", 0) + 1
    }