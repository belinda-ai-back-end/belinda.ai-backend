import uuid
from functools import lru_cache

from pydantic import BaseSettings, Field, SecretStr, validator


class Settings(BaseSettings):
    SESSION_SECRET_KEY: str = Field(default=str(uuid.uuid4()))
    CORS_ORIGINS: str = "*"

    ACCESS_TOKEN_EXPIRE_HOURS = 24

    POSTGRES_USER: str
    POSTGRES_PASSWORD: SecretStr
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_DB: str

    DATABASE_URI: str | None

    @validator("DATABASE_URI", pre=True)
    def validate_postgres_uri(cls, v: str, values: dict[str:str]) -> str:  # noqa: N805
        if isinstance(v, str):
            return v

        password: SecretStr = values.get("POSTGRES_PASSWORD", SecretStr(""))
        return (
            f'postgresql+asyncpg://{values.get("POSTGRES_USER")}:{password.get_secret_value()}'
            f'@{values.get("POSTGRES_HOST")}:{values.get("POSTGRES_PORT")}/{values.get("POSTGRES_DB")}'
        )

    class Config:
        env_file = "belinda_app/.env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings(**kwargs) -> Settings:
    return Settings(**kwargs)
