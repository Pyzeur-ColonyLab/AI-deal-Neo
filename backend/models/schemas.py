from typing import Optional, Dict, Any
from pydantic import BaseModel

# --- Chat ---
class ChatRequest(BaseModel):
    message: str
    channel: str
    user_id: str

class ChatResponse(BaseModel):
    response: str
    model: str
    timestamp: str
    parameters_used: Dict[str, Any] 