# Niksmind — Certification Preparation Platform

**Prepare. Practice. Master.**

A unified certification preparation platform for Microsoft, AWS, Cisco, and CompTIA certifications.

## Features

- 🎯 **Practice Engine** — 50 free + 50 premium MCQs per topic
- 📝 **Mock Exams** — Timed exam simulation with domain-weighted distribution
- 🧠 **Adaptive Learning** — AI-powered weak area detection
- 🤖 **AI Tutor** — Ollama-powered grounded Q&A
- 🃏 **Flashcards** — Spaced repetition learning
- 📊 **Progress Analytics** — Readiness scores and mastery tracking
- 💳 **Payments** — Razorpay integration with server-side verification
- 📄 **Document Intelligence** — Upload and query study materials

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL (or Docker)
- Ollama (optional, for AI features)

### Docker Setup (Recommended)

```bash
cd niksmind
docker-compose up -d
```

### Manual Setup

**Backend:**
```bash
cd backend
pip install -r requirements.txt
# Set up PostgreSQL and create database
createdb niksmind
# Run migrations
alembic upgrade head
# Seed data
python seed.py
# Start server
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### Environment Variables

Copy `.env.example` to `.env` in both `backend/` and `frontend/` directories.

## Default Accounts

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@niksmind.com | admin123 |
| Demo | demo@niksmind.com | demo123 |

## Architecture

```
niksmind/
├── frontend/          Next.js + React + TypeScript + Tailwind
├── backend/           FastAPI + SQLAlchemy + PostgreSQL
├── content/           Certification content data
├── docker-compose.yml
└── .env.example
```

## API Documentation

Once running, visit `http://localhost:8000/docs` for the Swagger API documentation.

## Supported Certifications

- **Microsoft**: AZ-900 (Azure Fundamentals)
- **AWS**: Cloud Practitioner
- **Cisco**: CCNA 200-301
- **CompTIA**: Security+ SY0-701

## Tech Stack

- **Frontend**: Next.js 14, React 18, TypeScript, Tailwind CSS, Zustand
- **Backend**: Python 3.11, FastAPI, SQLAlchemy, Alembic
- **Database**: PostgreSQL with pgvector
- **AI**: Ollama (local LLM)
- **Payments**: Razorpay
- **Auth**: JWT with bcrypt password hashing

## License

Private — All rights reserved.
