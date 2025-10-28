import aiohttp
import re
import string
from typing import Any, Optional, Tuple

from bs4 import BeautifulSoup
from bs4.element import Tag

from .models import Lesson, Day

# dictionary for timetable (get time by lesson num)
TIME_DICT: dict[int, str] = {
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
DAYS_OF_WEEK: tuple[str] = (
    "ПОНЕДЕЛЬНИК",
    "ВТОРНИК",
    "СРЕДА",
    "ЧЕТВЕРГ",
    "ПЯТНИЦА",
    "СУББОТА"
)

LINK: str = "http://rasp.rea.ru/Schedule/ScheduleCard"
HEADERS: dict[str, str] = {
        'X-Requested-With': 'XMLHttpRequest',
    }


async def get_schedule_soup(group_dict: dict[str, str]) -> Tuple[BeautifulSoup, Optional[int]]:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=LINK,
                params=group_dict,
                headers=HEADERS,
            ) as response:
                response.raise_for_status()
                data = await response.text()
                soup = BeautifulSoup(data, 'html.parser')
                if soup.find('div'):
                    week_input: Optional[Tag] = soup.find('input', id='weekNum')
                    week_value: Optional[str] = week_input.get('value') if week_input else None
                    week_num = int(week_value) if week_value is not None else None
                else:
                    week_num = None
                return soup, week_num
            
    except aiohttp.ClientError as e:
        raise Exception(f"Ошибка при выполнении запроса: {e}")
            

def get_schedule_text(soup: BeautifulSoup) -> str:
    schedule_text: str = ""
    tables: list[Tag] = soup.find_all(
        'table', 
        class_=['table table-light', 'table table-light today']
    )

    for day in DAYS_OF_WEEK:
        day_table: Optional[Tag] = next(
            (table for table in tables if day in table.find('h5').get_text()),
            None
        )
        if day_table:
            date_text: str = day_table.find('h5').get_text()
            date: str = date_text.split(', ')[1]
            cur_day: Day = Day(
                date=date,
                name=string.capwords(day)
            ) # date
            slots: list[Tag] = day_table.select(
                'tr[class^="slot load"]:not([class="slot load-empty"])'
            )
            if slots:
                lessons_list: list[Lesson] = []
                cur_day.lessons = lessons_list
                for slot in slots:
                    
                    # info about lesson num(). We need only num of pair -> use regular expression
                    pcap_span: Optional[Tag] = slot.find('span', class_='pcap')
                    if not pcap_span:
                        continue
                    pcap_text: str = pcap_span.get_text(strip=True)
                    time_match: Optional[re.Match[str]] = re.search(
                        pattern = r'\d+',
                        string = pcap_text
                    )
                    if not time_match:
                        continue
                    time_info: int = int(time_match.group(0))
                    
                    cur_less: Lesson = Lesson(num=time_info)
                    cur_less.time = TIME_DICT[time_info]

                    lesson_link: Optional[Tag] = slot.find('a', class_='task')
                    if lesson_link:
                        title: str = lesson_link.contents[0].strip() # name of lesson
                        cur_less.name = title

                        cur_less.type = lesson_link.i.get_text(strip=True).replace('\n                 ', '') # type of lesson

                        location_parts: str = list(lesson_link.stripped_strings)[2]
                        match: Optional[re.Match[str]] = re.search(
                            pattern = r'(\d+)\s*корпус\s*-\s*([\d/*.]+|[\w/ №\d]+)',
                            string = location_parts
                        )
                        if match:
                            location: str = f"{match.group(1)[0]}к {match.group(2)}"
                        else:
                            location = "Неизвестно"
                        cur_less.place = location
                        
                    lessons_list.append(cur_less)

            day_dict: dict[str, Any] = cur_day.model_dump()
            
            schedule_text += (
                f"----------------------------------------------\n"
                f"Дата: {day_dict['date']}, {day_dict['name']}"
            )
            if day_dict['lessons']:
                for index, lesson in enumerate(day_dict['lessons']):
                    lesson_data: dict[str, Any] = lesson
                    schedule_text += (
                        f"<blockquote>"
                        f"<b>Номер пары: </b>{lesson_data['num']}\n"
                        f"<b>Дисциплина </b>{lesson_data['name']}\n"
                        f"<b>Время: </b>{lesson_data['time']}\n"
                        f"<b>Тип: </b>{lesson_data['type']}\n"
                        f"<b>Аудитория: </b>{lesson_data['place']}"
                        f"</blockquote>"
                    )
                    if index != len(day_dict['lessons']) - 1: schedule_text += '\n'
            else:
                schedule_text += f"<blockquote>Занятий нет</blockquote>"

    return schedule_text
