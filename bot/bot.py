import logging
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage

from .config import TelegramSettings
from .core.db import redis
from .middlewares.week_updater import scheduler, upd_week_num
from .handlers import sched_handler, extra
from .middlewares.redis import RedisMiddleware

telegram_config = TelegramSettings()

redis_storage = RedisStorage(
    redis=redis,
)


bot = Bot(
    token = telegram_config.token,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML
    )
)


dp = Dispatcher(
    storage = RedisStorage(redis=redis),
    name = "reu_sched_bot",
)
dp.update.middleware(RedisMiddleware(redis))


async def main():
    await upd_week_num()
    scheduler.start()
    dp.include_routers(
        sched_handler.router,
        extra.router,
    )
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        logging.basicConfig(level=logging.INFO)
        asyncio.run(main())
    except KeyboardInterrupt:
        scheduler.shutdown()
        logging.info("Shutting down...")
