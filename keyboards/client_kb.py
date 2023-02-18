from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, KeyboardButtonPollType, InlineKeyboardButton, \
    InlineKeyboardMarkup

# --- Клавиатура для выбора пола ---
male_button = InlineKeyboardButton(text='Мужской ♂',
                                   callback_data='male')
female_button = InlineKeyboardButton(text='Женский ♀',
                                     callback_data='female')
undefined_button = InlineKeyboardButton(text='🤷 Пока не ясно',
                                        callback_data='undefined_gender')

gender_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [male_button],
        [female_button],
        [undefined_button]
    ]
)

# --- Клавиатура для главного меню ---
show_info = InlineKeyboardButton(text='Просмотр информации о себе',
                                 callback_data='/show_user_info')
random_fox_img = InlineKeyboardButton(text='Рандомная фотка лисы',
                                      callback_data='/rand_fox')
object_detection = InlineKeyboardButton(text='Детекция объектов на изображении',
                                        callback_data='/img_detection')
drop_user_from_database = InlineKeyboardButton(text='Удалить информацию о себе из бд',
                                               callback_data='/drop_user')

menu_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [show_info],
        [object_detection],
        [random_fox_img],
        [drop_user_from_database]
    ]
)

back_to_menu = KeyboardButton(text='/start')
to_menu = ReplyKeyboardMarkup(
    keyboard=[
        [back_to_menu]
    ],
    resize_keyboard=True,
)


# --- Клавиатура для выбора модели ---
yolo_model = InlineKeyboardButton(text='Yolov8',
                                  callback_data='yolo')
yoloseg_model = InlineKeyboardButton(text='Yolov8seg',
                                     callback_data='yoloseg')
midas_model = InlineKeyboardButton(text='MiDaS',
                                   callback_data='midas')
detectron_model = InlineKeyboardButton(text='Detectron2',
                                       callback_data='detectron')

choose_model_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [yolo_model],
        [yoloseg_model],
        [midas_model],
        [detectron_model]
    ]
)
