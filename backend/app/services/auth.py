from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from bcrypt import hashpw, gensalt, checkpw

from app.config import settings

def hash_password(password: str) -> str:
    return hashpw(password.encode(), gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return checkpw(password.encode(), hashed.encode())

def create_token(org_id: str) -> str:
    expiry = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expiry_minutes)
    return jwt.encode({"sub": org_id, "exp": expiry}, settings.jwt_secret, algorithm="HS256")

def decode_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
        return payload.get("sub")
    except JWTError:
        return None
