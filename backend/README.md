# WatchTower Backend

SIEM platform backend — FastAPI + PostgreSQL.

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
curl -X POST http://localhost:8000/ingest/00000000-0000-0000-0000-000000000001 \
  -H "Content-Type: application/json" \
  -d '{"logs": ["Jun  8 10:00:00 server sshd[1234]: Failed password for root from 10.0.0.1 port 22 ssh2"]}'
```

## Deploy to Render

1. Push the backend folder to a GitHub repository
2. Go to [render.com](https://render.com) and create a new Web Service
3. Connect the GitHub repository
4. Render auto-detects the `render.yaml` and fills build and start commands
5. Add the following environment variables manually in the Render dashboard:
   - **DATABASE_URL** — from Neon: go to [neon.tech](https://neon.tech), create a project, copy the connection string, replace `postgresql://` with `postgresql+asyncpg://`
   - **SECRET_KEY** — generate with: `openssl rand -hex 32`
   - **ALGORITHM** — set to `HS256`
   - **ACCESS_TOKEN_EXPIRE_MINUTES** — set to `1440`
   - **ALLOWED_ORIGINS** — your Vercel frontend URL after deploying
6. Deploy the service
