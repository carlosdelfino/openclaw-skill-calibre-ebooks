from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from pathlib import Path
from typing import Optional
import os


class Settings(BaseSettings):
    # Calibre OpenClaw Server
    CALIBRE_DB_PATH: str = Field(default="/mnt/Backup_2/Biblioteca/metadata.db")
    CALIBRE_LIBRARY_PATH: str = Field(default="/mnt/Backup_2/Biblioteca")
    SERVER_PORT: int = Field(default=6180)
    SERVER_HOST: str = Field(default="0.0.0.0")
    
    # Ollama
    OLLAMA_HOST: str = Field(default="http://localhost:11434")
    OLLAMA_MODEL: str = Field(default="nomic-embed-text-v2-moe:latest")
    
    # Embeddings
    CHUNK_SIZE: int = Field(default=500)
    CHUNK_OVERLAP: int = Field(default=50)
    SIMILARITY_THRESHOLD: float = Field(default=0.3)
    
    # PostgreSQL
    POSTGRESQL_DB_USER: str = Field(default="generativa")
    POSTGRESQL_DB_PASSWD: str = Field(default="")
    POSTGRESQL_DB_DATABASE: str = Field(default="rapport_biblioteca")
    POSTGRESQL_DB_HOST: str = Field(default="localhost")
    POSTGRESQL_DB_PORT: int = Field(default=5432)
    
    # Logs
    LOG_DIR: str = Field(default="/mnt/Backup_2/Biblioteca/logs")
    LOG_RETENTION_DAYS: int = Field(default=30)
    LOG_COMPRESS: bool = Field(default=True)
    
    @property
    def postgres_dsn(self) -> str:
        return f"postgresql://{self.POSTGRESQL_DB_USER}:{self.POSTGRESQL_DB_PASSWD}@{self.POSTGRESQL_DB_HOST}:{self.POSTGRESQL_DB_PORT}/{self.POSTGRESQL_DB_DATABASE}"
    
    @property
    def log_dir_path(self) -> Path:
        return Path(self.LOG_DIR)
    
    model_config = SettingsConfigDict(
        env_file=None,
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


def load_settings() -> Settings:
    """Load settings from .env file in multiple locations."""
    env_dir = os.environ.get("ENV_DIR")
    env_file = None
    
    if env_dir:
        env_file = Path(env_dir) / ".env"
        if not env_file.exists():
            env_file = None
    
    if not env_file:
        # Try current directory
        if Path(".env").exists():
            env_file = Path(".env")
    
    if env_file:
        return Settings(_env_file=str(env_file), _env_file_encoding="utf-8")
    return Settings()


settings = load_settings()
