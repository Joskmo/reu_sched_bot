import requests
import re
import classes as classes
import string
from bs4 import BeautifulSoup

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
days_of_week = [
    "ПОНЕДЕЛЬНИК",
    "ВТОРНИК",
    "СРЕДА",
    "ЧЕТВЕРГ",
    "ПЯТНИЦА",
    "СУББОТА"
]

headers = {
    'X-Requested-With': 'XMLHttpRequest',
}

# Default link
link = "https://rasp.rea.ru/Schedule/ScheduleCard?selection="


def get_soup_shedule(group_dict: dict):
    group_link = link + group_dict['group_num'].lower() + "&weekNum=" + (str(group_dict['week_num']) if group_dict['week_num'] else "")
    response = requests.get(
        group_link,
        headers=headers,
    ).text

    soup = BeautifulSoup(response, 'html.parser')
    if soup.find('div'): cur_week = int(soup.find('input', id='weekNum').get('value'))
    else: cur_week = None
    return soup, cur_week


def parser(soup):
    tables = soup.find_all('table', class_=['table table-light', 'table table-light today'])
    cur_week = soup.find('input', id='weekNum').get('value')

    for day, day_num in zip(days_of_week, range(0, 6)):
        
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
                    
                # sort for classes by num: 
                n = len(cur_day.lessons)
                for i in range(0, n-1):
                    for j in range(0, n-1):
                        if (cur_day.lessons[j].num > cur_day.lessons[j+1].num): 
                            cur_day.lessons[j], cur_day.lessons[j+1] = cur_day.lessons[j+1], cur_day.lessons[j]
            day_dict = cur_day.model_dump()
            rasp_dict[str(day_num)] = day_dict
    return rasp_dict, int(cur_week)
