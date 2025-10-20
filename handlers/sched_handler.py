from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import middlewares.site_actions as site_actions
import keyboards.schedule_kb as sched_kb
import middlewares.shared as sh

router = Router()

class UserStates(StatesGroup):
    group_num = State()
    week_num = State()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user = message.from_user
    if user and user.username:
        sh.users_set.add(user.username)
    elif message.chat:
        sh.users_set.add(str(message.chat.id))
    await state.clear()
    await message.answer("""Привет! Отправь полный номер группы и я его запомню
P.s.: если что-то сломалось, пропиши /start""")
    await state.set_state(UserStates.group_num)


@router.message(UserStates.group_num)
async def get_schedule(message: Message, state: FSMContext):
    soup, week_num = await site_actions.get_schedule_soup({
        'selection': message.text.lower() if message.text else "",
        'weekNum': sh.cur_week
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
    
    reply_text = f"<b>Расписание для группы </b>{group_num}\n<b>Неделя №{week_number}</b>\n"
    reply_text += site_actions.get_schedule_text(soup)
    if isinstance(call.message, Message):
        await call.message.edit_text(reply_text, reply_markup=sched_kb.schedule_navi())
    else:
        await call.message.answer(
            reply_text,
            reply_markup=sched_kb.schedule_navi()
        ) if call.message else None
    await call.answer(f"Неделя №{week_number}", show_alert=False, cache_time=1)


@router.callback_query(F.data.casefold() == 'sched_exit', UserStates.week_num)
async def exit(call: CallbackQuery, state: FSMContext):
    await state.clear()
    if isinstance(call.message, Message):
        await call.message.delete()
    await call.message.answer("Для возврата в расписание отправь номер группы") if call.message else None
    await state.set_state(UserStates.group_num)


@router.callback_query(F.data.casefold() == 'current_week', UserStates.week_num)
async def goto_cur_week(call: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    soup, _ = await site_actions.get_schedule_soup({'selection': user_data.get('group_num'),
                                              'weekNum': sh.cur_week})
    if sh.cur_week == user_data.get('week_num'):
        await call.answer(
            f'Расписание на текущую неделю уже открыто',
            cache_time=1
        )
    else:
        await state.update_data(
            week_num = sh.cur_week,
            group_num = user_data.get('group_num')
            )
        schedule_text: str = f"<b>Расписание для группы </b>{user_data.get('group_num')}\n<b>Неделя №{sh.cur_week}</b>\n"
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
            text=f"Неделя №{sh.cur_week} (текущая)",
            cache_time=1
        )
