from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def skip_btn (lang="ru"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Пропустить", callback_data="skip_media")]
    ])

def main_menu_keyboard(lang="ru"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎮 Категории игр", callback_data="view_categories")],
        [InlineKeyboardButton(text="💬 Оставить отзыв", callback_data="leave_review")],
        [InlineKeyboardButton(text="🆘 Поддержка", url="https://t.me/NyaOffical")]
    ])

def category_keyboard(lang="ru"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎯 PUBG", callback_data="cat_pubg")],
        [InlineKeyboardButton(text="⚔️ Mobile Legends", callback_data="cat_ml")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu")]
    ])



def admin_panel_keyboard(lang="ru"):
    if lang == "ru":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
            [InlineKeyboardButton(text="➕ Добавить аккаунт", callback_data="add_account")],
            [InlineKeyboardButton(text="🗑 Удалить аккаунт", callback_data="delete_account")],
            [InlineKeyboardButton(text="💬 Посмотреть отзыв", url="https://t.me/nyashoptest61616")],
            [InlineKeyboardButton(text="⬅️ Меню пользователя", callback_data="back_to_user_menu")]
        ])



def get_category_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎯 PUBG", callback_data="acc_cat_pubg")],
        [InlineKeyboardButton(text="⚔️ Mobile Legends", callback_data="acc_cat_ml")],
        [InlineKeyboardButton(
            text="⬅Назад",
            callback_data="admin_menu"
        )]
    ])

def get_accounts_keyboard(accounts, lang="ru"):
    buttons = []
    for acc in accounts:
        acc_id, category, login, password, price, description = acc
        acc_text = f"{category.upper()} | {price}₽"
        buttons.append([
            InlineKeyboardButton(
                text=acc_text,
                callback_data=f"select_account:{acc_id}"
            )
        ])
    buttons.append([
        InlineKeyboardButton(
            text="⬅️ Назад" ,
            callback_data="back_to_categories"
        )
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_account_actions_keyboard(acc_id, lang="ru"):
    text_pay = "💳 Оплатить"
    text_back = "⬅️ Назад"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=text_pay, callback_data=f"pay_{acc_id}")],
        [InlineKeyboardButton(text=text_back, callback_data="back_to_category")]
    ])


def get_payment_keyboard(account_id: int, lang="ru"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Оплатить",
                callback_data=f"pay_account:{account_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="🔙 Назад",
                callback_data="back_to_accounts"
            )
        ]
    ])
def admin_decision_keyboard(user_id: int, account_data: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Одобрить",callback_data=f"approve:{user_id}:{account_data}"),
        InlineKeyboardButton(text="❌ Отказать",callback_data=f"reject:{user_id}")]
    ])