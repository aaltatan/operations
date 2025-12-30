from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    db_url: str = "sqlite:///operations.sqlite3"

    debug: bool = True

    app_title: str = "Operations"
    app_description: str = "Operations API"
    app_version: str = "0.1.0"

    secret_key: str = ""
    jwt_algorithm: str = ""
    token_type: str = ""
    access_token_expires_minutes: int = 15

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_config() -> Config:
    return Config()
