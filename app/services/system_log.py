"""通用系统异常/事件日志：负库存出库、预留冲突等非客户预留专属场景的统一记录。

`write_system_log` 供其它 service 在检测到异常时调用（库存不足、调整异常等），
`get_system_logs` 供「日志查看」页面查询展示。
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.models.system_log import SystemLog
from app.schemas.inventory import SystemLogRead


async def write_system_log(
    session: AsyncSession,
    category: str,
    message: str,
    *,
    level: str = "warning",
    jan_code: str | None = None,
    warehouse_name: str | None = None,
) -> None:
    session.add(SystemLog(
        category=category,
        level=level,
        message=message,
        jan_code=jan_code,
        warehouse_name=warehouse_name,
    ))
    await session.flush()


async def get_system_logs(
    session: AsyncSession,
    category: str | None = None,
    level: str | None = None,
    limit: int = 200,
) -> list[SystemLogRead]:
    """查询系统日志，按时间倒序。"""
    stmt = select(SystemLog)
    if category:
        stmt = stmt.where(SystemLog.category == category)
    if level:
        stmt = stmt.where(SystemLog.level == level)
    stmt = stmt.order_by(SystemLog.created_at.desc()).limit(limit)

    logs = (await session.scalars(stmt)).all()
    if not logs:
        return []

    jan_codes = list({log.jan_code for log in logs if log.jan_code})
    products_map: dict[str, str] = {}
    if jan_codes:
        for p in (await session.scalars(select(Product).where(Product.jan_code.in_(jan_codes)))).all():
            products_map[p.jan_code] = p.name_jp

    result = []
    for log in logs:
        r = SystemLogRead.model_validate(log)
        if log.jan_code:
            r.product_name = products_map.get(log.jan_code)
        result.append(r)
    return result
