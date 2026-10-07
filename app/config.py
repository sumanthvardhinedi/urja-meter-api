from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    urja_base_url: str
    urja_username: str
    urja_password: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()