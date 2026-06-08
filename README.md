<div align="center">
  <img src="https://img.shields.io/badge/status-live-3b82f6" alt="Status">
  <img src="https://img.shields.io/badge/python-3.14-blue" alt="Python">
  <img src="https://img.shields.io/badge/react-18-61dafb" alt="React">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
</div>

<br />

<div align="center">
  <h1>WatchTower SIEM</h1>
  <p><strong>Open-source log intelligence and threat detection platform</strong></p>
  <p>
    <a href="https://frontend-alpha-rose-69.vercel.app" target="_blank">Live Demo</a> ·
    <a href="#features">Features</a> ·
    <a href="#architecture">Architecture</a> ·
    <a href="#deployment">Deployment</a> ·
    <a href="#api">API</a>
  </p>
  <br />
  <p>
    <code>https://frontend-alpha-rose-69.vercel.app</code><br />
    <code>https://watchtower-backend-5d3x.onrender.com</code><br />
    <em>Demo: demo@watchtower.dev / demo1234</em>
  </p>
</div>

---

## Overview

WatchTower ingests, parses, and analyzes security logs in real time. It supports SSH auth logs, Nginx access logs, JSON payloads, and generic syslog — no configuration required. A detection engine with 7 built-in rules scans every event and generates alerts that stream live to the dashboard via WebSocket.

Built with Python 3.14 + FastAPI async backend and React 18 + Recharts frontend.

---

## Features

- **Log Ingestion** — REST API accepts up to 1,000 logs per request. Auto-detects SSH, Nginx, JSON, and syslog formats.
- **Threat Detection** — 7 rules: SSH brute force, port scan, SQL injection, off-hours login, mass failed logins, admin enumeration, path enumeration.
- **Alert Deduplication** — Sliding 5-minute window prevents alert storms for repeated attacks from the same IP.
- **Live Dashboard** — Real-time WebSocket feed, hourly event timeline, severity breakdown, top source IPs.
- **Multi-tenant** — Organization isolation with per-org API keys and JWT authentication.
- **Dark-themed UI** — Professional SIEM interface built with TailwindCSS and Recharts.

---

## Architecture

```
┌──────────────┐     ┌──────────────────┐     ┌────────────┐
│  Vercel SPA  │────▶│  Render Backend  │────▶│ PostgreSQL │
│  (React 18)  │     │  (FastAPI async) │     │  or SQLite │
│   Recharts   │◀────│ WebSocket / REST │◀────│  (aiosqlite)│
└──────────────┘     └──────────────────┘     └────────────┘
```

### Backend Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI 0.136 |
| ORM | SQLAlchemy 2.0 async |
| Auth | JWT (python-jose) + bcrypt |
| Database | PostgreSQL (asyncpg) / SQLite (aiosqlite) |
| Deployment | Render (free tier) |

### Frontend Stack

| Layer | Technology |
|-------|-----------|
| Framework | React 18 + Vite |
| Routing | React Router v6 |
| State | TanStack Query |
| Charts | Recharts |
| Icons | Lucide React |
| Styling | TailwindCSS 3 |
| Deployment | Vercel |

---

## Detection Rules

| Rule | Severity | Description |
|------|----------|-------------|
| `brute_force_ssh` | Critical | >5 failed SSH attempts from same IP in 60s |
| `port_scan` | Critical | >10 connection attempts to >5 ports in 30s |
| `sql_injection` | Critical | SQL pattern matched in HTTP request path/body |
| `off_hours_login` | Warning | Successful SSH login between 00:00-06:00 UTC |
| `mass_failed_logins` | Warning | >20 total failed logins in 60s |
| `admin_enumeration` | Warning | Access attempt to known sensitive paths |
| `path_enumeration` | Warning | >15 404 responses from same IP in 60s |

---

## Deployment

### Live URLs

| Service | URL |
|---------|-----|
| Frontend | https://frontend-alpha-rose-69.vercel.app |
| Backend API | https://watchtower-backend-5d3x.onrender.com |
| API Docs (Swagger) | https://watchtower-backend-5d3x.onrender.com/docs |

### Demo Credentials

```
Email:    demo@watchtower.dev
Password: demo1234
```

### Quick Start (Local)

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

### Seed Data

```bash
cd backend
python seed.py
```

### Send a Test Log

```bash
curl -X POST https://watchtower-backend-5d3x.onrender.com/ingest/00000000-0000-0000-0000-000000000001 \
  -H "Content-Type: application/json" \
  -d '{"logs": ["Jun  8 10:00:00 server sshd[1234]: Failed password for root from 10.0.0.1 port 22 ssh2"]}'
```

---

## API

### Auth

| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/register` | Register a new organization |
| POST | `/auth/login` | Login and receive JWT |

### Logs

| Method | Path | Description |
|--------|------|-------------|
| POST | `/ingest/{api_key}` | Ingest log lines (max 1,000) |
| GET | `/logs` | Query ingested logs (paginated) |

### Alerts

| Method | Path | Description |
|--------|------|-------------|
| GET | `/alerts` | List alerts (filterable by status/severity) |
| PATCH | `/alerts/{id}` | Acknowledge or resolve an alert |

### Stats

| Method | Path | Description |
|--------|------|-------------|
| GET | `/stats` | Dashboard statistics (24h window) |

### WebSocket

| Path | Description |
|------|-------------|
| `wss://watchtower-backend-5d3x.onrender.com/ws/{api_key}` | Real-time alert feed |

---

## Environment Variables

### Backend (.env)

```
DATABASE_URL=sqlite+aiosqlite:///./watchtower.db
JWT_SECRET=dev-secret-change-in-production
JWT_EXPIRY_MINUTES=1440
```

For PostgreSQL (production):

```
DATABASE_URL=postgresql+asyncpg://user:pass@your-neon-host/db
```

### Frontend (Vercel env)

```
VITE_API_URL=https://watchtower-backend-5d3x.onrender.com
```

---

## Local Development

```bash
# Clone
git clone https://github.com/dzdzdzdzdzdz213/watchtower.git
cd watchtower

# Backend (runs on :8000)
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend (runs on :3000, proxies /api to :8000)
cd frontend
npm install
npm run dev
```

---

## License

MIT
