<div align="center">

# WatchTower SIEM

**Open-source SIEM platform for log ingestion and threat detection**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Language: Python](https://img.shields.io/badge/Language-Python-3776AB.svg)]()
[![Stars](https://img.shields.io/github/stars/dzdzdzdzdzdz213/watchtower-siem?style=social)]()
[![Status: Active](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()

</div>

---

## Overview

WatchTower SIEM is a full-stack security information and event management platform that ingests structured logs from multiple sources, applies deterministic detection rules, and presents correlated alerts through a real-time dashboard. It supports four common log formats out of the box, ships seven built-in detection rules with automatic alert deduplication, and streams updates to the frontend over WebSocket connections.

**[Live Demo](https://frontend-alpha-rose-69.vercel.app)**

## Features

- **4 Ingestion Formats** -- Native parsers for Apache, Nginx, syslog, and JSON log formats
- **7 Detection Rules** -- SSH brute-force, SQL injection, port scanning, unauthorized access, privilege escalation, anomalous outbound traffic, and configuration drift
- **Alert Deduplication** -- Automatically merges repeat alerts within a configurable time window to reduce noise
- **WebSocket Streaming** -- Pushes alerts and status updates to connected dashboard clients in real time
- **React 18 Dashboard** -- Interactive charts, filterable alert tables, and severity-based color coding
- **PostgreSQL Persistence** -- Durable storage for events, alerts, and rule definitions with full query support

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        Data Sources                          │
│                                                              │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│   │  Apache  │  │  Nginx   │  │  Syslog  │  │  JSON    │    │
│   │  Logs    │  │  Logs    │  │  Servers │  │  Events  │    │
│   └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘    │
│        │             │             │             │           │
│────────┼─────────────┼─────────────┼─────────────┼───────────│
│        │             │             │             │           │
│   ┌────┴─────────────┴─────────────┴─────────────┴────────┐  │
│   │              FastAPI Ingestion Layer                  │  │
│   │              POST /api/v1/events                      │  │
│   └────────────────────────┬──────────────────────────────┘  │
│                            │                                 │
│   ┌────────────────────────┴──────────────────────────────┐  │
│   │              Detection Engine (7 Rules)               │  │
│   │  brute_force | sqli | port_scan | privesc | ...      │  │
│   └────────────────────────┬──────────────────────────────┘  │
│                            │                                 │
│   ┌────────────────────────┴──────────────────────────────┐  │
│   │              PostgreSQL + Dedup                       │  │
│   └────────────────────────┬──────────────────────────────┘  │
│                            │                                 │
│            ┌───────────────┼───────────────┐                 │
│            │               │               │                 │
│   ┌────────┴─────┐  ┌──────┴──────┐  ┌─────┴──────────┐     │
│   │  REST API    │  │  WebSocket  │  │  React 18      │     │
│   │  /api/v1/*   │  │  /ws/alerts │  │  Dashboard     │     │
│   └──────────────┘  └─────────────┘  └────────────────┘     │
└──────────────────────────────────────────────────────────────┘
```

## Quick Start

```bash
# Clone the repository
git clone https://github.com/dzdzdzdzdzdz213/watchtower-siem.git
cd watchtower-siem

# Start the backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Start the frontend
cd ../frontend
npm install
npm run dev
```

Open `http://localhost:3000` to access the dashboard. The API is available at `http://localhost:8000`.

## Tech Stack

| Component        | Technology          | Purpose                          |
|------------------|---------------------|----------------------------------|
| API Server       | FastAPI             | Log ingestion and query API      |
| Database         | PostgreSQL          | Event and alert persistence      |
| Real-Time Push   | WebSocket           | Live alert streaming             |
| Frontend         | React 18            | Dashboard and visualization      |
| Styling          | TailwindCSS         | Responsive UI components         |
| Charts           | Recharts            | Alert trend and severity graphs  |
| Detection Engine | Python              | Rule evaluation and correlation  |
| Alert Dedup      | Python / Redis      | Time-window deduplication        |

## License

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This project is licensed under the MIT License.
