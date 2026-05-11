from app.db.base import Base
from app.db.session import engine
from app import models as _models
from sqlalchemy import text


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS units_per_case INTEGER"))
        await conn.execute(
            text(
                "ALTER TABLE products ADD COLUMN IF NOT EXISTS "
                "low_stock_alert_sent BOOLEAN NOT NULL DEFAULT FALSE"
            )
        )
        await conn.execute(text("ALTER TABLE stock_transactions ADD COLUMN IF NOT EXISTS reference_id VARCHAR(64)"))
        await conn.execute(text("ALTER TABLE stock_transactions ADD COLUMN IF NOT EXISTS note TEXT"))
