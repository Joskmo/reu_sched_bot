from pydantic import BaseModel
from typing import List, Optional


class Lesson(BaseModel):
    num: int # <needs to be parsed>
    type: Optional[str] = None # lecture_type
    time: Optional[str] = None # <needs to be parsed from num>
    name: Optional[str] = None # title
    place: Optional[str] = None # location


class Day(BaseModel):
    date: str # <needs to be parsed>
    name: str
    first_lesson_num: Optional[int] = None # <from min num>
    lessons: Optional[List[Lesson]] = None # <smt like link>


class Schedule(BaseModel):
    group: str
    week_number: Optional[int] = None
    schedule: Optional[dict] = None