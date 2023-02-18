from aiogram import Bot, Dispatcher
from setings import BOT_TOKEN

bot: Bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp: Dispatcher = Dispatcher()