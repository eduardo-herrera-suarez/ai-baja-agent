from langchain_core.prompts import ChatPromptTemplate
from backend.llm.provider import get_llm
from backend.state.bajastate import BajaState
import json
import re

llm = get_llm("food")

prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are a food recommendation expert for travel itineraries.

TASK:
Generate a structured food plan in JSON format ONLY.

RULES:
- Base recommendations ONLY on the provided travel itinerary
- Include meals for each day: breakfast, lunch, dinner, snacks
- Do NOT include budget
- Do NOT include prices
- Do NOT include transportation
- Do NOT include explanations
- Do NOT repeat the itinerary

OUTPUT FORMAT (STRICT):

{{
  "food": {{
    "day_1": [
      {{
        "meal": "breakfast",
        "description": "string"
      }},
      {{
        "meal": "lunch",
        "description": "string"
      }},
      {{
        "meal": "dinner",
        "description": "string"
      }},
      {{
        "meal": "snacks",
        "description": "string"
      }}
    ],
    "day_2": [...],
    "day_3": [...]
  }}
}}

VALIDATION RULES:
- Each day MUST include all 4 meals
- Output MUST be valid JSON
- No markdown
- No extra text
"""),
    ("human", "{input}")
])

chain = prompt | llm

def food_node(state: BajaState):

    memory = state.get("memory", {})

    # 🔥 If already computed → reuse from memory
    if memory.get("food"):
        print("⚠️ Skipping food (already exists)")
        return {
            **state,
            "food": memory.get("food")  
        }

    travel = state.get("travel", {})

    if not travel:
        print("⚠️ No travel found, skipping food generation")
        return state

    travel_text = json.dumps(travel, indent=2)

    full_input = f"""
Travel itinerary:
{travel_text}
"""

    response = chain.invoke({
        "input": full_input
    })

    raw_output = response.content

    try:
        clean = re.search(r"\{.*\}", raw_output, re.DOTALL)
        parsed = json.loads(clean.group())
        food_data = parsed.get("food", {})
    except Exception:
        food_data = {}

    return {
        **state,  # 🔥 preserve existing state
        "messages": state.get("messages", []) + [
            {"role": "assistant", "content": raw_output}
        ],
        "food": food_data
    }