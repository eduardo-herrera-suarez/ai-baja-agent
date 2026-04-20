from langchain_core.prompts import ChatPromptTemplate
from backend.llm.provider import get_llm
from backend.state.bajastate import BajaState
import json

# 🔥 Use lightweight model
llm = get_llm("classifier")

prompt = ChatPromptTemplate.from_messages([
("system", """
You are a strict travel plan reviewer.

Evaluate the plan and:

1. Fix any issues
2. Assign a confidence score (0 to 1)

Confidence rules:
- 0.9–1.0 → Perfect
- 0.75–0.89 → Minor issues
- 0.5–0.74 → Moderate issues
- <0.5 → Major issues

STRICT RULES:
- Keep exactly 3 days
- Ensure all locations are in Baja California
- Fix formatting to: HH:MM AM - Activity
- Replace vague items like "Lunch break" with real activities
- Ensure chronological order within each day
- Use consistent action verbs (Visit, Explore, Relax, Walk)
- Add clarity for transitions (e.g., drives between cities)

Return ONLY valid JSON with EXACT structure:

{{
  "confidence": number,
  "improved_plan": {{
    "travel": {{
      "Day 1": [],
      "Day 2": [],
      "Day 3": []
    }},
    "food": {{
      "Day 1": [],
      "Day 2": [],
      "Day 3": []
    }},
    "budget": {{
      "accommodation": "",
      "food": "",
      "transportation": "",
      "activities": "",
      "total": ""
    }}
  }}
}}

DO NOT include text before or after.
DO NOT explain anything.
DO NOT use markdown.
"""),
    ("human", "{input}")
])

chain = prompt | llm

def critic_node(state: BajaState):
    final_output = state["messages"][-1]["content"]
    response = chain.invoke({
        "input": final_output
    })

    content = response.content

    try:
        parsed = json.loads(content)
    except:
        parsed = {
            "confidence": 0.5,
            "improved_plan": final_output
        }

    return {
        "messages": state["messages"] + [
            {
                "role": "assistant",
                "content": parsed  # ✅ NOT json.dumps
            }
        ]
    }