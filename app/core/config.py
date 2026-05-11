from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "WMS Inventory API"
    app_env: str = "local"
    debug: bool = True
    telegram_bot_token: str | None = None
    telegram_webhook_secret: str = "change-me"
    telegram_webhook_path: str = "/api/v1/telegram/webhook"
    telegram_query_user_ids: str = ""
    telegram_operator_user_ids: str = ""
    telegram_admin_user_ids: str = ""
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"
    database_url: str = Field(
        default="postgresql+asyncpg://wms_user:wms_password@postgres:5432/wms",
        validation_alias="DATABASE_URL",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
