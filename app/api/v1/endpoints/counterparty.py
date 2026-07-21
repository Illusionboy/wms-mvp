"""秦丝供应商/客户缓存 + 简称匹配端点。

- POST /counterparty/sync?kind=supplier|customer  同步秦丝全量（admin）
- GET  /counterparty/search?kind=&q=              名称/发音/简称匹配，供微信报库下拉（只读）
- GET  /counterparty?kind=&q=                     管理页列表含简称（admin）
- POST /counterparty/{id}/alias                   加简称（admin）
- DELETE /counterparty/alias/{alias_id}           删简称（admin）
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import require_admin
from app.db.session import get_db_session
from app.models.qinsi_counterparty import QinsiCounterparty, QinsiCounterpartyAlias
from app.services.counterparty_match import canonical, search_counterparties, sync_counterparties

router = APIRouter()

_KIND = Query(..., pattern="^(supplier|customer)$")


class AliasRead(BaseModel):
    id: int
    alias: str
    model_config = {"from_attributes": True}


class CounterpartyRead(BaseModel):
    id: int
    kind: str
    qinsi_id: int
    name: str
    aliases: list[AliasRead] = []
    model_config = {"from_attributes": True}


class SearchHit(BaseModel):
    qinsi_id: int
    name: str
    kind: str
    score: int


class AliasCreate(BaseModel):
    alias: str


@router.post("/sync")
async def sync(
    kind: str = _KIND,
    session: AsyncSession = Depends(get_db_session),
    _=Depends(require_admin),
) -> dict:
    try:
        n = await sync_counterparties(session, kind)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"同步秦丝{kind}失败：{exc}（先确认秦丝会话有效）")
    return {"kind": kind, "count": n}


@router.get("/search", response_model=list[SearchHit])
async def search(
    kind: str = _KIND,
    q: str = Query(""),
    session: AsyncSession = Depends(get_db_session),
) -> list[SearchHit]:
    hits = await search_counterparties(session, kind, q)
    return [SearchHit(qinsi_id=cp.qinsi_id, name=cp.name, kind=cp.kind, score=s) for cp, s in hits]


@router.get("", response_model=list[CounterpartyRead])
async def list_counterparties(
    kind: str = _KIND,
    q: str = Query(""),
    session: AsyncSession = Depends(get_db_session),
    _=Depends(require_admin),
) -> list[CounterpartyRead]:
    rows = (await session.execute(
        select(QinsiCounterparty)
        .where(QinsiCounterparty.kind == kind)
        .options(selectinload(QinsiCounterparty.aliases))
        .order_by(QinsiCounterparty.name)
        .limit(1000)
    )).scalars().all()
    q = (q or "").strip()
    if q:
        qc = canonical(q)
        rows = [
            c for c in rows
            if (qc and qc in c.canonical) or q in c.name
            or any((qc and qc in a.canonical) for a in c.aliases)
        ]
    return [CounterpartyRead.model_validate(c) for c in rows]


@router.post("/{cp_id}/alias", response_model=CounterpartyRead)
async def add_alias(
    cp_id: int,
    payload: AliasCreate,
    session: AsyncSession = Depends(get_db_session),
    _=Depends(require_admin),
) -> CounterpartyRead:
    cp = await session.get(QinsiCounterparty, cp_id)
    if cp is None:
        raise HTTPException(status_code=404, detail="供应商/客户不存在")
    alias = (payload.alias or "").strip()
    if alias:
        session.add(QinsiCounterpartyAlias(counterparty_id=cp_id, alias=alias, canonical=canonical(alias)))
        await session.commit()
    cp = (await session.execute(
        select(QinsiCounterparty).where(QinsiCounterparty.id == cp_id)
        .options(selectinload(QinsiCounterparty.aliases))
    )).scalar_one()
    return CounterpartyRead.model_validate(cp)


@router.delete("/alias/{alias_id}")
async def del_alias(
    alias_id: int,
    session: AsyncSession = Depends(get_db_session),
    _=Depends(require_admin),
) -> dict:
    a = await session.get(QinsiCounterpartyAlias, alias_id)
    if a is not None:
        await session.delete(a)
        await session.commit()
    return {"ok": True}
