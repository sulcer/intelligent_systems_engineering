import pathlib
from pydantic import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    __project_root = pathlib.Path(__file__).resolve().parent.parent

    model_config = SettingsConfigDict(env_file=str(__project_root / ".env"))


settings = Settings()

