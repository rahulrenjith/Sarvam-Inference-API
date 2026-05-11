from pydantic import BaseModel, Field
from typing import Optional, Literal
from enum import Enum


class MessageRole(str, Enum):
    user = "user"
    assistant = "assistant"
    system = "system"


class ChatMessage(BaseModel):
    role: MessageRole
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    model: Optional[str] = None
    temperature: float = Field(default=0.2, ge=0, le=2)
    max_tokens: int = Field(default=512, ge=1, le=4096)
    use_cache: bool = True


class ChatResponse(BaseModel):
    response: str
    model: str
    usage: Optional[dict] = None
    latency_ms: Optional[float] = None
    cached: bool = False


class ServiceStatus(str, Enum):
    healthy = "healthy"
    degraded = "degraded"
    unhealthy = "unhealthy"


class ComponentHealth(BaseModel):
    status: ServiceStatus
    detail: Optional[str] = None


class HealthResponse(BaseModel):
    status: ServiceStatus
    version: str
    uptime_seconds: float
    components: dict[str, ComponentHealth]
