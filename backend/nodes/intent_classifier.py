from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from backend.state.bajastate import BajaState
from backend.llm.provider import get_llm

llm = get_llm("classifier")

prompt = ChatPromptTemplate.from_messages([
("system", """
Classify the user's intent into ONE label:

- travel → itinerary only
- food → food recommendations only
- history → historical info
- budget → cost estimation only
- trip_planner → ANY request involving:
    - planning
    - itinerary
    - multi-day trip
    - OR combination of travel + food + budget

IMPORTANT:
If the request includes planning OR multiple aspects, ALWAYS return "trip_planner".

Respond with ONLY the label.
"""),
    ("human", "{input}")
])

chain = prompt | llm

def classify_intent(state: BajaState):
    latest_user_message = state["messages"][-1]["content"]
    user_text = str(latest_user_message).lower()

    # =========================
    # 🔥 RULE-BASED CLASSIFIER (PRIMARY)
    # =========================

    if any(word in user_text for word in ["plan", "itinerary", "trip", "3 days", "vacation"]):
        detected_intent = "trip_planner"

    elif any(word in user_text for word in ["food", "restaurant", "eat", "dinner", "lunch"]):
        detected_intent = "food"

    elif any(word in user_text for word in ["budget", "cost", "price", "expensive", "cheap"]):
        detected_intent = "budget"

    elif any(word in user_text for word in ["history", "historical", "museum", "culture"]):
        detected_intent = "history"

    elif any(word in user_text for word in ["travel", "visit", "places", "things to do"]):
        detected_intent = "travel"

    else:
        # =========================
        # 🤖 LLM FALLBACK (RARE)
        # =========================
        try:
            response = chain.invoke({
                "input": latest_user_message
            })

            content = response.content

            if isinstance(content, list):
                content = " ".join(map(str, content))
            else:
                content = str(content)

            detected_intent = content.strip().lower()

        except Exception as e:
            # 🔥 FAILSAFE (NO LLM = NO CRASH)
            print("⚠️ LLM classification failed, defaulting to trip_planner:", e)
            detected_intent = "trip_planner"

    print("INTENT:", detected_intent)

    return {
        "intent": detected_intent,
        "messages": state["messages"]
    }