from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from app.config import settings

# Privilages
class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user" 
    ASSISTANT = "assistant"
    MODEL = "model"

# Message
class ChatMessage(BaseModel):
    role: MessageRole
    content: str


# Gemini Req and Res
class ChatRequest(BaseModel):
    message: str
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 150
    model: Optional[str] = settings.gemini_model


class ConversationRequest(BaseModel):
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 150
    model: Optional[str] = settings.gemini_model


class ChatResponse(BaseModel):
    response: str
    usage: Optional[dict] = None
    model: str


# Alpaca Req and Res
class AlpacaRequest(BaseModel):
    query : str



# Logging token usage
class UsageInfo(BaseModel):
    prompt_tokens : int
    output_tokens : int
    total_tokens : int