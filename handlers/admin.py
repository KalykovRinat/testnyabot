from aiogram import Router
from config import ADMIN_IDS,BOT_TOKEN
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from keyboards.inline import admin_panel_keyboard,get_category_keyboard
from utils.language import get_message
from states.add_account import AddAccountState
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from database.db import insert_account
from database.db import delete_account_by_id,get_all_accounts  # Предположим, эти функции есть
from handlers.is_admin import IsAdmin
import re
router = Router()
def extract_price(text: str) -> int | None:
    clean = re.sub(r"[^\d.,]", "", text)

    if "," in clean and "." not in clean:
        clean = clean.replace(",", ".")

    try:
        float_price = float(clean)
        return int(float_price)
    except ValueError:
        return None
@router.message(Command("admin"), IsAdmin())
async def admin_panel(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("У вас нет доступа к админ-панели.")
        return
    await message.answer("🔐 Админ-панель:", reply_markup=admin_panel_keyboard())

@router.callback_query(F.data == "add_account")
async def start_adding_account(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.message.answer("⛔ У тебя нет прав для добавления аккаунтов.")
        return
    data = await state.get_data()
    lang = data.get("lang", "ru")
    await state.set_state(AddAccountState.choosing_category)
    await callback.message.answer("Выбери категорию: pubg или ml",reply_markup=get_category_keyboard(lang))

@router.callback_query(F.data == "confirm_add_account")
async def confirm_account(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    category = data["category"]
    login = data["login"]
    password = data["password"]
    price_som = data["price_som"]
    price_rub = data["price_rub"]
    binding = data["binding"]
    description = data["description"]
    media_id = data.get("media_id")
    media_type = data.get("media_type")
    binding = data.get("binding")
    # вставка в БД
    await insert_account(category, login, password, price_som,price_rub, description, binding, media_id, media_type)

    await callback.message.answer("Аккаунт добавлен!")
    await state.clear()
    await callback.answer()

@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")
    msg = "📊 Здесь будет статистика."
    await callback.message.edit_text(msg, reply_markup=admin_panel_keyboard(lang))

from states.add_account import AddAccountState
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

@router.callback_query(F.data.startswith("acc_cat_"))
async def set_category(callback: CallbackQuery, state: FSMContext):
    category = callback.data.split("_")[-1]
    await state.update_data(category=category)
    await state.set_state(AddAccountState.entering_login)
    await callback.message.edit_text("Введите логин:")

@router.message(AddAccountState.entering_login)
async def get_login(message: Message, state: FSMContext):
    await state.update_data(login=message.text)
    await state.set_state(AddAccountState.entering_password)
    await message.answer("Введите пароль:")


@router.message(AddAccountState.entering_password)
async def get_password(message: Message, state: FSMContext):
    await state.update_data(password=message.text)
    await state.set_state(AddAccountState.entering_price_som)
    await message.answer("Введите цену в <b>сомах</b>:")
@router.message(AddAccountState.entering_price_som)
async def get_price_som(message: Message, state: FSMContext):
    if not message.text.strip().isdigit():
        await message.answer("❌ Введите только число для сомов.")
        return
    await state.update_data(price_som=int(message.text.strip()))
    await state.set_state(AddAccountState.entering_price_rub)
    await message.answer("Теперь введите цену в <b>рублях</b>:")
@router.message(AddAccountState.entering_price_rub)
async def get_price_rub(message: Message, state: FSMContext):
    if not message.text.strip().isdigit():
        await message.answer("❌ Введите только число для рублей.")
        return
    await state.update_data(price_rub=int(message.text.strip()))
    await state.set_state(AddAccountState.entering_description)
    await message.answer("Введите описание аккаунта:")


@router.message(AddAccountState.entering_description)
async def process_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Укажи, через что привязан аккаунт (например: Google, Facebook, Email и т.д.)")
    await state.set_state(AddAccountState.entering_binding)

@router.message(AddAccountState.entering_binding)
async def get_binding(message: Message, state: FSMContext):
    await state.update_data(binding=message.text)
    await message.answer("Загрузите фото или видео аккаунта:")
    await state.set_state(AddAccountState.uploading_media)

@router.message(AddAccountState.uploading_media, F.photo | F.video)
async def handle_media(message: Message, state: FSMContext):
    media_id = None
    media_type = None

    if message.photo:
        media_id = message.photo[-1].file_id
        media_type = "photo"
    elif message.video:
        media_id = message.video.file_id
        media_type = "video"
    else:
        await message.answer("Пожалуйста, отправьте фото или видео.")
        return

    await state.update_data(media_id=media_id, media_type=media_type)
    await message.answer("Подтвердите добавление аккаунта. ✅", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Добавить", callback_data="confirm_add_account")],
        [InlineKeyboardButton(text="Отмена", callback_data="cancel_add_account")]
    ]))
    await state.set_state(AddAccountState.confirming)



@router.message(AddAccountState.entering_description)
async def get_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    data = await state.get_data()

    from database.db import add_account
    await add_account(
        category=data['category'],
        login=data['login'],
        password=data['password'],
        price=data['price'],
        description=data['description']
    )

    await message.answer("✅ Аккаунт успешно добавлен!")
    await state.clear()

@router.callback_query(F.data == "delete_account")
async def delete_account_prompt(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        return await callback.answer("Нет доступа.")

    accounts = await get_all_accounts()  # Возвращает список (id, category, login, price)
    if not accounts:
        return await callback.message.edit_text("Нет доступных аккаунтов для удаления.", reply_markup=admin_panel_keyboard())

    buttons = [
        [InlineKeyboardButton(
            text=f"{cat.upper()} | {login} | {price_som}Сом | {price_rub}Р ",
            callback_data=f"del_acc:{acc_id}"
        )] for acc_id, cat, login, price_som, price_rub in accounts
    ]
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_menu")])

    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.edit_text("Выберите аккаунт для удаления:", reply_markup=markup)

@router.callback_query(F.data.startswith("del_acc:"))
async def delete_selected_account(callback: CallbackQuery):
    acc_id = int(callback.data.split(":")[1])
    await delete_account_by_id(acc_id)  # Функция из db.py
    await callback.message.edit_text(f"✅ Аккаунт с ID {acc_id} удалён.", reply_markup=admin_panel_keyboard())
@router.callback_query(F.data == "admin_menu")
async def ba_to_admin_menu(callback: CallbackQuery):
    await callback.message.edit_text("🔐 Админ-панель:", reply_markup=admin_panel_keyboard())

@router.callback_query(F.data == "manage_categories")
async def manage_categories(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")
    msg = "📂 Управление категориями пока недоступно." if lang == "ru" else "📂 Category management is not available yet."
    await callback.message.edit_text(msg, reply_markup=admin_panel_keyboard(lang))

@router.callback_query(F.data == "view_reviews")
async def view_reviews(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")
    msg = "💬 Здесь будут отзывы пользователей." if lang == "ru" else "💬 User reviews will be displayed here."
    await callback.message.edit_text(msg, reply_markup=admin_panel_keyboard(lang))

@router.callback_query(F.data == "back_to_user_menu")
async def back_to_user_menu(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")
    from keyboards.inline import main_menu_keyboard
    from utils.language import get_message
    await callback.message.edit_text(get_message(lang, "main_menu"), reply_markup=main_menu_keyboard(lang))
