from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str
    llm_provider: str = "fake"
    llm_timeout_seconds: int = 15
    openai_api_key: str | None = None


settings = Settings()
