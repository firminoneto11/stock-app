from .base import BaseSettings


class Settings(BaseSettings):
    ENVIRONMENT = "development"
    DATABASE_URL = "sqlite+aiosqlite:///./database.db"
    DEBUG = True
    HOST = "127.0.0.1"
    PORT = 8000
