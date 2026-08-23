# NIKS SECURITY — Cybersecurity SaaS Platform

> **Detect. Investigate. Respond.**
> Real-time threat detection and security intelligence platform for modern infrastructure.

---

## 🛡️ Overview

NIKS SECURITY is a production-ready, enterprise-grade Security Operations Center (SOC) platform built with:

- **Backend:** FastAPI + SQLAlchemy + SQLite (upgradeable to PostgreSQL)
- **Frontend:** Next.js 14 + React 18 + TailwindCSS + Recharts
- **Auth:** JWT-based authentication with role-based access control
- **Detection Engine:** Modular rule-based threat detection pipeline

The platform follows the complete security workflow:

```
COLLECT → NORMALIZE → DETECT → CORRELATE → ENRICH → ALERT → INVESTIGATE → RESPOND → REPORT
```

---

## 🚀 Features

### Core Security
- **Threat Detection Engine** — 10+ built-in detection rules (brute force, port scanning, SQL injection, XSS, command injection, etc.)
- **Alert Management** — Full lifecycle with severity, status, confidence scoring, MITRE mapping
- **Incident Management** — NEW → TRIAGED → INVESTIGATING → CONTAINED → RESOLVED workflow
- **MITRE ATT&CK** — Technique matrix mapping with detection counts
- **Threat Intelligence** — IP, domain, hash lookup with risk scoring and geolocation
- **Log Management** — Upload, parse, normalize, search, and export security logs

### Platform
- **Multi-tenant SaaS** — Organizations, workspaces, and data isolation
- **RBAC** — Admin, Security Analyst, and Viewer roles
- **Dashboard** — Real-time security score, charts, alerts over time, severity distribution
- **Attack Simulation** — Safe, controlled attack simulations for testing detection rules
- **Reports** — Generate security summaries, incident reports, threat reports
- **API Keys** — REST API with key-based authentication
- **Audit Logging** — Track all sensitive actions
- **Notifications** — In-app notification system

### Design
- Dark enterprise SOC aesthetic
- Premium cybersecurity visual identity
- Responsive design (desktop, tablet, mobile)
- Glass effects, gradient borders, severity indicators
- Professional data visualization with Recharts

---

## 📁 Project Structure

```
niksmind/
├── backend/
│   ├── app/
│   │   ├── api/           # API route handlers
│   │   │   ├── auth.py    # Authentication endpoints
│   │   │   ├── dashboard.py
│   │   │   ├── alerts.py
│   │   │   ├── incidents.py
│   │   │   ├── logs.py
│   │   │   ├── assets.py
│   │   │   ├── detection_rules.py
│   │   │   ├── threat_intel.py
│   │   │   ├── mitre.py
│   │   │   ├── reports.py
│   │   │   ├── simulation.py
│   │   │   ├── notifications.py
│   │   │   ├── audit_logs.py
│   │   │   ├── settings.py
│   │   │   └── __init__.py
│   │   ├── detector/      # Detection engine
│   │   │   ├── parser.py  # Log parsing
│   │   │   ├── rules.py   # Detection rules
│   │   │   └── risk.py    # Risk scoring
│   │   ├── models/        # SQLAlchemy models
│   │   ├── auth.py        # JWT authentication
│   │   ├── config.py      # Configuration
│   │   ├── database.py    # Database setup
│   │   └── main.py        # FastAPI application
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app/
│   │   ├── page.tsx       # Root redirect
│   │   ├── home/          # Public landing page
│   │   ├── login/         # Authentication
│   │   ├── signup/        # Registration
│   │   └── dashboard/     # Authenticated SOC dashboard
│   │       ├── layout.tsx # Sidebar + topbar
│   │       ├── page.tsx   # Dashboard overview
│   │       ├── alerts/    # Alert management
│   │       ├── incidents/ # Incident management
│   │       ├── logs/      # Log management
│   │       ├── assets/    # Asset tracking
│   │       ├── rules/     # Detection rule management
│   │       ├── mitre/     # MITRE ATT&CK mapping
│   │       ├── threat-intel/ # Threat intelligence
│   │       ├── reports/   # Report generation
│   │       ├── simulation/ # Attack simulation
│   │       └── settings/  # User settings
│   ├── lib/
│   │   ├── utils.ts       # API client, helpers
│   │   └── store.ts       # Zustand store
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── .env.example
```

