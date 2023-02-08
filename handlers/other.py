
from aiogram.types import Message
import json, string
from create_bot import dp
from aiogram import Dispatcher


# @dp.message_handler()
async def mat_send(message: Message):
    if {i.lower().translate(str.maketrans('', '', string.punctuation)) for i in message.text.split(' ')}.intersection(
            set(json.load(open('cenz.json')))) != set():
        await message.reply('Маты запрещены')
        await message.delete()
    else:
        await message.answer(text=message.text)


def regster_handlers_other(dp: Dispatcher):
    dp.message.register(mat_send)
