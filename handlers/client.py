import requests
from aiogram import Dispatcher
from aiogram import F
from aiogram.filters import Command
from aiogram.types import Message
from setings import API_FOX_URL


# Этот хэндлер будет срабатывать на команду "/start"
async def process_start_command(message: Message):
    await message.answer('Добро времени суток!\nЖду твоих команд.')


ERROR_TEXT: str = 'Здесь должна была быть картинка с лисой :('


# Хендлер на команду 'rand_fox'
async def process_fox_command(message: Message):
    await message.answer('Привет, как на счет фоточек лисы?')
    fox_response = requests.get(API_FOX_URL)
    if fox_response.status_code == 200:
        fox_link = fox_response.json()['image']
        await message.answer_photo(fox_link)
    else:
        await message.answer(ERROR_TEXT)


# Хендлер на фотки
async def send_photo_echo(message: Message):
    await message.reply_photo(message.photo[0].file_id)


# Этот хэндлер на любые текстовые сообщения
async def send_echo(message: Message):
    await message.answer(text=message.text)


def regster_handlers_client(dp: Dispatcher):
    dp.message.register(process_start_command, Command(commands=['start', 'help']))
    dp.message.register(process_fox_command, Command(commands=['rand_fox']))
    dp.message.register(send_photo_echo, F.photo)

