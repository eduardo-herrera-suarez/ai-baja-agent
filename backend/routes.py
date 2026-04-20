from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from backend.agent import agent
import asyncio

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    session_id: str

@router.post("/chat-stream")
async def chat_stream(request: ChatRequest):

    async def event_generator():
        async for chunk in agent.astream(
            {"input": request.message},
            config={"configurable": {"session_id": request.session_id}},
        ):
            # chunk is an AIMessage or BaseMessage
            if hasattr(chunk, "content") and chunk.content:
                yield chunk.content

    return StreamingResponse(
        event_generator(),
        media_type="text/plain"
    )

def route_intent(state: BajaState):
    return state["intent"]

graph.add_conditional_edges(
    "IntentClassifier",
    route_intent,
    {
        "travel": "TravelNode",
        "food": "FoodNode",
        "history": "HistoryNode",
        "budget": "BudgetNode",
        "mixed": "MixedNode",
    }
)
