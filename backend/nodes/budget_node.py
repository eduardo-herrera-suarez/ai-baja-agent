from langchain_core.prompts import ChatPromptTemplate
from backend.llm.provider import get_llm
from backend.state.bajastate import BajaState
from langchain_core.prompts import ChatPromptTemplate
import json
import re

llm = get_llm("budget")

budget_prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are a travel budget planner.

====================
TASK
====================
Generate a structured budget in JSON format ONLY.

====================
RULES
====================
- Base the budget on the provided travel and food plan
- Use realistic estimates for Baja California, Mexico
- All values must be numbers (no currency symbols, no text)
- Do NOT include explanations
- Do NOT include extra text

====================
OUTPUT FORMAT (STRICT)
====================

{{
  "budget": {{
    "accommodation": number,
    "food": number,
    "transportation": number,
    "activities": number,
    "total": number
  }}
}}

====================
VALIDATION RULES
====================
- All fields MUST be present
- total MUST equal the sum of all categories
- Output MUST be valid JSON
- No markdown
- No extra text
"""),
    ("human", "{input}")
])

budget_chain = budget_prompt | llm

def budget_node(state: BajaState):

    memory = state.get("memory", {})

    # 🔥 If already computed → reuse from memory
    if memory.get("budget"):
        print("⚠️ Skipping budget (already exists)")
        return {
            **state,
            "budget": memory.get("budget")  # ✅ rehydrate
        }

    travel = state.get("travel", {})
    food = state.get("food", {})

    # 🔴 Guard: need both travel + food
    if not travel or not food:
        print("⚠️ Missing travel or food, skipping budget")
        return state

    input_data = {
        "travel": travel,
        "food": food
    }

    full_input = json.dumps(input_data, indent=2)

    response = budget_chain.invoke({
        "input": full_input
    })

    raw_output = response.content

    # 🔥 Safe JSON extraction
    try:
        clean = re.search(r"\{.*\}", raw_output, re.DOTALL)
        parsed = json.loads(clean.group())
        budget_data = parsed.get("budget", {})
    except Exception:
        budget_data = {}

    return {
        **state,  # ✅ preserve everything
        "messages": state.get("messages", []) + [
            {"role": "assistant", "content": raw_output}
        ],
        "budget": budget_data
    }