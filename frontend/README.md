# WatchTower Frontend

React SIEM dashboard.

## Setup

```bash
npm install
cp .env.example .env.local
```

Set `VITE_API_URL` and `VITE_WS_URL` in `.env.local`.

## Environment Variables

| Variable | Description | Example |
|---|---|---|
| `VITE_API_URL` | Backend API URL | `https://your-app-name.onrender.com` |
| `VITE_WS_URL` | WebSocket URL (same host, wss://) | `wss://your-app-name.onrender.com` |

## Run

```bash
npm run dev
```

## Build

```bash
npm run build
```

## Deploy to Vercel

1. Connect repo to Vercel
2. Set `VITE_API_URL` and `VITE_WS_URL` in Vercel dashboard
3. Vercel detects `vercel.json` automatically
