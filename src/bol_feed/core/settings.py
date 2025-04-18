from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    class Config:
        env_file = 'config.ini'

    database_host: str
    database_port: int
    database_user: str
    database_password: str
    database_name: str

    notify_email: str
    notify_categories: list[str]

    smtp_user: str
    smtp_password: str
    smtp_port: int
    smtp_host: str
    dkim_path: str | None
    dkim_selector: str | None

    feed_url: str


@lru_cache
def get_settings():
    # noinspection PyArgumentList
    return Settings()
