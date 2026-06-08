from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./watchtower.db"
    jwt_secret: str = "dev-secret-change-in-production"
    jwt_expiry_minutes: int = 1440

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

settings = Settings()
