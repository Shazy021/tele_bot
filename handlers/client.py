import requests
from aiogram import F, html
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile, ReplyKeyboardRemove, CallbackQuery
from keyboards.client_kb import gender_markup, menu_markup, to_menu, choose_model_markup
from models.detectron import Detectron2
from models.utils import class_names
from models.yolo import YOLOv8

from models.yolo_seg import YOLOSeg
from setings import API_FOX_URL
from create_bot import bot, dp
from models import mod
from aiogram.fsm.state import State, StatesGroup
from config_data.user_db import add_user, user_check, get_user_name, get_user_age, get_user_gender, \
    drop_user_from_users, get_detection_info, add_detections

user_dict = {}


# Машина состояний для регистрации
class FSMRegisterClient(StatesGroup):
    name = State()
    gender = State()
    age = State()
    photo = State()


# Мвшина состояний для детекции
class FSMImgDetection(StatesGroup):
    img = State()


# Этот хэндлер будет срабатывать на команду "/start"
@dp.message(Command(commands=['start']))
async def process_start_command(message: Message, state: FSMContext) -> None:
    user_status = user_check(message.from_user.id)
    if user_status:
        await message.answer(
            f'Привет {get_user_name(message.from_user.id)} 👋',
            reply_markup=ReplyKeyboardRemove(),
        )
        await message.answer(
            f'Выбери команду 👇',
            reply_markup=menu_markup
        )
        await message.delete()

    else:
        await state.set_state(FSMRegisterClient.name)
        await message.answer(
            'Добро пожаловать!\nВведи своё имя:',
            reply_markup=ReplyKeyboardRemove(),
        )
        await message.delete()
        user_dict[message.from_user.id] = {}


# Хендлер на команду "/cancel"
@dp.message(Command(commands=['cancel']))
@dp.message(F.text.casefold() == 'cancel')
async def cancel_handler(message: Message, state: FSMContext) -> None:
    global user_dict
    user_dict = {}

    await state.clear()
    await message.answer(
        'Завершено',
        reply_markup=to_menu,
    )


# Хендлер на ввод имени
@dp.message(FSMRegisterClient.name)
async def process_name(message: Message, state: FSMContext) -> None:
    user_dict[message.from_user.id]['name'] = message.text
    await state.update_data(name=message.text)
    await message.answer(
        f'Рады тебя видеть, {html.quote(message.text)}!'
    )
    await message.delete()
    # Отправляем пользователю сообщение с клавиатурой
    await message.answer(text=f'Спасибо!\n\nУкажите ваш пол:',
                         reply_markup=gender_markup)
    # Устанавливаем состояние ожидания выбора пола
    await state.set_state(FSMRegisterClient.gender)


# Этот хэндлер будет срабатывать, если во время выбора пола
# будет введено/отправлено что-то некорректное
@dp.message(FSMRegisterClient.gender)
async def warning_not_gender(message: Message):
    await message.answer(text='Пожалуйста, пользуйтесь кнопками '
                              'при выборе пола\n\nЕсли вы хотите прервать '
                              'заполнение анкеты - отправьте команду /cancel')


# Хендлер на отлов команд с кнопок выбора пола
@dp.message(FSMRegisterClient.gender)
@dp.callback_query(lambda callback: callback.data in ['male', 'female', 'undefined_gender'])
async def process_gender_press(callback: CallbackQuery, state: FSMContext):
    # C помощью менеджера контекста сохраняем пол (callback.data нажатой
    # кнопки) в хранилище, по ключу "gender"
    user_dict[callback.from_user.id]["gender"] = str(callback.data)
    # Удаляем сообщение с кнопками, потому что следующий этап - ввод возраста
    # чтобы у пользователя не было желания тыкать кнопки
    await callback.message.delete()
    await callback.message.answer(text='Спасибо! А теперь введите '
                                       'свой возраст:')
    # Устанавливаем состояние ожидания загрузки фото
    await state.set_state(FSMRegisterClient.age)


# Хендлер на проверку ввода возраста
@dp.message(FSMRegisterClient.age, (lambda message: not (message.text.isdigit()) or (4 > int(message.text) < 120)))
async def age_warning(message: Message):
    await message.answer(
        'Возраст должен быть целым числом от 4 до 120!\n\n'
        'Попробуйте еще раз\n\nЕсли вы хотите прервать '
        'заполнение анкеты - отправьте команду /cancel'
    )


# Хендлер на запись возраста + перенос данных из user_dict в DB
@dp.message(FSMRegisterClient.age, lambda message: message.text.isdigit())
async def process_name(message: Message, state: FSMContext) -> None:
    user_dict[message.from_user.id]['age'] = message.text
    await state.update_data(age=int(message.text))

    await message.answer(
        f'Ваше Имя: {user_dict[message.from_user.id]["name"]}\n'
        f'Ваш Возраст: {user_dict[message.from_user.id]["age"]}\n'
        f'Ваш Пол: {user_dict[message.from_user.id]["gender"]}\n'
        'Спасибо за вашу информацию'
    )
    await message.delete()

    add_user(message.from_user.id, user_dict)
    await state.clear()
    del user_dict[message.from_user.id]


