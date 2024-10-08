import asyncio
import bs4
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, InlineKeyboardMarkup, CallbackQuery
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from config import config
import parser

bot = Bot(
    token = config.TG_TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML
    )
)

dp = Dispatcher()

chatId_to_group = {}


def open_shed_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="Открыть расписание")
    kb.button(text="Сменить группу")
    kb.adjust(2)
    return kb.as_markup(
        resize_keyboard = True,
        input_field_placeholder = "Выбери пункт меню",
        one_time_keyboard = True
    )

def schedule_navi() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="<<<", callback_data="prev_week")
    kb.button(text=">>>", callback_data="next_week")
    kb.button(text="Выйти из расписания", callback_data="sched_exit")
    kb.adjust(2)
    return kb.as_markup()

def schedule_parser(schedule: dict) -> str:
    lesson_type_dict = {
        'sem': 'Семинар',
        'lect': 'лекция',
        'lab': 'Лабораторная работа'
    }
    reply_text = ""
    for i in range(0,6):
        day = schedule[str(i)]
        reply_text += f"""----------------------------------------------
Дата: {day['date']}, {day['name']}"""
        if day['lessons']:  # Проверяем, есть ли занятия
            for index, lesson in enumerate(day['lessons']):
                reply_text += f"""<blockquote><b>Номер пары: </b>{lesson['num']}
<b>Дисциплина: </b>{lesson['name']}
<b>Время: </b>{lesson['time']}
<b>Тип: </b>{lesson_type_dict[lesson['type']]}
<b>Аудитория: </b>{lesson['place']}</blockquote>"""
                if index != len(day['lessons']) - 1: reply_text += '\n'
        else:
            reply_text += f"<blockquote>Занятий нет</blockquote>"
    return reply_text


class UserStates(StatesGroup):
    sched_soup = State()
    week_num = State()
    


@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await message.answer("Привет! Отправь полный номер группы и я его запомню")
    await state.set_state(UserStates.week_num)
    

@dp.message(UserStates.week_num)
async def ind_group(message: Message, state: FSMContext):
    soup, week_num = parser.get_soup_shedule({'group_num': message.text.lower(),
                                              'week_num': None})
    if week_num:
        await state.update_data(
            week_num = week_num,
            sched_soup = soup
            )
        chatId_to_group[str(message.chat.id)] = message.text.lower()
        await state.set_state(UserStates.sched_soup)
        await message.answer("Группа успешно найдена и сохранена!", reply_markup=open_shed_kb())
    else:
        await message.answer("Расписание для указанной группы не найдено")


@dp.message(F.text.lower() == "открыть расписание", UserStates.sched_soup)
async def schedule(message: Message, state: FSMContext):
    user_data = await state.get_data()
    soup = user_data.get('sched_soup')
    text = schedule_parser(parser.parser(soup)[0])
    reply_text = f"<b>Расписание для группы </b>{chatId_to_group[str(message.chat.id)]}\n<b>Неделя №{user_data.get('week_num')}</b>\n" + text
    await state.update_data(week_num=user_data.get('week_num'))
    await message.answer(text=text, reply_markup=schedule_navi())


@dp.callback_query(lambda c: c.data in ['prev_week', 'next_week'], UserStates.sched_soup)
async def week_change(call: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    week_number = user_data.get('week_num')
    group_num = chatId_to_group[str(call.message.chat.id)]

    if call.data == "prev_week": 
        week_number -= 1
    elif call.data == "next_week":
        week_number += 1

    await state.update_data(week_num = week_number)
    soup, week_num = parser.get_soup_shedule({'group_num': group_num,
                                              'week_num': week_number})
    text = schedule_parser(parser.parser(soup)[0])
    reply_text = f"<b>Расписание для группы </b>{group_num}\n<b>Неделя №{week_number}</b>\n" + text
    await call.message.edit_text(reply_text, reply_markup=schedule_navi())
    await call.answer(cache_time=1)


@dp.callback_query(F.data.casefold() == 'sched_exit', UserStates.sched_soup)
async def exit(call: CallbackQuery, state: FSMContext):
    state.clear()
    await call.message.delete()
    await call.message.answer("Привет! Отправь полный номер группы и я его запомню")
    await state.set_state(UserStates.week_num)
    

@dp.message(F.text.lower() == 'сменить группу', UserStates.sched_soup)
async def change(message: Message, state: FSMContext):
    await message.answer("Отправь полный номер группы и я его запомню")
    await state.set_state(UserStates.week_num)



async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())