import requests
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

from setings import BOT_TOKEN

bot: Bot = Bot(token=BOT_TOKEN)
dp: Dispatcher = Dispatcher()
API_URL: str = 'https://api.telegram.org/bot'
API_FOX_URL: str = 'https://randomfox.ca/floof'
ERROR_TEXT: str = 'Здесь должна была быть картинка с лисой :('
offset: int = -2


# Этот хэндлер будет срабатывать на команду "/start"
@dp.message(Command(commands=["start"]))
async def process_start_command(message: Message):
    await message.answer('Привет!\nМеня зовут Эхо-бот!\nНапиши мне что-нибудь')


# Хендлер на команду '/hi'
@dp.message(Command(commands=["hi"]))
async def process_start_command(message: Message, offset=offset):
    updates = requests.get(f'{API_URL}{BOT_TOKEN}/getUpdates?offset={offset - 1}').json()

    await message.answer('Привет, как на счет фоточек лисы?')

    for result in updates['result']:
        chat_id = result['message']['from']['id']
        fox_response = requests.get(API_FOX_URL)
        if fox_response.status_code == 200:
            cat_link = fox_response.json()['image']
            requests.get(f'{API_URL}{BOT_TOKEN}/sendPhoto?chat_id={chat_id}&photo={cat_link}')
        else:
            requests.get(f'{API_URL}{BOT_TOKEN}/sendMessage?chat_id={chat_id}&text={ERROR_TEXT}')


# Хендлер на фотки
@dp.message()
async def send_photo_echo(message: Message):
    await message.reply_photo(message.photo[0].file_id)


# Этот хэндлер будет срабатывать на любые ваши текстовые сообщения,
# кроме команд "/start" и "/help""
@dp.message()
async def send_echo(message: Message):
    await message.answer(text=message.text)


if __name__ == '__main__':
    dp.run_polling(bot)
