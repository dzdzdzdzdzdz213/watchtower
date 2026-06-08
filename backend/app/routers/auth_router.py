from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr

from app.database import get_db
from app.models import Organization
from app.services.auth import hash_password, verify_password, create_token, decode_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@router.post("/register", status_code=201)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Organization).where(Organization.email == req.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    org = Organization(
        name=req.name,
        email=req.email,
        password_hash=hash_password(req.password),
    )
    db.add(org)
    await db.commit()
    await db.refresh(org)
    token = create_token(str(org.id))
    return {"token": token, "org": {"id": str(org.id), "name": org.name, "email": org.email, "api_key": str(org.api_key), "plan": org.plan}}

import os

DEV_EMAIL = os.getenv("DEV_EMAIL", "demo@watchtower.dev")
DEV_PASS = os.getenv("DEV_PASS", "demo1234")
DEV_API_KEY = os.getenv("DEV_API_KEY", "00000000-0000-0000-0000-000000000001")

@router.post("/login")
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    # Dev mode: no DB needed for demo credentials
    if req.email == DEV_EMAIL and req.password == DEV_PASS:
        token = create_token(DEV_EMAIL)
        return {"token": token, "org": {"id": DEV_EMAIL, "name": "DemoCorp", "email": DEV_EMAIL, "api_key": DEV_API_KEY, "plan": "free"}}
    try:
        result = await db.execute(select(Organization).where(Organization.email == req.email))
        org = result.scalar_one_or_none()
        if org and verify_password(req.password, org.password_hash):
            token = create_token(str(org.id))
            return {"token": token, "org": {"id": str(org.id), "name": org.name, "email": org.email, "api_key": str(org.api_key), "plan": org.plan}}
    except Exception:
        pass
    raise HTTPException(status_code=401, detail="Invalid email or password")

class MockOrg:
    def __init__(self):
        self.id = DEV_EMAIL
        self.name = "DemoCorp"
        self.email = DEV_EMAIL
        self.api_key = DEV_API_KEY
        self.plan = "free"

mock_org = MockOrg()

async def get_current_org(credentials: HTTPAuthorizationCredentials = Depends(security), db: AsyncSession = Depends(get_db)) -> Organization:
    org_id = decode_token(credentials.credentials)
    if not org_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    if org_id == DEV_EMAIL:
        return mock_org
    try:
        result = await db.execute(select(Organization).where(Organization.id == org_id))
        org = result.scalar_one_or_none()
        if not org:
            raise HTTPException(status_code=401, detail="Organization not found")
        return org
    except Exception:
        raise HTTPException(status_code=401, detail="Organization not found")
