import aiohttp
import pytz
from bs4 import BeautifulSoup
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

import middlewares.shared as sh


async def upd_week_num():
    headers = {
        'X-Requested-With': 'XMLHttpRequest',
    }
    link = "http://rasp.rea.ru/Schedule/ScheduleCard?selection=15.27д-би01/24б"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url=link, headers=headers) as response:
                response.raise_for_status()
                data = await response.text()
                soup = BeautifulSoup(data, 'html.parser')
                if soup.find('div'): 
                    week_input = soup.find('input', id='weekNum')
                    if week_input and week_input.get('value'):
                        cur_week = int(week_input.get('value'))
                        sh.cur_week = cur_week
                        print(cur_week)
                    else:
                        print("Не удалось найти номер недели в ответе.")

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

