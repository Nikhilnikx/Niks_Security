"""Main AI Copilot service - orchestrates providers, tools, context, and conversation."""
import json
import time
from typing import Optional, List, AsyncIterator
from sqlalchemy.orm import Session

from app.copilot.providers.base import AIProvider
from app.copilot.providers.ollama import OllamaProvider
from app.copilot.prompts import (
    SYSTEM_PROMPT, ALERT_INVESTIGATION_PROMPT, INCIDENT_INVESTIGATION_PROMPT,
    DASHBOARD_PROMPT, THREAT_HUNT_PROMPT, MITRE_PROMPT,
)
from app.copilot.context import (
    build_alert_context, build_incident_context, build_dashboard_context,
    build_ip_context,
)
from app.copilot.sanitizer import sanitize_dict, sanitize_context
from app.copilot.tools.registry import get_tool_schemas, call_tool
from app.copilot.schemas import CopilotRequest, CopilotResponse, ChatMessage

# Import tools to register them
import app.copilot.tools.alerts
import app.copilot.tools.logs
import app.copilot.tools.incidents
import app.copilot.tools.assets


# Conversation memory (in-memory, per-user)
_conversations: dict = {}  # user_id -> list of messages
MAX_HISTORY = 20

# Rate limiting
_rate_limits: dict = {}  # user_id -> list of timestamps
RATE_LIMIT_PER_MINUTE = 15


def _get_provider() -> AIProvider:
    """Get the configured AI provider."""
    return OllamaProvider()


def _check_rate_limit(user_id: int) -> bool:
    """Check if user is within rate limits."""
    now = time.time()
    if user_id not in _rate_limits:
        _rate_limits[user_id] = []
    # Clean old entries
    _rate_limits[user_id] = [t for t in _rate_limits[user_id] if now - t < 60]
    if len(_rate_limits[user_id]) >= RATE_LIMIT_PER_MINUTE:
        return False
    _rate_limits[user_id].append(now)
    return True


def _get_history(user_id: int) -> list:
    """Get conversation history for a user."""
    return _conversations.get(user_id, [])


def _add_to_history(user_id: int, role: str, content: str):
    """Add message to conversation history."""
    if user_id not in _conversations:
        _conversations[user_id] = []
    _conversations[user_id].append({"role": role, "content": content})
    # Trim to max history
    if len(_conversations[user_id]) > MAX_HISTORY:
        _conversations[user_id] = _conversations[user_id][-MAX_HISTORY:]


def clear_conversation(user_id: int):
    """Clear conversation history for a user."""
    _conversations.pop(user_id, None)


async def health_check() -> dict:
    """Check AI copilot health."""
    provider = _get_provider()
    return await provider.health_check()


def _build_prompt_with_context(request: CopilotRequest, context: dict, tool_schemas: list) -> str:
    """Build the full prompt with context and tool definitions."""
    prompt_parts = []

    # Add tool definitions
    if tool_schemas:
        prompt_parts.append("## Available Tools:")
        for tool in tool_schemas:
            prompt_parts.append(f"- **{tool['name']}**: {tool['description']}")
        prompt_parts.append("")

    # Add context
    if context and not context.get("error"):
        prompt_parts.append("## Security Context:")
        prompt_parts.append(json.dumps(context, indent=2, default=str)[:8000])  # Limit context size
        prompt_parts.append("")

    # Add conversation history
    history = _get_history(request.context_id or 0)
    if history:
        prompt_parts.append("## Previous conversation:")
        for msg in history[-6:]:  # Last 6 messages
            prompt_parts.append(f"{msg['role'].upper()}: {msg['content'][:500]}")
        prompt_parts.append("")

    # Add user question
    prompt_parts.append(f"## Analyst Question:\n{request.message}")

    return "\n".join(prompt_parts)


def _get_system_prompt(context_type: Optional[str] = None) -> str:
    """Get the appropriate system prompt based on context."""
    base = SYSTEM_PROMPT
    if context_type == "alert":
        return base + "\n\n" + ALERT_INVESTIGATION_PROMPT
    elif context_type == "incident":
        return base + "\n\n" + INCIDENT_INVESTIGATION_PROMPT
    elif context_type == "dashboard":
        return base + "\n\n" + DASHBOARD_PROMPT
    elif context_type == "threat_hunt":
        return base + "\n\n" + THREAT_HUNT_PROMPT
    elif context_type == "mitre":
        return base + "\n\n" + MITRE_PROMPT
    return base


