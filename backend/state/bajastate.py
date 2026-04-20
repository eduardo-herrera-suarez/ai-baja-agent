from typing import TypedDict, List, Dict
from typing import Annotated
import operator

class BajaState(TypedDict, total=False):
    session_id: str
    messages: Annotated[list[dict[str, str]], operator.add]
    intent: str
    confidence: float

    travel: dict
    food: dict
    budget: dict
    enriched_plan: dict

    valid_travel: bool
    invalid_segment: dict
    retry_count: int