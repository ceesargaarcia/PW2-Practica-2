from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./desert_vault.db"
    jwt_secret: str = "changeme_secret"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440  # 24h

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
