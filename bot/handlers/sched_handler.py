from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import logging

from redis.asyncio import Redis

from ..core import site_actions
from ..keyboards import schedule_kb as sched_kb


router = Router()

class UserStates(StatesGroup):
    group_num = State()
    week_num = State()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user = message.from_user
    logging.info(f"User @{user.username if user.username else 'No_nickname'} ({user.id}) started the bot.")
    await state.clear()
    await message.answer(
        text = (
            f"Привет! Отправь полный номер группы и я его запомню"
            f"P.s.: если что-то сломалось, пропиши /start"""
        )
    )
    await state.set_state(UserStates.group_num)


@router.message(UserStates.group_num)
async def get_schedule(message: Message, state: FSMContext, redis: Redis):
    soup, week_num = await site_actions.get_schedule_soup({
        'selection': message.text.lower() if message.text else "",
    })
    if week_num:
        await state.update_data(
            week_num = week_num,
            group_num = message.text.lower() if message.text else ""
        )
        await state.set_state(UserStates.week_num)
        schedule_text: str = (
            f"<b>Расписание для группы </b>{message.text.lower() if message.text else ''}\n"
            f"<b>Неделя №{week_num}</b>\n"
        )
        schedule_text += site_actions.get_schedule_text(soup)
        await message.answer(
            text=schedule_text,
            reply_markup=sched_kb.schedule_navi()
        )
        if message.text:
            await redis.set(
                name=f"base_group",
                value=f"{message.text.lower()}"
            )
    else:
        await message.answer("Расписание для указанной группы не найдено")


@router.callback_query(lambda c: c.data in ['prev_week', 'next_week'], UserStates.week_num)
async def week_change(call: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    week_number = user_data.get('week_num')
    group_num = user_data.get('group_num')

    if call.data == "prev_week":
        if week_number and week_number > 1:
            week_number -= 1
    elif call.data == "next_week":
        if week_number:
            week_number += 1

    await state.update_data(week_num = week_number)
    soup, _ = await site_actions.get_schedule_soup({
        'selection': group_num,
        'weekNum': week_number
    })
    
    reply_text = (
        f"<b>Расписание для группы </b>{group_num}\n"
        f"<b>Неделя №{week_number}</b>\n"
    )
    reply_text += site_actions.get_schedule_text(soup)
    if isinstance(call.message, Message):
        await call.message.edit_text(
            text=reply_text,
            reply_markup=sched_kb.schedule_navi()
        )
    else:
        await call.message.answer(
            text=reply_text,
            reply_markup=sched_kb.schedule_navi()
        ) if call.message else None
    await call.answer(
        text=f"Неделя №{week_number}",
        show_alert=False,
        cache_time=1
    )


@router.callback_query(F.data.casefold() == 'sched_exit', UserStates.week_num)
async def exit(call: CallbackQuery, state: FSMContext):
    await state.clear()
    if isinstance(call.message, Message):
        await call.message.delete()
    if call.message:
        await call.message.answer(
            text = "Для возврата в расписание отправь номер группы"
        )
    await state.set_state(UserStates.group_num)


@router.callback_query(F.data.casefold() == 'current_week', UserStates.week_num)
async def goto_cur_week(call: CallbackQuery, state: FSMContext, redis: Redis):
    user_data = await state.get_data()
    cur_week = int(await redis.get("cur_week"))
    soup, _ = await site_actions.get_schedule_soup({
        'selection': user_data.get('group_num'),
        'weekNum': cur_week
    })
    if cur_week == user_data.get('week_num'):
        await call.answer(
            f'Расписание на текущую неделю уже открыто',
            cache_time=1
        )
    else:
        await state.update_data(
            week_num = cur_week,
            group_num = user_data.get('group_num')
        )
        schedule_text: str = (
            f"<b>Расписание для группы </b>{user_data.get('group_num')}\n"
            f"<b>Неделя №{cur_week}</b>\n"
        )
        schedule_text += site_actions.get_schedule_text(soup)
        if isinstance(call.message, Message):
            await call.message.edit_text(
                text=schedule_text,
                reply_markup=sched_kb.schedule_navi()
            )
        else:
            await call.message.answer(
                text=schedule_text,
                reply_markup=sched_kb.schedule_navi()
            ) if call.message else None

        await call.answer(
            text=f"Неделя №{cur_week} (текущая)",
            cache_time=1
        )
