import json
from typing import Any

from pydantic import Field, field_validator
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
    # Maps 秦丝 warehouse names → WMS warehouse names.
    # Set via QINSI_WAREHOUSE_MAP env var as a JSON string, e.g.:
    #   QINSI_WAREHOUSE_MAP={"北津守仓库":"普通仓库","乐天仓库":"乐天仓库"}
    # Any type prevents pydantic-settings from JSON-parsing the env var itself;
    # the field_validator below handles all parsing so empty/invalid values degrade gracefully.
    qinsi_warehouse_map: Any = Field(default_factory=dict)

    @field_validator("qinsi_warehouse_map", mode="before")
    @classmethod
    def _parse_warehouse_map(cls, v: object) -> dict[str, str]:
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return {}
            return json.loads(v)
        if isinstance(v, dict):
            return v
        return {}

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
