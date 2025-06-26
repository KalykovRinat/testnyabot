import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN, ADMIN_IDS
from handlers import user, admin
from aiogram.client.default import DefaultBotProperties
from database.db import init_db_pool


async def main():
    await init_db_pool()
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_routers(
        user.router,
        admin.router
    )

    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
