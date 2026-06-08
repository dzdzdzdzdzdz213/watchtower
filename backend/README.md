# WatchTower Backend

SIEM platform backend — FastAPI async + SQLAlchemy 2.0 + PostgreSQL/SQLite.

**Live API**: https://watchtower-backend-5d3x.onrender.com  
**Swagger Docs**: https://watchtower-backend-5d3x.onrender.com/docs

## Setup

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env  # edit DATABASE_URL
```

## Run

```bash
uvicorn app.main:app --reload
```

## Seed Data

```bash
python seed.py
```

Login: demo@watchtower.dev / demo1234

## Send a Test Log

```bash
curl -X POST https://watchtower-backend-5d3x.onrender.com/ingest/00000000-0000-0000-0000-000000000001 \
  -H "Content-Type: application/json" \
  -d '{"logs": ["Jun  8 10:00:00 server sshd[1234]: Failed password for root from 10.0.0.1 port 22 ssh2"]}'
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite+aiosqlite:///./watchtower.db` | Database connection string |
| `JWT_SECRET` | `dev-secret-change-in-production` | Secret key for JWT signing |
| `JWT_EXPIRY_MINUTES` | `1440` | JWT token expiry in minutes |
