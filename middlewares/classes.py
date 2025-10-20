from pydantic import BaseModel
from typing import List, Optional


class Lesson(BaseModel):
    num: int
    type: Optional[str] = None
    time: Optional[str] = None
    name: Optional[str] = None
    place: Optional[str] = None


class Day(BaseModel):
    date: str
    name: str
    first_lesson_num: Optional[int] = None
    lessons: Optional[List[Lesson]] = None


class Schedule(BaseModel):
    group: str
    week_number: Optional[int] = None
    schedule: Optional[dict] = None