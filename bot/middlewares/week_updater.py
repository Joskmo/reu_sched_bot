import aiohttp
import pytz
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from bs4 import BeautifulSoup

from ..core.db import redis


async def upd_week_num() -> None:
    headers = {
        'X-Requested-With': 'XMLHttpRequest',
    }
    group_num = await redis.get("base_group")
    group_num = group_num.decode('utf-8') if group_num else None
    if not group_num:
        logging.info("Base group not set. Skipping week number update.")
        return
    link = f"http://rasp.rea.ru/Schedule/ScheduleCard?selection={group_num}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url=link, headers=headers) as response:
                response.raise_for_status()
                data = await response.text()
                soup = BeautifulSoup(data, 'html.parser')
                if soup.find('div'): 
                    week_input: BeautifulSoup = soup.find('input', id='weekNum')
                    if week_input and week_input.get('value'):
                        cur_week = int(week_input.get('value'))
                        await redis.set(name="cur_week", value=str(cur_week))
                        logging.info(f"Updated week number. Set week_num to {cur_week}")
                    else:
                        logging.warning("Week number input not found in the response.")

    except aiohttp.ClientError as e:
        print(f"Ошибка при получении данных: {e}")


scheduler = AsyncIOScheduler()
moscow_tz = pytz.timezone('Europe/Moscow')
scheduler.add_job(
    upd_week_num,
    trigger=CronTrigger(
        day_of_week='mon',
        hour=0,
        minute=1,
        timezone=moscow_tz
    ),
    id="week_num_updater",
    name="Обновление номера недели"
)
