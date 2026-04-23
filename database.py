"""
🗄️ Database modul — asyncpg + PostgreSQL (Render)
"""

import asyncpg
import os
import logging

logger = logging.getLogger(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL", "")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

_pool = None


async def get_pool():
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=5)
    return _pool


async def close_pool():
    global _pool
    if _pool:
        await _pool.close()
        _pool = None


async def init_db():
    pool = await get_pool()
    async with pool.acquire() as conn:
        # Ro'yxatdan o'tganlar
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id       BIGINT PRIMARY KEY,
                name          TEXT NOT NULL,
                phone         TEXT NOT NULL,
                username      TEXT DEFAULT '—',
                registered_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)
        # Login logi
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS logins (
                id         SERIAL PRIMARY KEY,
                user_id    BIGINT,
                logged_at  TIMESTAMPTZ DEFAULT NOW()
            )
        """)
        # /start bosganlar (ro'yxatdan o'tmagan ham)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS starts (
                user_id    BIGINT PRIMARY KEY,
                username   TEXT DEFAULT '—',
                full_name  TEXT DEFAULT '—',
                started_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)
        # Rejalashtirilgan reklamalar
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS scheduled_ads (
                id           SERIAL PRIMARY KEY,
                text         TEXT NOT NULL,
                target       TEXT NOT NULL DEFAULT 'all',
                scheduled_at TIMESTAMPTZ NOT NULL,
                sent         BOOLEAN DEFAULT FALSE,
                created_at   TIMESTAMPTZ DEFAULT NOW()
            )
        """)
    logger.info("✅ Database tayyor")


# ─── USERS ───────────────────────────────────────────────

async def save_user(user_id: int, name: str, phone: str, username: str):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO users (user_id, name, phone, username)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (user_id) DO UPDATE
            SET name=$2, phone=$3, username=$4
        """, user_id, name, phone, username)


async def get_users_with_time() -> list:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT u.user_id, u.name, u.phone, u.username,
                   u.registered_at,
                   MAX(l.logged_at) as last_login
            FROM users u
            LEFT JOIN logins l ON u.user_id = l.user_id
            GROUP BY u.user_id
            ORDER BY u.registered_at DESC
        """)
        return [dict(r) for r in rows]


async def get_all_users() -> list:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM users ORDER BY registered_at DESC")
        return [dict(r) for r in rows]


async def get_all_user_ids() -> list:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT user_id FROM users")
        return [r["user_id"] for r in rows]


async def count_users() -> int:
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchval("SELECT COUNT(*) FROM users")


# ─── LOGINS ──────────────────────────────────────────────

async def log_login(user_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO logins (user_id) VALUES ($1)", user_id
        )


# ─── STARTS ──────────────────────────────────────────────

async def save_start(user_id: int, username: str, full_name: str):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO starts (user_id, username, full_name, started_at)
            VALUES ($1, $2, $3, NOW())
            ON CONFLICT (user_id) DO UPDATE
            SET username=$2, full_name=$3, started_at=NOW()
        """, user_id, username, full_name)


async def get_all_starts() -> list:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM starts ORDER BY started_at DESC")
        return [dict(r) for r in rows]


async def get_all_start_ids() -> list:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT user_id FROM starts")
        return [r["user_id"] for r in rows]


async def count_starts() -> int:
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchval("SELECT COUNT(*) FROM starts")


# ─── SCHEDULED ADS ───────────────────────────────────────

async def add_scheduled_ad(text: str, target: str, scheduled_at) -> int:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            INSERT INTO scheduled_ads (text, target, scheduled_at)
            VALUES ($1, $2, $3)
            RETURNING id
        """, text, target, scheduled_at)
        return row["id"]


async def get_pending_ads() -> list:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT * FROM scheduled_ads
            WHERE sent = FALSE AND scheduled_at <= NOW()
            ORDER BY scheduled_at ASC
        """)
        return [dict(r) for r in rows]


async def get_all_scheduled_ads() -> list:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT * FROM scheduled_ads
            WHERE sent = FALSE
            ORDER BY scheduled_at ASC
        """)
        return [dict(r) for r in rows]


async def mark_ad_sent(ad_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE scheduled_ads SET sent=TRUE WHERE id=$1", ad_id
        )


async def delete_scheduled_ad(ad_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "DELETE FROM scheduled_ads WHERE id=$1", ad_id
        )
