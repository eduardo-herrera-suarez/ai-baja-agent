from database.database import save_message, get_conversation
from backend.state.bajastate import BajaState

def load_memory(state: BajaState):
    session_id = state["session_id"]
    conversation = get_conversation(session_id)

    state["messages"] = conversation
    return state


def save_memory(state: BajaState):
    session_id = state["session_id"]

    # Save latest assistant message
    last_message = state["messages"][-1]

    save_message(session_id, last_message["role"], last_message["content"])

    return state
