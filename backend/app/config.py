from typing import Set
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./watchtower.db"
    jwt_secret: str = "dev-secret-change-in-production"
    jwt_expiry_minutes: int = 1440
    allowed_origins: str = "*"

    @property
    def origins(self) -> list[str]:
        if self.allowed_origins == "*":
            return ["*"]
        return [o.strip() for o in self.allowed_origins.split(",")]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

settings = Settings()
