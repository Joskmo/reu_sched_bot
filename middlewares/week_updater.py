import requests, pytz
from bs4 import BeautifulSoup
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

import middlewares.shared as sh


def upd_week_num():
    headers = {
        'X-Requested-With': 'XMLHttpRequest',
    }
    link = "https://rasp.rea.ru/Schedule/ScheduleCard?selection=15.27д-би01/24б"
    try:
        response = requests.get(url=link, headers=headers)
        response.raise_for_status()
        data = response.text
        soup = BeautifulSoup(data, 'html.parser')
        if soup.find('div'): 
            cur_week = int(soup.find('input', id='weekNum').get('value'))
            sh.cur_week = cur_week
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при выполнении запроса: {e}")


scheduler = AsyncIOScheduler()
moscow_tz = pytz.timezone('Europe/Moscow')
scheduler.add_job(upd_week_num, CronTrigger(day_of_week='mon', hour=0, minute=1, timezone=moscow_tz))

