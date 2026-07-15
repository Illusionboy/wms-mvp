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
    # 安全库存公式 SS = Z * sigma_D * sqrt(L) 中的服务水平系数，默认对应 95% 不缺货概率
    safety_stock_z: float = Field(default=1.65, validation_alias="SAFETY_STOCK_Z")
    jwt_secret_key: str = Field(
        default="change-me-in-production",
        validation_alias="JWT_SECRET_KEY",
    )
    jwt_expire_days: int = 30
    # 乐天凭据加密密钥（对称加密 rakuten_credentials 里的密码）。任意字符串即可，
    # 后端会用 SHA-256 派生出合法的 Fernet 密钥。未设置时回退到 jwt_secret_key。
    rakuten_cred_key: str | None = Field(default=None, validation_alias="RAKUTEN_CRED_KEY")
    # 乐天自动下载定时（Mon–Sat 08:50 JST）总开关。仅在跑抓取的那台(VPS)设 true。
    rakuten_auto_enabled: bool = Field(default=False, validation_alias="RAKUTEN_AUTO_ENABLED")
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
