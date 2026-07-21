"""秦丝供应商/客户：同步缓存 + 名称智能匹配（简繁 / 日文发音 / 拼音 / 简称）。

- canonical(): NFKC + 繁→简(zhconv) + 去公司后缀/标点噪音 → 归一化名，简繁互匹配的关键
- reading():   日文汉字→假名→罗马音(pykakasi) + 中文拼音(pypinyin) → 按发音匹配
- sync_counterparties(): 从秦丝分页拉全量 supplier/customer 上载缓存
- search_counterparties(): 内存打分排序，返回候选（数据量小，全量载入即可）
"""
from __future__ import annotations

import unicodedata

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from zhconv import convert as _zh_convert

from app.models.qinsi_counterparty import QinsiCounterparty
from app.scrapers.qinsi_backfill import _QS_API_HEADERS, _QS_BASE, _load_cookie_dict

# 公司后缀/常见噪音（归一化时剥掉，小写比对）
_NOISE = [
    "株式会社", "有限会社", "合同会社", "合资会社", "合資会社", "（株）", "(株)", "㈱", "㈲",
    "（有）", "(有)", "股份有限公司", "有限公司", "有限责任公司", "公司",
    "co.,ltd.", "co.,ltd", "co., ltd.", "co., ltd", "ltd.", "ltd", "inc.", "inc", "co.",
]
_STRIP_CHARS = set(" \t　・·,，.。、-—_/\\|()（）[]【】{}«»<>\"'`")

_kks = None


def _kakasi():
    global _kks
    if _kks is None:
        from pykakasi import kakasi
        _kks = kakasi()
    return _kks


def canonical(name: str | None) -> str:
    """归一化名：全半角统一 + 繁转简 + 去公司后缀/标点。简繁输入据此互相匹配。"""
    s = unicodedata.normalize("NFKC", name or "").strip().lower()
    try:
        s = _zh_convert(s, "zh-hans")
    except Exception:
        pass
    for n in _NOISE:
        s = s.replace(n.lower(), "")
    return "".join(ch for ch in s if ch not in _STRIP_CHARS)


def reading(name: str | None) -> str:
    """发音串：日文罗马音(pykakasi hepburn) + 中文拼音(pypinyin)，空格分隔。按读音匹配用。"""
    s = unicodedata.normalize("NFKC", name or "").strip()
    if not s:
        return ""
    jp = ""
    try:
        jp = "".join(seg.get("hepburn", "") for seg in _kakasi().convert(s)).lower()
    except Exception:
        pass
    zh = ""
    try:
        from pypinyin import lazy_pinyin
        zh = "".join(lazy_pinyin(s)).lower()
    except Exception:
        pass
    return f"{jp} {zh}".strip()


# ── 同步 ─────────────────────────────────────────────────────────────────────
# 秦丝下拉数据源（POST，空 searchKey 分页拉全量）
_SRC = {
    "customer": ("/gis/admin/inner/client/clientSelectJSON.ac", {"showDisable": 1}),
    "supplier": ("/gis/admin/inner/supplier/supplierSelectJSON.ac", {}),
}
_SKIP_NAMES = {"-请选择-", "-全部-", ""}


def _extract(o: dict) -> tuple[int | None, str]:
    qid = o.get("val") if o.get("val") not in (None, "") else o.get("id")
    name = o.get("text") or o.get("supplierName") or o.get("clientName") or o.get("name") or ""
    try:
        return (int(qid) if qid not in (None, "") else None), str(name).strip()
    except (TypeError, ValueError):
        return None, str(name).strip()


async def sync_counterparties(session: AsyncSession, kind: str) -> int:
    """从秦丝拉取 kind(supplier/customer) 全量，upsert 进缓存。返回条数。"""
    if kind not in _SRC:
        raise ValueError(f"未知 kind: {kind}")
    path, extra = _SRC[kind]
    cookies = _load_cookie_dict()
    seen: dict[int, str] = {}
    async with httpx.AsyncClient(cookies=cookies, headers=_QS_API_HEADERS, timeout=30) as client:
        page = 1
        while page <= 500:  # 安全上限
            r = await client.post(_QS_BASE + path, params={**extra, "page": page, "searchKey": ""})
            j = r.json()
            ol = j.get("optionList") or []
            for o in ol:
                qid, name = _extract(o)
                if qid and name and name not in _SKIP_NAMES:
                    seen[qid] = name
            total = j.get("totalPage") or 1
            if page >= total or not ol:
                break
            page += 1

    existing = {
        c.qinsi_id: c
        for c in (await session.execute(
            select(QinsiCounterparty).where(QinsiCounterparty.kind == kind)
        )).scalars()
    }
    for qid, name in seen.items():
        canon, read = canonical(name), reading(name)
        c = existing.get(qid)
        if c is not None:
            c.name, c.canonical, c.reading, c.active = name, canon, read, True
        else:
            session.add(QinsiCounterparty(
                kind=kind, qinsi_id=qid, name=name, canonical=canon, reading=read, active=True,
            ))
    await session.commit()
    return len(seen)


# ── 匹配 ─────────────────────────────────────────────────────────────────────
def _score(qc: str, qr_tokens: list[str], cp_canon: str, cp_reading: str, alias_canons: list[str]) -> int:
    if not qc:
        return 0
    if qc == cp_canon or qc in alias_canons:
        return 100
    if qc in cp_canon:
        return 85 if cp_canon.startswith(qc) else 65
    for ac in alias_canons:
        if ac and qc in ac:
            return 75 if ac.startswith(qc) else 60
    for t in qr_tokens:
        if len(t) >= 2 and t in cp_reading:
            return 40
    return 0


async def search_counterparties(
    session: AsyncSession, kind: str, query: str, limit: int = 20
) -> list[tuple[QinsiCounterparty, int]]:
    """按名称/发音/简称匹配，返回 [(counterparty, score)]，分数高在前。"""
    query = (query or "").strip()
    if not query:
        return []
    qc = canonical(query)
    qr_tokens = [t for t in reading(query).split() if len(t) >= 2]
    rows = (await session.execute(
        select(QinsiCounterparty)
        .where(QinsiCounterparty.kind == kind, QinsiCounterparty.active.is_(True))
        .options(selectinload(QinsiCounterparty.aliases))
    )).scalars().all()

    scored: list[tuple[QinsiCounterparty, int]] = []
    for cp in rows:
        s = _score(qc, qr_tokens, cp.canonical, cp.reading, [a.canonical for a in cp.aliases])
        if s > 0:
            scored.append((cp, s))
    scored.sort(key=lambda x: (-x[1], len(x[0].canonical or "")))
    return scored[:limit]
