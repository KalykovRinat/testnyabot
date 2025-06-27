import aiomysql
from config import DB_CONFIG
import asyncio
import aiosqlite

db_pool = None

async def init_db_pool():
    global db_pool
    loop = asyncio.get_event_loop()
    db_pool = await aiomysql.create_pool(
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        db=DB_CONFIG["db"],
        autocommit=True,
        minsize=1,
        maxsize=10,
        loop=loop
    )

async def get_accounts_by_category(category):
    async with db_pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                "SELECT * FROM accounts WHERE category = %s AND is_deleted = FALSE",
                (category,)
            )
            accounts = await cur.fetchall()
    return accounts

async def insert_account(category, login, password, price_som,price_rub, description, binding, media_id=None, media_type=None):
    async with db_pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("""
                INSERT INTO accounts (category, login, password, price_som,price_rub, description, binding, media_id, media_type)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (category, login, password, price_som,price_rub, description, binding, media_id, media_type))
        await conn.commit()

async def get_all_accounts():
    async with db_pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT id, category, login, price_som, price_rub FROM accounts WHERE is_deleted = FALSE"
            )
            rows = await cur.fetchall()
            return rows


async def get_account_by_id(acc_id):
    async with db_pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                "SELECT * FROM accounts WHERE id = %s AND is_deleted = FALSE",
                (acc_id,)
            )
            return await cur.fetchone()


async def delete_account_by_id(acc_id):
    async with db_pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("UPDATE accounts SET is_deleted = TRUE WHERE id = %s", (acc_id,))
        await conn.commit()
