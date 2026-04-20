from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from backend.state.bajastate import BajaState
from backend.llm.provider import get_llm

llm = get_llm()

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a Baja California history expert. Provide historical insights, cultural background, and key events."),
    ("placeholder", "{chat_history}"),
    ("human", "{user_input}")
])

chain = prompt | llm

def history_node(state: BajaState):
    response = chain.invoke({
        "chat_history": state["chat_history"],
        "user_input": state["user_input"]
    })

    updated_history = state["chat_history"] + [
        {"role": "assistant", "content": response.content}
    ]

    return {
        **state,
        "chat_history": updated_history
    }
