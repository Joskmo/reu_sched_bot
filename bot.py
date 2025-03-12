import logging
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties


from config import config
from middlewares.week_updater import scheduler, upd_week_num
from handlers import sched_handler, extra


bot = Bot(
    token = config.TG_TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML
    )
)


dp = Dispatcher()


async def main():
    upd_week_num()
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