async def chat(request: CopilotRequest, user_id: int, org_id: int, db: Session) -> dict:
    """Handle a chat message from the copilot."""
    # Rate limit check
    if not _check_rate_limit(user_id):
        return {"response": "Rate limit reached. Please wait a moment before sending another message.", "error": True}

    provider = _get_provider()

    # Check provider health
    health = await provider.health_check()
    if health.get("status") == "offline":
        return {
            "response": "🔒 AI Copilot is currently offline. Please ensure Ollama is running (`ollama serve`). Threat detection remains fully operational.",
            "error": True,
        }
    if health.get("status") == "model_missing":
        return {
            "response": f"⚠️ AI model '{health.get('model', 'unknown')}' is not available. Please pull it with `ollama pull {health.get('model', 'llama3.2')}`. Available models: {', '.join(health.get('available_models', []))}",
            "error": True,
        }

    # Build context based on context_type
    context = {}
    if request.context_type == "alert" and request.context_id:
        context = build_alert_context(db, org_id, request.context_id)
    elif request.context_type == "incident" and request.context_id:
        context = build_incident_context(db, org_id, request.context_id)
    elif request.context_type == "dashboard":
        context = build_dashboard_context(db, org_id)
    elif request.context_type == "ip" and request.message:
        # Try to extract IP from message
        import re
        ip_match = re.search(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', request.message)
        if ip_match:
            ip = ip_match.group()
            context = build_ip_context(db, org_id, ip)
            context_type = "ip"
        else:
            context_type = request.context_type
    else:
        context_type = request.context_type

    # Sanitize context
    context = sanitize_context(context)

    # Build prompt
    tool_schemas = get_tool_schemas()
    full_prompt = _build_prompt_with_context(request, context, tool_schemas)
    system_prompt = _get_system_prompt(request.context_type)

    try:
        # Generate response
        response = await provider.generate(
            prompt=full_prompt,
            system_prompt=system_prompt,
            temperature=0.3,
            max_tokens=4096,
        )

        # Update conversation history
        _add_to_history(user_id, "user", request.message[:1000])
        _add_to_history(user_id, "assistant", response.content[:1000])

        return {
            "response": response.content,
            "tools_used": [],
            "context_type": request.context_type,
            "context_id": request.context_id,
            "model": response.model,
            "tokens_used": response.tokens_used,
        }

    except Exception as e:
        return {
            "response": f"⚠️ AI Copilot encountered an error: {str(e)}. Threat detection remains operational.",
            "error": True,
        }


async def investigate_alert(alert_id: int, user_id: int, org_id: int, db: Session) -> dict:
    """Full alert investigation workflow."""
    provider = _get_provider()
    health = await provider.health_check()
    if health.get("status") != "online":
        return {"response": "AI Copilot is offline.", "error": True}

    context = build_alert_context(db, org_id, alert_id)
    if context.get("error"):
        return {"response": context["error"], "error": True}

    context = sanitize_context(context)
    tool_schemas = get_tool_schemas()

    prompt = f"""Investigate this security alert thoroughly.

## Alert Context:
{json.dumps(context, indent=2, default=str)[:8000]}

Generate a structured investigation report with:
1. **Summary** - What happened
2. **Evidence** - Confirmed findings from the data
3. **Risk Assessment** - Why this is dangerous
4. **MITRE ATT&CK** - Relevant techniques
5. **Related Activity** - Other events from this source
6. **Recommended Investigation** - Next steps
7. **Recommended Response** - Response actions
8. **Confidence** - Your confidence level

Use the evidence from the data. Clearly distinguish confirmed facts from hypotheses."""

    try:
        response = await provider.generate(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT + "\n\n" + ALERT_INVESTIGATION_PROMPT,
            temperature=0.3,
            max_tokens=4096,
        )

        _add_to_history(user_id, "user", f"Investigate alert #{alert_id}")
        _add_to_history(user_id, "assistant", response.content[:1000])

        return {
            "response": response.content,
            "context_type": "alert",
            "context_id": alert_id,
            "tools_used": [],
            "model": response.model,
            "tokens_used": response.tokens_used,
        }
    except Exception as e:
        return {"response": f"Investigation failed: {str(e)}", "error": True}


async def investigate_incident(incident_id: int, user_id: int, org_id: int, db: Session) -> dict:
    """Full incident investigation workflow."""
    provider = _get_provider()
    health = await provider.health_check()
    if health.get("status") != "online":
        return {"response": "AI Copilot is offline.", "error": True}

    context = build_incident_context(db, org_id, incident_id)
    if context.get("error"):
        return {"response": context["error"], "error": True}

    context = sanitize_context(context)

    prompt = f"""Analyze this security incident comprehensively.

## Incident Context:
{json.dumps(context, indent=2, default=str)[:8000]}

Generate:
1. **Incident Summary** - What happened
2. **Attack Timeline** - Chronological events
3. **Potential Attack Path** - How the attack progressed
4. **Affected Assets** - What was impacted
5. **Indicators of Compromise** - IOCs found
6. **MITRE Techniques** - Techniques used
7. **Risk Assessment** - Impact and severity
8. **Recommended Investigation** - Next steps
9. **Recommended Response** - Containment and remediation"""

    try:
        response = await provider.generate(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT + "\n\n" + INCIDENT_INVESTIGATION_PROMPT,
            temperature=0.3,
            max_tokens=4096,
        )

        _add_to_history(user_id, "user", f"Investigate incident #{incident_id}")
        _add_to_history(user_id, "assistant", response.content[:1000])

        return {
            "response": response.content,
            "context_type": "incident",
            "context_id": incident_id,
            "model": response.model,
            "tokens_used": response.tokens_used,
        }
    except Exception as e:
        return {"response": f"Investigation failed: {str(e)}", "error": True}


async def stream_chat(request: CopilotRequest, user_id: int, org_id: int, db: Session):
    """Stream a chat response."""
    provider = _get_provider()
    health = await provider.health_check()
    if health.get("status") != "online":
        yield json.dumps({"type": "error", "content": "AI Copilot is offline."}) + "\n"
        return

    context = {}
    if request.context_type == "alert" and request.context_id:
        context = build_alert_context(db, org_id, request.context_id)
    elif request.context_type == "incident" and request.context_id:
        context = build_incident_context(db, org_id, request.context_id)
    elif request.context_type == "dashboard":
        context = build_dashboard_context(db, org_id)

    context = sanitize_context(context)
    tool_schemas = get_tool_schemas()
    full_prompt = _build_prompt_with_context(request, context, tool_schemas)
    system_prompt = _get_system_prompt(request.context_type)

    try:
        async for chunk in provider.stream(
            prompt=full_prompt,
            system_prompt=system_prompt,
            temperature=0.3,
            max_tokens=4096,
        ):
            yield json.dumps({"type": "chunk", "content": chunk}) + "\n"

        yield json.dumps({"type": "done"}) + "\n"

        _add_to_history(user_id, "user", request.message[:1000])

    except Exception as e:
        yield json.dumps({"type": "error", "content": str(e)}) + "\n"
