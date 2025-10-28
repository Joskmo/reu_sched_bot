from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message


router = Router()


@router.message(Command('code'))
async def github_link(message: Message):
    await message.answer(text=(
        "Разработчик: @Joskmo\n"
        "Ссылка на исходный код на gitHub: https://github.com/Joskmo/reu_sched_bot\n"
        "Принимаю все пожелания, комментарии и доработки :)"
    ))
    