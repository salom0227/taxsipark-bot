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
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id       BIGINT PRIMARY KEY,
                name          TEXT NOT NULL,
                phone         TEXT NOT NULL,
                username      TEXT DEFAULT '—',
                registered_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)
    logger.info("✅ Database tayyor")


async def save_user(user_id: int, name: str, phone: str, username: str):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO users (user_id, name, phone, username)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (user_id) DO UPDATE
            SET name=$2, phone=$3, username=$4
        """, user_id, name, phone, username)


async def get_all_users() -> list:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM users ORDER BY registered_at DESC")
        return [dict(r) for r in rows]


async def count_users() -> int:
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchval("SELECT COUNT(*) FROM users")
