"""乐天店铺凭据 DTO。密码只写不读——读取时只回布尔"是否已设置"，绝不回明文/密文。"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RakutenCredentialUpsert(BaseModel):
    store: str = Field(..., min_length=1, max_length=16)          # 店铺标识，与 P1 mgmt 前缀一致（"1"/"2"）
    store_label: str | None = Field(default=None, max_length=64)  # 展示名，如"一号店"
    rms_login_id: str | None = None                              # RMS 登录账号
    rms_password: str | None = None                              # RMS 登录密码（留空=保持不变）
    member_email: str | None = None                             # 楽天会員 邮箱（session upgrade 登录）
    member_password: str | None = None                          # 楽天会員 密码（留空=保持不变）
    csv_user: str | None = None                                  # CSV 下载专用账号
    csv_password: str | None = None                             # CSV 下载专用密码（留空=保持不变）
    enabled: bool = True


class RakutenCredentialRead(BaseModel):
    id: int
    store: str
    store_label: str | None
    rms_login_id: str
    member_email: str
    csv_user: str
    has_rms_password: bool      # 是否已设置 RMS 密码（不回明文）
    has_member_password: bool   # 是否已设置 楽天会員 密码
    has_csv_password: bool      # 是否已设置 CSV 密码
    enabled: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
