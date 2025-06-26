from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menureply_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Главное меню")],
            [KeyboardButton(text="просто")],
            [KeyboardButton(text="Просто")]
        ],
        resize_keyboard=True
    )
