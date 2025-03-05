from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class RabbitmqSettings(BaseSettings):
    RABBITMQ_HOST: str | None = None
    RABBITMQ_PORT: int | None = None
    RABBITMQ_USER: str | None = None
    RABBITMQ_PASS: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache()
def get_rabbitmq_settings() -> RabbitmqSettings:
    return RabbitmqSettings()
