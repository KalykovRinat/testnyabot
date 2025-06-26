def get_message(lang: str, key: str) -> str:
    return MESSAGES.get(lang, MESSAGES["ru"]).get(key, "")

MESSAGES = {
    "ru": {
        "start": "Добро пожаловать! Выберите язык 👇",
        "language_selected": "Язык выбран: Русский 🇷🇺",
        "main_menu": "📋 Главное меню. Выберите действие:",
        "category_title": "Выберите игру:"
    }
}

async def get_lang(user_id: int) -> str:
    # Пока возвращаем "ru" по умолчанию, позже можно добавить сохранение языка в БД
    return "ru"

