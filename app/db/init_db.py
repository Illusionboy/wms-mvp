from sqlalchemy import select, text

from app.core.config import settings
from app.db.base import Base
from app.db.session import AsyncSessionLocal, engine
from app import models as _models


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
        await conn.execute(text(
            "ALTER TABLE warehouses ADD COLUMN IF NOT EXISTS "
            "allow_negative_stock BOOLEAN NOT NULL DEFAULT FALSE"
        ))
        await conn.execute(text(
            "ALTER TABLE stock_transactions ADD COLUMN IF NOT EXISTS transaction_date DATE"
        ))
        # Drop the non-negative check constraint — negative stock is a valid state
        # for warehouses with allow_negative_stock=True (e.g. during month-end count gap)
        await conn.execute(text(
            "ALTER TABLE inventory_records DROP CONSTRAINT IF EXISTS "
            "ck_inventory_records_quantity_non_negative"
        ))
        await conn.execute(text(
            "ALTER TABLE stock_transactions ADD COLUMN IF NOT EXISTS "
            "user_id INTEGER REFERENCES users(id) ON DELETE SET NULL"
        ))
        await conn.execute(text(
            "ALTER TABLE stock_transactions ADD COLUMN IF NOT EXISTS supplier VARCHAR(255)"
        ))
        await conn.execute(text(
            "ALTER TABLE stock_transactions ADD COLUMN IF NOT EXISTS customer VARCHAR(255)"
        ))
        await conn.execute(text(
            "ALTER TABLE products ADD COLUMN IF NOT EXISTS outer_jan VARCHAR(13)"
        ))
        # Partial unique index: prevents duplicate batch transactions at the DB level.
        # NULL reference_id (manual web_ui entries) is excluded by the WHERE clause.
        await conn.execute(text("""
            CREATE UNIQUE INDEX IF NOT EXISTS uq_stock_tx_source_ref
              ON stock_transactions(source, reference_id)
              WHERE reference_id IS NOT NULL
        """))
        # telegram_allowed_users is created by create_all via the model import;
        # the unique index is also declared there.

        # Harden FK ON DELETE actions: CASCADE/SET NULL → RESTRICT to protect the audit trail.
        # The DO block uses pg_constraint.confdeltype ('c'=CASCADE, 'n'=SET NULL) so it only
        # runs the ALTER when the old rule is still in place — fully idempotent on re-runs.
        await conn.execute(text("""
            DO $$
            DECLARE v_name text;
            BEGIN
                -- stock_transactions.inventory_record_id: CASCADE → RESTRICT
                SELECT c.conname INTO v_name
                FROM pg_constraint c
                JOIN pg_class t ON c.conrelid = t.oid
                JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = c.conkey[1]
                WHERE t.relname = 'stock_transactions'
                  AND a.attname = 'inventory_record_id'
                  AND c.contype = 'f' AND c.confdeltype = 'c';
                IF v_name IS NOT NULL THEN
                    EXECUTE 'ALTER TABLE stock_transactions DROP CONSTRAINT ' || quote_ident(v_name);
                    EXECUTE 'ALTER TABLE stock_transactions ADD CONSTRAINT ' || quote_ident(v_name) ||
                        ' FOREIGN KEY (inventory_record_id) REFERENCES inventory_records(id) ON DELETE RESTRICT';
                END IF;

                -- inventory_records.product_jan: CASCADE → RESTRICT
                SELECT c.conname INTO v_name
                FROM pg_constraint c
                JOIN pg_class t ON c.conrelid = t.oid
                JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = c.conkey[1]
                WHERE t.relname = 'inventory_records'
                  AND a.attname = 'product_jan'
                  AND c.contype = 'f' AND c.confdeltype = 'c';
                IF v_name IS NOT NULL THEN
                    EXECUTE 'ALTER TABLE inventory_records DROP CONSTRAINT ' || quote_ident(v_name);
                    EXECUTE 'ALTER TABLE inventory_records ADD CONSTRAINT ' || quote_ident(v_name) ||
                        ' FOREIGN KEY (product_jan) REFERENCES products(jan_code) ON DELETE RESTRICT';
                END IF;

                -- inventory_records.warehouse_id: CASCADE → RESTRICT
                SELECT c.conname INTO v_name
                FROM pg_constraint c
                JOIN pg_class t ON c.conrelid = t.oid
                JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = c.conkey[1]
                WHERE t.relname = 'inventory_records'
                  AND a.attname = 'warehouse_id'
                  AND c.contype = 'f' AND c.confdeltype = 'c';
                IF v_name IS NOT NULL THEN
                    EXECUTE 'ALTER TABLE inventory_records DROP CONSTRAINT ' || quote_ident(v_name);
                    EXECUTE 'ALTER TABLE inventory_records ADD CONSTRAINT ' || quote_ident(v_name) ||
                        ' FOREIGN KEY (warehouse_id) REFERENCES warehouses(id) ON DELETE RESTRICT';
                END IF;

                -- inventory_records.customer_id: SET NULL → RESTRICT
                SELECT c.conname INTO v_name
                FROM pg_constraint c
                JOIN pg_class t ON c.conrelid = t.oid
                JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = c.conkey[1]
                WHERE t.relname = 'inventory_records'
                  AND a.attname = 'customer_id'
                  AND c.contype = 'f' AND c.confdeltype = 'n';
                IF v_name IS NOT NULL THEN
                    EXECUTE 'ALTER TABLE inventory_records DROP CONSTRAINT ' || quote_ident(v_name);
                    EXECUTE 'ALTER TABLE inventory_records ADD CONSTRAINT ' || quote_ident(v_name) ||
                        ' FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE RESTRICT';
                END IF;
            END;
            $$;
        """))

    await _ensure_admin_user()
    await _seed_telegram_users_from_env()


async def _seed_telegram_users_from_env() -> None:
    """One-time migration: import TELEGRAM_QUERY_USER_IDS env var into DB.

    Safe to run on every startup — uses INSERT ... ON CONFLICT DO NOTHING.
    Once IDs are in DB they are managed via the API; the env var becomes optional.
    """
    from app.models.telegram_allowed_user import TelegramAllowedUser

    raw = settings.telegram_query_user_ids.strip()
    if not raw:
        return

    ids: list[int] = []
    for part in raw.split(","):
        part = part.strip()
        if part.isdigit():
            ids.append(int(part))
    if not ids:
        return

    async with AsyncSessionLocal() as session:
        for tg_id in ids:
            exists = await session.scalar(
                select(TelegramAllowedUser).where(
                    TelegramAllowedUser.telegram_user_id == tg_id
                )
            )
            if exists is None:
                session.add(TelegramAllowedUser(
                    telegram_user_id=tg_id,
                    note="seeded from TELEGRAM_QUERY_USER_IDS env var",
                ))
        await session.commit()


async def _ensure_admin_user() -> None:
    from app.models.user import User
    from app.services.auth import hash_password

    username = settings.admin_username
    password = settings.admin_password
    if not username or not password:
        return

    async with AsyncSessionLocal() as session:
        existing = await session.scalar(select(User).where(User.username == username))
        if existing is None:
            session.add(User(username=username, password_hash=hash_password(password)))
            await session.commit()
