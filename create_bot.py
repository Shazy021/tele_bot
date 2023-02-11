from aiogram import Bot, Dispatcher, F
from setings import BOT_TOKEN
from aiogram.fsm.storage.memory import MemoryStorage

bot: Bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp: Dispatcher = Dispatcher()