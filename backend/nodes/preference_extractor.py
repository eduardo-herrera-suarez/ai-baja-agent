from langchain_core.prompts import ChatPromptTemplate
from backend.llm.provider import get_llm
from database.database import get_preferences, save_preferences
from backend.state.bajastate import BajaState
import json

llm = get_llm("preferences")

prompt = ChatPromptTemplate.from_messages([
    ("system", """
Extract user preferences from the message.

Return JSON only.

Possible fields:
- interests (beaches, food, hiking, nightlife)
- budget (low, medium, high)
- travel_style (relaxed, adventure, luxury)

If nothing found, return empty JSON {{}}.
"""),
    ("human", "{input}")
])

chain = prompt | llm

def preference_extractor(state: BajaState):
    session_id = state["session_id"]
    latest_user_message = state["messages"][-1]["content"]

    response = chain.invoke({"input": latest_user_message})

    try:
        extracted = json.loads(response.content)
    except:
        extracted = {}

    existing = get_preferences(session_id)

    # merge preferences
    updated = {**existing, **extracted}

    save_preferences(session_id, updated)

    return {
        "messages": state["messages"]
    }