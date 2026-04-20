from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from backend.agent.orchestrator import agent_orchestrator
from database.database import (
    init_db,
    save_message,
    get_conversation,
    get_summary,
    get_agent_state
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for dev (later restrict)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()


class ChatRequest(BaseModel):
    session_id: str
    message: str


@app.post("/chat")
def chat(req: ChatRequest):

    # =========================
    # 1️⃣ Load memory
    # =========================
    if "plan" in req.message.lower():
        history = []
        summary = ""
        memory = {}
    else:
        history = get_conversation(req.session_id)
        summary = get_summary(req.session_id)
        memory = get_agent_state(req.session_id)

    # =========================
    # 2️⃣ Append user message
    # =========================
    history.append({
        "role": "user",
        "content": req.message
    })

    # =========================
    # 3️⃣ Build state
    # =========================
    state = {
        "session_id": req.session_id,
        "messages": history,
        "summary": summary,
        "memory": memory
    }

    # =========================
    # 4️⃣ Call orchestrator (🔥 FIX)
    # =========================
    result = agent_orchestrator(state)

    # =========================
    # 5️⃣ Extract response
    # =========================
    assistant_reply = result["messages"][-1]["content"]

    # =========================
    # 6️⃣ Save memory (🔥 FIX: BEFORE return)
    # =========================
    save_message(req.session_id, "user", req.message)
    save_message(req.session_id, "assistant", str(assistant_reply))

    # =========================
    # 7️⃣ Return response
    # =========================
    if isinstance(assistant_reply, dict):
        return {
            "confidence": assistant_reply.get("confidence", 0.8),
            "response": assistant_reply.get("improved_plan", assistant_reply)
        }

    return {
        "confidence": result.get("confidence", 0.8),
        "response": assistant_reply
    }