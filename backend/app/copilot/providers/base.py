"""Abstract AI provider interface."""
from abc import ABC, abstractmethod
from typing import Optional, AsyncIterator
from pydantic import BaseModel


class AIResponse(BaseModel):
    content: str
    model: str = ""
    tokens_used: int = 0
    finish_reason: str = "stop"


class AIProvider(ABC):
    """Base class for AI providers. Implement this to swap Ollama for cloud LLMs."""

    @abstractmethod
    async def health_check(self) -> dict:
        """Check if the provider is available."""
        ...

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> AIResponse:
        """Generate a complete response."""
        ...

    @abstractmethod
    async def stream(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> AsyncIterator[str]:
        """Stream response tokens."""
        ...
