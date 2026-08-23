"""Ollama AI provider - local LLM runtime."""
import json
import httpx
from typing import AsyncIterator
from app.copilot.providers.base import AIProvider, AIResponse
from app.config import get_settings

settings = get_settings()


class OllamaProvider(AIProvider):
    def __init__(self):
        self.base_url = getattr(settings, "OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = getattr(settings, "OLLAMA_MODEL", "llama3.2")
        self.timeout = getattr(settings, "COPILOT_TIMEOUT", 120)

    async def health_check(self) -> dict:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                if resp.status_code == 200:
                    models = resp.json().get("models", [])
                    model_names = [m.get("name", "") for m in models]
                    available = any(self.model in name for name in model_names)
                    return {
                        "status": "online" if available else "model_missing",
                        "provider": "ollama",
                        "model": self.model,
                        "available_models": model_names,
                        "model_configured": available,
                    }
                return {"status": "error", "detail": f"Ollama returned {resp.status_code}"}
        except Exception as e:
            return {"status": "offline", "provider": "ollama", "detail": str(e)}

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> AIResponse:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(f"{self.base_url}/api/chat", json=payload)
            resp.raise_for_status()
            data = resp.json()

        message = data.get("message", {})
        return AIResponse(
            content=message.get("content", ""),
            model=data.get("model", self.model),
            tokens_used=data.get("eval_count", 0) + data.get("prompt_eval_count", 0),
            finish_reason="stop",
        )

    async def stream(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> AsyncIterator[str]:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream("POST", f"{self.base_url}/api/chat", json=payload) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if line:
                        try:
                            chunk = json.loads(line)
                            content = chunk.get("message", {}).get("content", "")
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            continue
