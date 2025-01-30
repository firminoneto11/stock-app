from shared.utils import get_env

from .base import BaseSettings

with get_env().prefixed(BaseSettings.ENVIRONMENT_PREFIX) as env:

    class Settings(BaseSettings):
        ENVIRONMENT = "production"
        DATABASE_URL = env.str("DATABASE_URL")
        DEBUG = False
        HOST = "0.0.0.0"
        PORT = 8000
