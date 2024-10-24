from aiogram import Router
from aiogram import F
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
    sh.users_set.add(message.from_user.username)
    await state.clear()
    await message.answer("""Привет! Отправь полный номер группы и я его запомню
P.s.: если что-то сломалось, пропиши /start""")
    await state.set_state(UserStates.group_num)


@router.message(UserStates.group_num)
async def get_schedule(message: Message, state: FSMContext):
    soup, week_num = site_actions.get_schedule_soup({'selection': message.text.lower(),
                                              'weekNum': sh.cur_week})
    if week_num:
        await state.update_data(
            week_num = week_num,
            group_num = message.text.lower()
            )
        await state.set_state(UserStates.week_num)
        schedule_text: str = f"<b>Расписание для группы </b>{message.text.lower()}\n<b>Неделя №{week_num}</b>\n"
        schedule_text += site_actions.get_schedule_text(soup)
        await message.answer(text=schedule_text, reply_markup=sched_kb.schedule_navi())
    else:
        await message.answer("Расписание для указанной группы не найдено")


@router.callback_query(lambda c: c.data in ['prev_week', 'next_week'], UserStates.week_num)
async def week_change(call: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    week_number = user_data.get('week_num')
    group_num = user_data.get('group_num')

    if call.data == "prev_week": 
        week_number -= 1
    elif call.data == "next_week":
        week_number += 1

    await state.update_data(week_num = week_number)
    soup, _ = site_actions.get_schedule_soup({'selection': group_num,
                                              'weekNum': week_number})
    
    reply_text = f"<b>Расписание для группы </b>{group_num}\n<b>Неделя №{week_number}</b>\n"
    reply_text += site_actions.get_schedule_text(soup)

    await call.message.edit_text(reply_text, reply_markup=sched_kb.schedule_navi())
    await call.answer(f"Неделя №{week_number}", show_alert=False, cache_time=1)


@router.callback_query(F.data.casefold() == 'sched_exit', UserStates.week_num)
async def exit(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.delete()
    await call.message.answer("Для возврата в расписание отправь номер группы")
    await state.set_state(UserStates.group_num)


@router.callback_query(F.data.casefold() == 'current_week', UserStates.week_num)
async def goto_cur_week(call: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    soup, _ = site_actions.get_schedule_soup({'selection': user_data.get('group_num'),
                                              'weekNum': sh.cur_week})
    if sh.cur_week == user_data.get('week_num'):
        await call.answer(f'Расписание на текущую неделю уже открыто', cache_time=1)
    else:
        await state.update_data(
            week_num = sh.cur_week,
            group_num = user_data.get('group_num')
            )
        schedule_text: str = f"<b>Расписание для группы </b>{user_data.get('group_num')}\n<b>Неделя №{sh.cur_week}</b>\n"
        schedule_text += site_actions.get_schedule_text(soup)
        await call.message.edit_text(text=schedule_text, reply_markup=sched_kb.schedule_navi())
        await call.answer(f"Неделя №{sh.cur_week} (текущая)", cache_time=1)
