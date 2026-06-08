from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routers import auth_router, ingest_router, logs_router, alerts_router, stats_router, ws_router

app = FastAPI(title="WatchTower SIEM", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(ingest_router.router)
app.include_router(logs_router.router)
app.include_router(alerts_router.router)
app.include_router(stats_router.router)
app.include_router(ws_router.router)

@app.on_event("startup")
async def startup():
    await init_db()

@app.get("/health")
async def health():
    return {"status": "ok"}
