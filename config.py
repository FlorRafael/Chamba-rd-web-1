import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "CHAMBA RD API"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://chamba_user:chamba_pass@localhost:5432/chambard"
    )
    SECRET_KEY: str = os.getenv("SECRET_KEY", "chamba_rd_super_secret_jwt_key_dominicana_2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "43200")) # 30 days
    DEFAULT_COMMISSION_RATE: float = float(os.getenv("DEFAULT_COMMISSION_RATE", "0.10")) # 10%
    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "admin@chambard.com")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "")
    CORS_ORIGINS: list[str] = ["*"]

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
