"""Copilot API schemas."""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class CopilotRequest(BaseModel):
    message: str
    context_type: Optional[str] = None  # "alert", "incident", "log", "threat_intel", "dashboard"
    context_id: Optional[int] = None    # alert_id, incident_id, etc.
    conversation_history: Optional[List[ChatMessage]] = None


class CopilotInvestigate(BaseModel):
    alert_id: Optional[int] = None
    incident_id: Optional[int] = None
    ip_address: Optional[str] = None
    domain: Optional[str] = None
    technique_id: Optional[str] = None


class ToolCall(BaseModel):
    name: str
    arguments: Dict[str, Any]
    result: Optional[Any] = None


class CopilotResponse(BaseModel):
    response: str
    tools_used: List[str] = []
    context_type: Optional[str] = None
    context_id: Optional[int] = None
    model: str = ""
    tokens_used: int = 0
    streaming: bool = False
