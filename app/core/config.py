from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "WMS Inventory API"
    app_env: str = "local"
    debug: bool = False
    api_key: str | None = None  # Required for all mutation endpoints; set via API_KEY env var
    telegram_bot_token: str | None = None
    telegram_webhook_secret: str = "change-me"
    telegram_webhook_path: str = "/api/v1/telegram/webhook"
    telegram_query_user_ids: str = ""
    telegram_operator_user_ids: str = ""
    telegram_admin_user_ids: str = ""
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"
    jwt_secret_key: str = Field(
        default="change-me-in-production",
        validation_alias="JWT_SECRET_KEY",
    )
    jwt_expire_days: int = 30
    admin_username: str | None = Field(default=None, validation_alias="ADMIN_USERNAME")
    admin_password: str | None = Field(default=None, validation_alias="ADMIN_PASSWORD")
    # 秦丝生意通爬虫配置
    qinsi_username: str | None = Field(default=None, validation_alias="QINSI_USERNAME")
    qinsi_password: str | None = Field(default=None, validation_alias="QINSI_PASSWORD")
    qinsi_base_url: str = Field(
        default="https://web.syt.qinsilk.com/gis/admin/",
        validation_alias="QINSI_BASE_URL",
    )
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
