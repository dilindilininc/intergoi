from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Main keyboard
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✡ | Список | ✡")],
        [KeyboardButton(text="✡ | Связь | ✡")]
    ],
    resize_keyboard=True
)

# Question keyboard
question_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Как меня зовут?")],
        [KeyboardButton(text="Что я могу?")],
        [KeyboardButton(text="Вернуться в главное меню")]
    ],
    resize_keyboard=True
)

# Admin panel keyboard
admin_panel_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Добавить гоя")],
        [KeyboardButton(text="Удалить гоя")]
    ],
    resize_keyboard=True
)

# Inline keyboard for crime categories
crime_categories_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Терроризм и Онанизм", callback_data="terrorism_onanism")],
        [InlineKeyboardButton(text="Раскрытие секретной/совершенно секретной информации", callback_data="secret_info")],
        [InlineKeyboardButton(text="Нарушение статьи УК ВЖЛ", callback_data="uk_vjl_violation")]
    ]
)

# Inline keyboard for delete criteria
delete_criteria_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="По ФИО", callback_data="delete_by_name")],
        [InlineKeyboardButton(text="По ID", callback_data="delete_by_id")]
    ]
)
