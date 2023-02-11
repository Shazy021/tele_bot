import requests
from aiogram import Dispatcher, F, html
import logging
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile, ReplyKeyboardRemove
from setings import API_FOX_URL
from create_bot import bot, dp
from models import yolo, mod
from keyboards import client_kb
from aiogram.fsm.state import State, StatesGroup
from config_data.user_db import add_user, user_check, get_user_name


class FSMClient(StatesGroup):
    name = State()
    age = State()
    photo = State()


user_dict = {}


# Этот хэндлер будет срабатывать на команду "/start"
@dp.message(Command(commands=['start']))
async def process_start_command(message: Message, state: FSMContext) -> None:
    user_status = user_check(message.from_user.id)
    if user_status:
        await state.set_state(FSMClient.name)
        await message.answer(
            'Добро пожаловать!\nВведи своё имя:',
            reply_markup=ReplyKeyboardRemove(),
        )
        await message.delete()
        user_dict[message.from_user.id] = {}
    else:
        await message.answer(
            f'Привет {get_user_name(message.from_user.id)} 👋'
        )

# Хендлер на команду "/cancel"
@dp.message(Command(commands=['cancel']))
@dp.message(F.text.casefold() == 'cancel')
async def cancel_handler(message: Message, state: FSMContext) -> None:
    """
    Для отмены действий
    """
    del user_dict[message.from_user.id]
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info("Завершение операции %r", current_state)
    await state.clear()
    await message.answer(
        'Завершено',
        reply_markup=ReplyKeyboardRemove(),
    )

# Хендлер на ввод имени
@dp.message(FSMClient.name)
async def process_name(message: Message, state: FSMContext) -> None:
    user_dict[message.from_user.id]['name'] = message.text
    await state.update_data(name=message.text)
    await message.answer(
        f'Рады тебя видеть, {html.quote(message.text)}!\nВведите ваш возраст:'
    )
    await state.set_state(FSMClient.age)

# Хендлер на проверку ввода возраста
@dp.message(FSMClient.age, (lambda message: 4 > int(message.text) < 120))
async def age_warning(message: Message):
    await message.answer(
        'Возраст должен быть целым числом от 4 до 120!\n\n'
        'Попробуйте еще раз\n\nЕсли вы хотите прервать '
        'заполнение анкеты - отправьте команду /cancel'
    )

# Хендлер на запись возраста + перенос данных из user_dict в DB
@dp.message(FSMClient.age, lambda message: message.text.isdigit())
async def process_name(message: Message, state: FSMContext) -> None:
    user_dict[message.from_user.id]['age'] = message.text
    await state.update_data(age=int(message.text))

    await message.answer(
        f'Ваше Имя: {user_dict[message.from_user.id]["name"]}\n'
        f'Ваш Возраст: {user_dict[message.from_user.id]["age"]}\n'
        'Спасибо за вашу информацию'
    )

    add_user(message.from_user.id, user_dict)
    await state.clear()
    del user_dict[message.from_user.id]


# Хендлер на команду 'rand_fox'
async def process_fox_command(message: Message):
    await message.answer('Привет, как на счет фоточек лисы?', reply_markup=ReplyKeyboardRemove())
    await message.delete()
    fox_response = requests.get(API_FOX_URL)
    ERROR_TEXT: str = 'Здесь должна была быть картинка с лисой :('
    if fox_response.status_code == 200:
        fox_link = fox_response.json()['image']
        await message.answer_photo(fox_link)
    else:
        await message.answer(ERROR_TEXT)


# Хендлер на команду /get_detect
async def photo_detection(message: Message):
    await message.answer('Пожалуйста загрузите фотографию')


# Хендлер на фотки
async def send_photo_echo(message: Message):
    await message.reply_photo(message.photo[0].file_id)
    file = await bot.get_file(message.photo[-1].file_id)
    file_path = file.file_path
    await bot.download_file(file_path, "./data/test.png")
    yolo.yolo_predict('./data/test.png')
    await bot.send_photo(chat_id=message.chat.id, photo=FSInputFile("./data/result.png"))
    midas_names = "MiDaS_small"
    mid = mod.MiDas(models_name=midas_names, photo_pth="./data/test.png")
    await bot.send_photo(chat_id=message.chat.id, photo=FSInputFile("./data/midas.png"))


def regster_handlers_client(dp: Dispatcher):
    # dp.message.register(process_start_command, Command(commands=['start', 'help']))
    dp.message.register(process_fox_command, Command(commands=['rand_fox']))
    dp.message.register(send_photo_echo, F.photo)