# Хендлер на callback с меню 'rand_fox'
@dp.callback_query(lambda callback: callback.data in ['/rand_fox'])
async def process_fox_command(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer('Держи рандомную фоточку лисы', reply_markup=ReplyKeyboardRemove())
    fox_response = requests.get(API_FOX_URL)
    ERROR_TEXT: str = 'Здесь должна была быть картинка с лисой :('
    if fox_response.status_code == 200:
        fox_link: str = fox_response.json()['image']  # ссылка на фото
        await callback.message.answer_photo(fox_link, reply_markup=to_menu)
    else:
        await callback.message.answer(ERROR_TEXT)


# Хендлер на callback /get_detect
@dp.callback_query(lambda callback: callback.data in ['/img_detection'])
async def photo_detection(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer('Выберите модель.', reply_markup=choose_model_markup)

    await state.set_state(FSMImgDetection.img)


# Хендлер на загрузку изображения
@dp.callback_query(lambda callback: callback.data in ['yolo', 'yoloseg', 'midas', 'detectron'])
async def choose_model(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    global model
    model = callback.data

    await callback.message.answer('Пожалуйста загрузите изображение')

    await state.set_state(FSMImgDetection.img)


# Хендлер на фотки пришедшие c callback /img_detection
@dp.message(FSMImgDetection.img, F.photo)
async def send_photo_echo(message: Message, state: FSMContext):
    file = await bot.get_file(message.photo[-1].file_id)
    file_path = file.file_path
    await bot.download_file(file_path, "./data/test.png")
    await message.reply_photo(message.photo[0].file_id)

    global model
    match model:
        case 'yolo':
            model = YOLOv8('./data/test.png')
            res_dict = {}

            for key in model.res_labels:
                if key in res_dict:
                    res_dict[key] += 1
                else:
                    res_dict[key] = 1
            print(res_dict)

            add_detections(message.from_user.id, res_dict)
            await bot.send_photo(chat_id=message.chat.id, photo=FSInputFile("./data/result.png"), reply_markup=to_menu)
            del res_dict

        case 'yoloseg':
            model = YOLOSeg('./models/yolov8l-seg.onnx', conf_thres=0.1, iou_thres=0.1)
            res_dict = {}

            for key in model.class_ids:
                if class_names[key] in res_dict:
                    res_dict[class_names[key]] += 1
                else:
                    res_dict[class_names[key]] = 1
            print(res_dict)

            add_detections(message.from_user.id, res_dict)
            await bot.send_photo(chat_id=message.chat.id, photo=FSInputFile('./data/yolo-seg.png'),
                                 reply_markup=to_menu)
            del res_dict

        case 'midas':
            midas_names = "MiDaS_small"
            mod.MiDas(models_name=midas_names, photo_pth="./data/test.png")
            await bot.send_photo(chat_id=message.chat.id, photo=FSInputFile("./data/midas.png"), reply_markup=to_menu)

        case 'detectron':
            try:
                model = Detectron2('./data/test.png', conf_thres=0.5)
                res_dict = {}

                for key in model.classes:
                    if class_names[key] in res_dict:
                        res_dict[class_names[key]] += 1
                    else:
                        res_dict[class_names[key]] = 1
                print(res_dict)
                del model

                add_detections(message.from_user.id, res_dict)
                await bot.send_photo(chat_id=message.chat.id, photo=FSInputFile("./data/detectron.png"),
                                     reply_markup=to_menu)
            except:
                await message.answer('Пожалуйста попробуйте загрузить другое изображение')
                await state.set_state(FSMImgDetection.img)
                return None

    await message.delete()
    await state.clear()


# Хендлер на проверку отправки фотографий
@dp.message(FSMImgDetection.img)
async def warning_not_gender(message: Message):
    await message.delete()
    await message.answer(
        'Пожалуйста, загрузите ИЗОБРАЖЕНИЕ!!!'
        '\n\nЕсли вы хотите прервать '
        'команду отправки изображения - отправьте команду /cancel'
    )


# Хендлер на показ информации о пользователе
@dp.callback_query(lambda callback: callback.data in ['/show_user_info'])
async def user_info(callback: CallbackQuery):
    await callback.message.delete()
    user_id = callback.from_user.id
    name, age, gender = get_user_name(user_id), get_user_age(user_id), get_user_gender(user_id)

    info = get_detection_info(user_id)
    sorted_tuples = sorted(info.items(), key=lambda item: item[1])[::-1]
    info = {k: v for k, v in sorted_tuples}
    keys = list(info.keys())[1:]
    text = ''

    for i, key in enumerate(keys):
        text += '   ' + str(keys[i][:1]).upper() + keys[i][1::] + ': ' + str(info[key]) + "\n"

    await callback.message.answer(
        f'Информация о пользователе {name}:\n\n'
        f'Возраст: {age}\n'
        f'Пол: {gender}\n\n'
        f'За всё время, вы задетектировали:\n'
        f'{text}\n\n'
        f'Для выхода в главное меню нажмите на кнопку',
        reply_markup=to_menu
    )


# Хендлер на удаление записи в таблице users
@dp.callback_query(lambda callback: callback.data in ['/drop_user'])
async def user_drop(callback: CallbackQuery):
    await callback.message.delete()
    drop_user_from_users(callback.from_user.id)
    await callback.message.answer(
        f'Ваша запись удалена',
        reply_markup=to_menu
    )
