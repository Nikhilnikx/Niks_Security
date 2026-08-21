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
- 🚀 **Career Paths** — Personalized certification roadmaps
- 🏆 **Gamification** — XP, levels, and achievements
- 🔔 **Notifications** — Smart reminders and updates
- 📄 **Document Intelligence** — Upload and query study materials

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14, React 18, TypeScript, Tailwind CSS |
| Backend | Python 3.11, FastAPI, SQLAlchemy, Alembic |
| Database | PostgreSQL 16 + pgvector |
| AI | Ollama (local LLM) |
| Payments | Razorpay |
| Animations | React Bits (Antigravity, SplitText, CountUp) |

---

## Quick Start (Development)

### Prerequisites
- Node.js 18+
- Python 3.11+
- Docker

### 1. Start PostgreSQL
```bash
docker run -d --name niksmind-db \
  -e POSTGRES_DB=niksmind \
  -e POSTGRES_USER=niksmind \
  -e POSTGRES_PASSWORD=niksmind \
  -p 5432:5432 pgvector/pgvector:pg16
```

### 2. Backend
```bash
cd backend
pip install -r requirements.txt
cp ../.env.example .env
python seed.py
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend
```bash
cd frontend
npm install
npm run dev
```

### 4. Open
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs

### Demo Account
| Email | Password | Role |
|-------|----------|------|
| demo@niksmind.com | demo123 | User |
| admin@niksmind.com | admin123 | Admin |

---

## Production Deployment

### Option 1: Docker Compose (Recommended)

```bash
# 1. Configure environment
cp .env.production .env.production.local
# Edit .env.production.local with your values

# 2. Deploy
chmod +x deploy.sh
./deploy.sh

# 3. Access
# Frontend: https://yourdomain.com
# API: https://api.yourdomain.com
```

### Option 2: Vercel + Docker Backend

**Frontend (Vercel):**
```bash
cd frontend
# Connect to Vercel via GitHub
# Set environment variables in Vercel dashboard:
#   NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

**Backend (Docker):**
```bash
cd backend
docker build -t niksmind-backend .
docker run -d --name niksmind-api \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  -e SECRET_KEY=... \
  niksmind-backend
```

### Option 3: VPS (DigitalOcean, Hetzner, etc.)

```bash
# Install Docker
curl -fsSL https://get.docker.com | sh

# Clone and deploy
git clone <repo-url> niksmind
cd niksmind
cp .env.production .env.production.local
# Edit .env.production.local
chmod +x deploy.sh
./deploy.sh
```

---

## Project Structure

```
niksmind/
├── frontend/              Next.js frontend
│   ├── app/               Pages and routes
│   ├── components/        React components
│   │   ├── animations/    React Bits animations
│   │   └── layout/        Navigation, sidebar
│   ├── lib/               API client, store
│   └── types/             TypeScript types
│
├── backend/               FastAPI backend
│   ├── app/
│   │   ├── api/           API routes (14 routers)
│   │   ├── models/        SQLAlchemy models (25+)
│   │   ├── auth/          JWT authentication
│   │   └── main.py        FastAPI app
│   ├── migrations/        Alembic migrations
│   └── seed.py            Database seeder
│
├── nginx/                 Reverse proxy config
├── docker-compose.yml     Development compose
├── docker-compose.prod.yml Production compose
├── deploy.sh              Deployment script
└── .env.production        Production env template
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register` | POST | User registration |
| `/api/auth/login` | POST | User login |
| `/api/certifications` | GET | List certifications |
| `/api/careers/` | GET | Career paths |
| `/api/quizzes/start` | POST | Start practice quiz |
| `/api/mock-exams/start` | POST | Start mock exam |
| `/api/ai/chat` | POST | AI tutor chat |
| `/api/payments/create-order` | POST | Create Razorpay order |
| `/api/dashboard` | GET | User dashboard |
| `/api/activity/streak` | GET | Study streak |

Full API docs: http://localhost:8000/docs

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | ✅ | PostgreSQL connection string |
| `SECRET_KEY` | ✅ | JWT signing secret |
| `OLLAMA_BASE_URL` | ⚡ | Ollama server URL |
| `RAZORPAY_KEY_ID` | 💳 | Razorpay API key |
| `RAZORPAY_KEY_SECRET` | 💳 | Razorpay secret |
| `NEXT_PUBLIC_API_URL` | ✅ | Backend API URL |
| `FRONTEND_URL` | ✅ | Frontend URL for CORS |

---

## License

Private — All rights reserved.
