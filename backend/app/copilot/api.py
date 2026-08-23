"""AI Copilot API endpoints."""
import json
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.auth import get_current_user
from app.copilot import service
from app.copilot.schemas import CopilotRequest, CopilotInvestigate

router = APIRouter(prefix="/api/copilot", tags=["ai-copilot"])


@router.get("/health")
async def copilot_health():
    """Check AI copilot availability."""
    health = await service.health_check()
    return health


@router.post("/chat")
async def copilot_chat(request: CopilotRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Send a message to the AI copilot."""
    result = await service.chat(request, current_user.id, current_user.organization_id, db)

    # Audit log
    _log_interaction(db, current_user, "chat", request.message[:200], request.context_type, request.context_id, result)

    return result


@router.post("/chat/stream")
async def copilot_chat_stream(request: CopilotRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Stream a chat response from the AI copilot."""
    async def generate():
        async for chunk in service.stream_chat(request, current_user.id, current_user.organization_id, db):
            yield chunk

    return StreamingResponse(generate(), media_type="text/event-stream", headers={
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",
    })


@router.post("/investigate/alert/{alert_id}")
async def investigate_alert(alert_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Run a full AI investigation on an alert."""
    result = await service.investigate_alert(alert_id, current_user.id, current_user.organization_id, db)

    _log_interaction(db, current_user, "investigate_alert", f"Alert #{alert_id}", "alert", alert_id, result)

    return result


@router.post("/investigate/incident/{incident_id}")
async def investigate_incident(incident_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Run a full AI investigation on an incident."""
    result = await service.investigate_incident(incident_id, current_user.id, current_user.organization_id, db)

    _log_interaction(db, current_user, "investigate_incident", f"Incident #{incident_id}", "incident", incident_id, result)

    return result


@router.post("/clear")
async def clear_conversation(current_user: User = Depends(get_current_user)):
    """Clear conversation history."""
    service.clear_conversation(current_user.id)
    return {"message": "Conversation cleared"}


def _log_interaction(db, user, action, message, context_type, context_id, result):
    """Log copilot interaction for audit."""
    try:
        from app.models.audit_log import AuditLog
        audit = AuditLog(
            action=f"copilot_{action}",
            resource_type="copilot",
            resource_id=context_id,
            details=f"Message: {message[:200]} | Error: {result.get('error', False)} | Model: {result.get('model', 'unknown')}",
            user_id=user.id,
            organization_id=user.organization_id,
        )
        db.add(audit)
        db.commit()
    except Exception:
        pass  # Don't fail the request if audit logging fails
