from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import get_settings
from app.database import engine, Base
from app.api import auth, certifications, questions, mock_exams, progress, ai_tutor, payments, flashcards, documents, search, admin
from app.api import careers, bookmarks_notes, notifications, question_reports, achievements, activity, content_versions, admin_analytics, coupons

settings = get_settings()

app = FastAPI(
    title="Niksmind API",
    description="Certification Preparation Platform API",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

# Register routers
app.include_router(auth.router)
app.include_router(certifications.router)
app.include_router(questions.router)
app.include_router(mock_exams.router)
app.include_router(progress.router)
app.include_router(ai_tutor.router)
app.include_router(payments.router)
app.include_router(flashcards.router)
app.include_router(documents.router)
app.include_router(search.router)
app.include_router(admin.router)
app.include_router(careers.router)
app.include_router(bookmarks_notes.router)
app.include_router(notifications.router)
app.include_router(question_reports.router)
app.include_router(achievements.router)
app.include_router(activity.router)
app.include_router(content_versions.router)
app.include_router(admin_analytics.router)
app.include_router(coupons.router)


@app.get("/")
async def root():
    return {
        "name": "Niksmind API",
        "version": "1.0.0",
        "description": "Certification Preparation Platform",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
