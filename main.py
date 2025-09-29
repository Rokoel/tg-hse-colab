import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN, EVENTS
from db import init_db, ensure_events
from handlers_user import router as user_router
from handlers_admin import router as admin_router

async def main():
    init_db()
    ensure_events(EVENTS)

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(user_router)
    dp.include_router(admin_router)

    print("Bot started")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
