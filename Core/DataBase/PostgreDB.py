import asyncio
import logging
from typing import Optional
import asyncpg
from Core.Settings import SettingsApp

logger = logging.getLogger(__name__)

settings = SettingsApp()
POSTGRE_URL = settings.postgre_url or "postgresql://postgres:postgres@localhost:5432/testdb"

_pools = {}
_initialized_pools = set()


async def get_postgres_pool() -> asyncpg.Pool:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop not in _pools or _pools[loop] is None or _pools[loop]._closed:
        logger.debug(f"Connecting to PostgreSQL pool at {POSTGRE_URL}")
        _pools[loop] = await asyncpg.create_pool(dsn=POSTGRE_URL, min_size=1, max_size=5)

    pool = _pools[loop]
    if pool not in _initialized_pools:
        try:
            await init_postgres_db(pool)
            _initialized_pools.add(pool)
        except Exception as e:
            logger.warning(f"Could not auto-initialize postgres table: {e}")

    return pool


async def close_postgres_pool():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop in _pools and _pools[loop] is not None:
        await _pools[loop].close()
        _pools[loop] = None


CREATE_USERS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'user',
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    created_at VARCHAR(100) NOT NULL,
    updated_at VARCHAR(100) NOT NULL
);
"""


async def init_postgres_db(pool=None):
    if pool is None:
        pool = await get_postgres_pool()
    async with pool.acquire() as conn:
        await conn.execute(CREATE_USERS_TABLE_SQL)
        logger.info("PostgreSQL users table initialized successfully")
