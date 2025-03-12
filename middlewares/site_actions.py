import requests
import re
import middlewares.classes as classes
import string
from bs4 import BeautifulSoup

from middlewares import shared as sh

rasp_dict = {}

# dictionary for timetable (get time by lesson num)
time_dict = {
    1: "08:30 - 10:00",
    2: "10:10 - 11:40",
    3: "11:50 - 13:20",
    4: "14:00 - 15:30",
    5: "15:40 - 17:10",
    6: "17:20 - 18:50",
    7: "18:55 - 20:25", 
    8: "20:30 - 22:00"
}

# List if days of the week
days_of_week = (
    "ПОНЕДЕЛЬНИК",
    "ВТОРНИК",
    "СРЕДА",
    "ЧЕТВЕРГ",
    "ПЯТНИЦА",
    "СУББОТА"
)

link = "http://rasp.rea.ru/Schedule/ScheduleCard"
headers = {
        'X-Requested-With': 'XMLHttpRequest',
    }


def get_schedule_soup(group_dict: dict):    
    response = requests.get(
        url=link,
        params=group_dict,
        headers=headers,
        verify=False,
    )
    soup = BeautifulSoup(response.text, 'html.parser')
    if soup.find('div'): week_num = int(soup.find('input', id='weekNum').get('value'))
    else: week_num = None
    return soup, week_num


def get_schedule_text(soup: BeautifulSoup) -> str:
    schedule_text: str = ""
    tables = soup.find_all('table', class_=['table table-light', 'table table-light today'])

    for day in days_of_week:
        day_table = next((table for table in tables if day in table.find('h5').get_text()), None)
        if day_table:
            date_text = day_table.find('h5').get_text()
            date = date_text.split(', ')[1]
            cur_day = classes.Day(date=date, name=string.capwords(day)) # date
            slots = day_table.select('tr[class^="slot load"]:not([class="slot load-empty"])')
            if slots:
                cur_day.lessons = []
                for slot in slots:
                    
                    # info about lesson num(). We need only num of pair -> use regular expression
                    time_info = int(re.match(r'\d', (slot.find('span', class_='pcap').get_text(strip=True)))[0])
                    
                    cur_less = classes.Lesson(num=time_info)
                    cur_less.time = time_dict[time_info]

                    lesson_link = slot.find('a', class_='task')
                    if lesson_link:
                        title = lesson_link.contents[0].strip() # name of lesson
                        cur_less.name = title

                        cur_less.type = lesson_link.i.get_text(strip=True).replace('\n                 ', '') # type of lesson

                        location_parts = list(lesson_link.stripped_strings)[2]
                        match = re.search(r'(\d+)\s*корпус\s*-\s*([\d/*.]+|[\w/ №\d]+)', location_parts)
                        if match:
                            location = f"{match.group(1)[0]}к {match.group(2)}"
                        else:
                            location = "Неизвестно"
                        cur_less.place = location
                        
                    cur_day.lessons.append(cur_less)

            day_dict = cur_day.model_dump()
            
            schedule_text += f"""----------------------------------------------
Дата: {day_dict['date']}, {day_dict['name']}"""
            if day_dict['lessons']:  # Проверяем, есть ли занятия
                for index, lesson in enumerate(day_dict['lessons']):
                    schedule_text += f"""<blockquote><b>Номер пары: </b>{lesson['num']}
<b>Дисциплина: </b>{lesson['name']}
<b>Время: </b>{lesson['time']}
<b>Тип: </b>{lesson['type']}
<b>Аудитория: </b>{lesson['place']}</blockquote>"""
                    if index != len(day_dict['lessons']) - 1: schedule_text += '\n'
            else:
                schedule_text += f"<blockquote>Занятий нет</blockquote>"

    return schedule_text
