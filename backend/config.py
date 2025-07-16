import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_VERSION: str = "v1"
    PROJECT_NAME: str = "Aid-al-Neo"
    API_KEY: str = os.getenv("API_KEY", "changeme")
    ADMIN_TOKEN: str = os.getenv("ADMIN_TOKEN", "adminchangeme")
    MODEL_CACHE_DIR: str = os.getenv("MODEL_CACHE_DIR", "./models/cache")
    LOG_DIR: str = os.getenv("LOG_DIR", "./logs")
    PARAMS_DIR: str = os.getenv("PARAMS_DIR", "./params")
    HF_TOKEN: str = os.getenv("HF_TOKEN", "")
    ENV: str = os.getenv("ENV", "development")

settings = Settings() 