"""Niks Security - Cybersecurity SaaS Platform"""
import asyncio
import json
from datetime import datetime, timezone
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.database import engine, Base
from app.sse import alert_broadcaster

settings = get_settings()

app = FastAPI(
    title="Niks Security API",
    description="Production-Ready Cybersecurity SaaS Platform",
    version="1.0.0",
)

# CORS
origins = [o.strip() for o in settings.CORS_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables and seed data
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    from app.database import SessionLocal
    from app.seed import seed_database
    db = SessionLocal()
    try:
        seed_database(db)
    except Exception as e:
        print(f"Seed warning: {e}")
    finally:
        db.close()

# Health checks
@app.get("/health")
async def health():
    return {"status": "healthy", "service": "niks-security", "version": "1.0.0"}

@app.get("/readiness")
async def readiness():
    return {"status": "ready"}

# Register all API routers
from app.api import auth, dashboard, alerts, incidents, assets, logs, detection_rules
from app.api import threat_intel, mitre, notifications, audit_logs, reports, simulation, settings as settings_api
from app.api import onboarding
from app.models import notification_config  # Ensure table is created on startup

app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(alerts.router)
app.include_router(incidents.router)
app.include_router(assets.router)
app.include_router(logs.router)
app.include_router(detection_rules.router)
app.include_router(threat_intel.router)
app.include_router(mitre.router)
app.include_router(notifications.router)
app.include_router(audit_logs.router)
app.include_router(reports.router)
app.include_router(simulation.router)
app.include_router(settings_api.router)
app.include_router(onboarding.router)


@app.get("/api/events/stream")
async def stream_events(request: Request, org_id: int = None):
    """SSE endpoint - streams real-time alerts and notifications."""
    if not org_id:
        return {"error": "org_id query param required"}

    queue = alert_broadcaster.subscribe(org_id)

    async def event_generator():
        try:
            # Send initial connection event
            yield f"event: connected\ndata: {json.dumps({'message': 'Connected to alert stream', 'org_id': org_id})}\n\n"

            while True:
                # Check if client disconnected
                if await request.is_disconnected():
                    break

                try:
                    message = await asyncio.wait_for(queue.get(), timeout=30)
                    yield f"event: {message['event']}\ndata: {message['data']}\n\n"
                except asyncio.TimeoutError:
                    # Send keepalive ping
                    yield f": keepalive {datetime.now(timezone.utc).isoformat()}\n\n"
        finally:
            alert_broadcaster.unsubscribe(org_id, queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/")
async def root():
    return {"name": "Niks Security", "version": "1.0.0", "status": "running"}
