from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
from typing import List
class Settings(BaseSettings):
    environment: str = "development"
    jwt_secret: SecretStr = SecretStr("supersecretdefensekey_change_in_prod")
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/aegis"
    qdrant_url: str = "http://localhost:6333"
    ollama_url: str = "http://localhost:11434"
    cors_origins: List[str] = ["http://localhost:3000"]
    MAX_WS_CONNECTIONS: int = 1000
    GPS_JAMMED_NOISE_SIGMA: float = 50.0
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
settings = Settings()
