from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    db_url: str = ""

    debug: bool = True

    app_title: str = ""
    app_description: str = ""
    app_version: str = ""

    secret_key: str = ""
    jwt_algorithm: str = ""
    access_token_expires_minutes: int = 15
    token_type: str = ""

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_config() -> Config:
    return Config()
