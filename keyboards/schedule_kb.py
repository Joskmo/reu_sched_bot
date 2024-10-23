from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton as InlKbBtn


def schedule_navi() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="<<<", callback_data="prev_week")
    kb.button(text=">>>", callback_data="next_week")
    kb.adjust(2)
    kb.row(
        InlKbBtn(text="Перейти к текущей неделе", callback_data="current_week"),
        InlKbBtn(text="Выйти из расписания", callback_data="sched_exit"),
        width=1
    )
    return kb.as_markup()
