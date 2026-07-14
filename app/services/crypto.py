"""对称加密辅助：用于把敏感凭据（乐天 RMS / CSV 下载密码）加密后存库。

密钥来自 `settings.rakuten_cred_key`（env `RAKUTEN_CRED_KEY`），未设置时回退到 `jwt_secret_key`。
用户可填任意字符串，这里用 SHA-256 派生出合法的 32 字节 Fernet 密钥——所以换密钥会导致旧密文
无法解密（需重新在设置页填一次密码）。**密文只进 DB，明文只在调用抓取时临时解出，绝不返回前端。**
"""
from __future__ import annotations

import base64
import hashlib
from functools import lru_cache

from cryptography.fernet import Fernet, InvalidToken

from app.core.config import settings


@lru_cache(maxsize=1)
def _fernet() -> Fernet:
    raw = settings.rakuten_cred_key or settings.jwt_secret_key or "change-me-in-production"
    key = base64.urlsafe_b64encode(hashlib.sha256(raw.encode("utf-8")).digest())
    return Fernet(key)


def encrypt(plaintext: str) -> str:
    """加密明文 → base64 密文字符串。空串原样返回（表示"未设置"）。"""
    if not plaintext:
        return ""
    return _fernet().encrypt(plaintext.encode("utf-8")).decode("ascii")


def decrypt(token: str) -> str:
    """解密密文 → 明文。空串或密钥不匹配/损坏时返回空串（调用方据此判定凭据缺失）。"""
    if not token:
        return ""
    try:
        return _fernet().decrypt(token.encode("ascii")).decode("utf-8")
    except (InvalidToken, ValueError):
        return ""
