"""
Central configuration. Everything comes from environment variables so the
same code runs locally, in Docker, or wherever you deploy it later.

Set these in a .env file (never commit it) or your shell before running:
    DATABASE_URL=postgresql://user:password@localhost:5432/expensemind
    JWT_SECRET_KEY=some-long-random-string
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 1 day

    class Config:
        env_file = ".env"


settings = Settings()
