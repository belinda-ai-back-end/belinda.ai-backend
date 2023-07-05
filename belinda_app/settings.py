import uuid
from functools import lru_cache

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    SESSION_SECRET_KEY: str = Field(default=str(uuid.uuid4()))
    CORS_ORIGINS: str = "*"


@lru_cache
def get_settings(**kwargs):
    return Settings(**kwargs)
