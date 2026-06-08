# WatchTower Frontend

SIEM dashboard — React 18 + Vite + TailwindCSS + Recharts.

**Live**: https://frontend-alpha-rose-69.vercel.app

## Setup

```bash
npm install
```

## Dev

```bash
npm run dev
```

Proxies `/api` to `http://localhost:8000`. Set `VITE_API_URL` for production.

## Build

```bash
npm run build
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `VITE_API_URL` | Yes (prod) | Backend API URL (https://watchtower-backend-5d3x.onrender.com) |
