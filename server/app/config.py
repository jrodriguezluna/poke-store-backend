from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    db_host: str
    db_port: int = 3306
    db_user: str
    db_password: str
    db_name: str = "pokestore"
    upload_dir: str = "uploads"
    max_upload_bytes: int = 2 * 1024 * 1024
    cors_origins: str = "http://localhost:5173"


settings = Settings()