---

## 🏃 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm

### Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Access

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

---

## 🐳 Docker Setup

```bash
# Copy environment variables
cp .env.example .env
# Edit .env with your settings

# Build and start
docker-compose up --build

# Or run in background
docker-compose up -d
```

---

## 📊 Detection Rules

The platform includes 10 built-in detection rules:

| Rule | Severity | MITRE | Description |
|------|----------|-------|-------------|
| SSH Brute Force | HIGH | T1110 | Detects repeated failed SSH logins |
| Port Scanning | MEDIUM | T1046 | Detects multi-port connection attempts |
| SQL Injection | CRITICAL | T1190 | Detects SQL injection patterns |
| XSS Attack | MEDIUM | T1189 | Detects cross-site scripting payloads |
| Command Injection | CRITICAL | T1059 | Detects OS command injection |
| Suspicious Authentication | HIGH | T1078 | Detects unusual login patterns |
| Malware Indicators | CRITICAL | T1059 | Detects known malware signatures |
| Suspicious Process | HIGH | T1059 | Detects suspicious process activity |
| Privilege Escalation | CRITICAL | T1068 | Detects privilege escalation attempts |
| Abnormal Network | MEDIUM | T1071 | Detects unusual network patterns |

---

## 🔒 Security

- JWT-based authentication with bcrypt password hashing
- Tenant isolation (organization-scoped data access)
- Role-based access control (Admin, Analyst, Viewer)
- CORS configuration
- Input validation via Pydantic
- API key authentication for programmatic access
- Audit logging for sensitive operations
- No secrets exposed to frontend

---

## 🧪 Attack Simulation

The platform includes a safe simulation mode for testing:

1. Navigate to **Attack Simulation** in the dashboard
2. Select an attack type (Brute Force, Port Scan, SQL Injection, etc.)
3. Click **Run Simulation**
4. Events are generated and processed through the detection pipeline
5. View generated alerts and investigate

⚠️ All simulations are controlled and safe. No real attacks are performed.

---

## 📖 API Documentation

Once the backend is running, visit:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/signup` | Create account |
| POST | `/api/auth/login` | Login |
| GET | `/api/dashboard/summary` | Dashboard data |
| GET | `/api/alerts` | List alerts |
| GET | `/api/incidents` | List incidents |
| POST | `/api/logs/upload` | Upload log files |
| POST | `/api/simulation/run` | Run attack simulation |
| GET | `/api/mitre/mapping` | MITRE ATT&CK mapping |
| GET | `/api/threat-intel/lookup` | IOC investigation |

---

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Frontend   │────▶│    Backend    │────▶│   Database   │
│  (Next.js)   │     │   (FastAPI)   │     │  (SQLite)    │
│   Port 3000  │     │   Port 8000   │     │              │
└─────────────┘     └──────┬───────┘     └─────────────┘
                           │
                    ┌──────▼───────┐
                    │   Detection   │
                    │    Engine     │
                    └──────────────┘
```

### Detection Pipeline

1. **Collect** — Ingest logs from files, APIs, or simulations
2. **Parse** — Extract structured fields from raw logs
3. **Detect** — Match events against detection rules
4. **Score** — Calculate risk scores and confidence
5. **Alert** — Generate severity-ranked alerts
6. **Correlate** — Link related alerts and events

---

## 📝 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `sqlite:///./data/app.db` |
| `JWT_SECRET` | Secret key for JWT tokens | Required |
| `CORS_ORIGINS` | Allowed CORS origins | `http://localhost:3000` |
| `ENVIRONMENT` | App environment | `development` |
| `NEXT_PUBLIC_API_URL` | Backend API URL for frontend | `http://localhost:8000` |

---

## 📄 License

MIT License © 2026 Niks Security

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to branch
5. Create a Pull Request

---

**Built with ❤️ for security teams everywhere.**
