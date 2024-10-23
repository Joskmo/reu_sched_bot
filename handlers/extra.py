from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

import middlewares.shared as sh

router = Router()


with open('users.txt', 'r') as file:
    for line in file:
        nickname = line.strip()
        sh.users_set.add(nickname)


@router.message(Command('dump'))
async def dump_users(message: Message):
    with open('users.txt', 'w') as dump_file:
        for nickname in sh.users_set:
            dump_file.write(nickname + '\n')
    await message.answer(text='Дамп был создан')


@router.message(Command('code'))
async def github_link(message: Message):
    reply_text = """Разработчик: @Joskmo
Ссылка на исходный код на gitHub: https://github.com/Joskmo/reu_sched_bot
Принимаю все пожелания, комментарии и доработки :)"""
    await message.answer(text=reply_text)
    