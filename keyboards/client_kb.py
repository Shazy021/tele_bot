from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, KeyboardButtonPollType


b1: KeyboardButton = KeyboardButton(text='/rand_fox')

keyboard: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
    keyboard=[[b1]],
    resize_keyboard=True,
    one_time_keyboard=True
)

