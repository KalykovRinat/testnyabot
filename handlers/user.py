from gc import callbacks
from account_bot.config import ADMIN_IDS, Review, BOT_TOKEN, chat_admin
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery,InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from keyboards.inline import  main_menu_keyboard, category_keyboard,get_account_actions_keyboard,get_accounts_keyboard,get_payment_keyboard
from database.db import get_accounts_by_category
from database.db import get_account_by_id
from aiogram.exceptions import TelegramBadRequest
from keyboards.inline import admin_decision_keyboard
from account_bot.keyboards.reply import main_menureply_keyboard
from account_bot.utils.language import get_lang

class FeedbackStates(StatesGroup):
    waiting_for_text = State()
    waiting_for_media = State()

class PaymentStates(StatesGroup):
    waiting_for_screenshot = State()




router = Router()

async def show_account_by_index(message: Message, state: FSMContext):
    data = await state.get_data()
    accounts = data["accounts"]
    index = data["acc_index"]
    lang = data.get("lang", "ru")

    if index < 0 or index >= len(accounts):
        await message.answer("Нет данных.")
        return

    acc = accounts[index]
    acc_id = acc["id"]
    login = acc["login"]
    price_som = acc["price_som"]
    price_rub = acc["price_rub"]
    description = acc["description"]
    media_id = acc.get("media_id")
    media_type = acc.get("media_type")

    text = (
        f"🔐 <b>Логин:</b> {login}\n"
        f"💰 <b>Цена:</b> {price_som}Сом / {price_rub}Рубль \n"
        f"📝 <b>Описание:</b> {description}\n"
        f"📦 <b>Аккаунт {index + 1} из {len(accounts)}</b>"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⬅️", callback_data="acc_prev") if index > 0 else InlineKeyboardButton(
                text=" ",callback_data="ignore"),
            InlineKeyboardButton(text="➡️", callback_data="acc_next") if index < len(accounts) - 1 else InlineKeyboardButton(
                text=" ",callback_data="ignore")],
        [InlineKeyboardButton(text="🛒 Выбрать", callback_data=f"pay_account:{acc_id}")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="view_categories")]
    ])

    if media_type == "photo":
        await message.answer_photo(photo=media_id, caption=text, reply_markup=keyboard)
    elif media_type == "video":
        await message.answer_video(video=media_id, caption=text, reply_markup=keyboard)
    else:
        await message.answer(text, reply_markup=keyboard)

@router.message(F.text == "/start")
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await state.set_data({"lang": "ru"})
    await message.answer("👋 Добро пожаловать! Выберите действие:", reply_markup=main_menureply_keyboard())

@router.callback_query(F.data == "view_categories")
async def view_categories(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")
    title = "📂 Категории игр"
    markup = category_keyboard(lang)

    if callback.message.text:
        await callback.message.edit_text(title, reply_markup=markup)
    else:
        await callback.message.edit_reply_markup(reply_markup=markup)
        await callback.message.answer(title, reply_markup=markup)

    await callback.answer()
@router.message(lambda message: message.text == "Главное меню")
async def MainMenu(message: Message):
    await message.answer("👋 Добро пожаловать! Выберите действие:",reply_markup=main_menu_keyboard())

@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")

    try:
        await callback.message.delete()
        await callback.message.answer(
            get_message(lang, "main_menu"),
            reply_markup=main_menu_keyboard(lang)
        )
    except Exception as e:
        await callback.answer("Ошибка при обновлении меню.")
    else:
        await callback.answer()


@router.callback_query(F.data.startswith("cat_"))
async def show_accounts(callback: CallbackQuery, state: FSMContext):
    category = callback.data.split("_")[-1]
    lang = await get_lang(callback.from_user.id)
    accounts = await get_accounts_by_category(category)

    if not accounts:
        await callback.message.edit_text("Нет доступных аккаунтов.")
        return
    await state.update_data(accounts=accounts, acc_index=0, acc_category=category)
    await show_account_by_index(callback.message, state)

@router.callback_query(F.data == "acc_next")
async def next_account(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    index = data.get("acc_index", 0) + 1
    await state.update_data(acc_index=index)
    await callback.message.delete()
    await show_account_by_index(callback.message, state)


@router.callback_query(F.data == "acc_prev")
async def prev_account(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    index = data.get("acc_index", 0) - 1
    await state.update_data(acc_index=index)
    await callback.message.delete()
    await show_account_by_index(callback.message, state)


@router.callback_query(F.data == "ignore")
async def ignore_callback(callback: CallbackQuery):
    await callback.answer()

@router.callback_query(F.data.startswith("pay_account:"))
async def select_account(callback: CallbackQuery):
    parts = callback.data.split(":")
    if len(parts) < 2 or not parts[1].isdigit():
        await callback.answer("Некорректный ID аккаунта.")
        return

    acc_id = int(parts[1])
    lang = await get_lang(callback.from_user.id)

    # Получаем аккаунт по ID
    accounts = list(await get_accounts_by_category("pubg")) + list(await get_accounts_by_category("ml"))
    account = next((acc for acc in accounts if acc["id"] == acc_id), None)

    if not account:
        await callback.message.answer("Аккаунт не найден.")
        return

    acc_id = account["id"]
    category = account["category"]
    login = account["login"]
    password = account["password"]
    price_som = account["price_som"]
    price_rub = account["price_rub"]
    description = account["description"]

    text = f"<b>{category.upper()}</b>\nЦена: {price_som}Сом/{price_rub}Рубль\nЛогин: <code>{login}</code>\nОписание: {description}"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплатить", callback_data=f"pa_account:{acc_id}")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="view_categories")]
    ])
    try:
        await callback.message.edit_text(text, reply_markup=keyboard)
    except TelegramBadRequest:
        await callback.message.delete()
        await callback.message.answer(text, reply_markup=keyboard)


@router.callback_query(F.data.startswith("pa_account:"))
async def start_payment(callback: CallbackQuery, state: FSMContext):
    acc_id = int(callback.data.split(":")[1])
    lang = await get_lang(callback.from_user.id)

    await state.update_data(acc_id=acc_id, lang=lang)

    text = (
        "💸 Отправьте <b>скриншот чека</b> после оплаты на номер: <code>+996 XXX XXX XXX</code>\n\n"
        "После этого мы проверим оплату и отправим вам данные аккаунта."
    )
    await callback.message.edit_text(text)
    await state.set_state(PaymentStates.waiting_for_screenshot)

@router.message(PaymentStates.waiting_for_screenshot)
async def handle_payment_screenshot(message: Message, state: FSMContext):
    if not message.photo:
        await message.answer("Пожалуйста, отправьте именно фото скриншота.")
        return

    data = await state.get_data()
    acc_id = data.get("acc_id")
    lang = data.get("lang", "ru")

    account = await get_account_by_id(acc_id)

    if not account:
        await message.answer("Аккаунт не найден.")
        await state.clear()
        return

    account_data = f"{account['login']}|{account['password']}|{account.get('binding', 'N/A')}"

    # Распаковка данных из SQL
    account_dict = {
        "id": account["id"],
        "category": account["category"],
        "login": account["login"],
        "password": account["password"],
        "price_som": account["price_som"],
        "price_rub": account["price_rub"],
        "description": account["description"]
    }

    caption = (
        f"🧾 Новый чек от @{message.from_user.username or message.from_user.id}\n"
        f"🎮 Игра: {account_dict['category'].upper()}\n"
        f"🆔 ID: {account_dict['id']}\n"
        f"👤 Логин: <code>{account_dict['login']}</code>\n"
        f"🔑 Пароль: <code>{account_dict['password']}</code>\n"
        f"💰 Цена: {account_dict['price_som']} \n"
        f"📝 Описание: {account_dict['description']}"
    )

    for admin_id in chat_admin if isinstance(chat_admin, list) else [chat_admin]:
        await message.bot.send_photo(
            chat_id=chat_admin,
            photo=message.photo[-1].file_id,
            caption=caption,
            reply_markup=admin_decision_keyboard(
                message.from_user.id,
                account_data
            )
        )

    await message.answer(
        "✅ Ваш чек отправлен. Ожидайте подтверждения от администратора."
    )
    await state.clear()


@router.callback_query(F.data == "leave_review")
async def start_review_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer ("Напишите ваш отзыв:")
    await state.set_state(FeedbackStates.waiting_for_text)
    await callback.answer()

@router.message(FeedbackStates.waiting_for_text, F.text)

async def get_review_text(message: Message, state: FSMContext):
    text = message.text.strip()
    if not text:
        await message.answer("Пожалуйста, введите текст отзыва.")
        return

    await state.update_data(review_text=text)

    skip_btn = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Пропустить", callback_data="skip_media")]
    ])

    await message.answer("Теперь отправьте фото или видео, или нажмите 'Пропустить'", reply_markup=skip_btn)
    await state.set_state(FeedbackStates.waiting_for_media)

Bot = BOT_TOKEN
@router.message(FeedbackStates.waiting_for_media, F.photo | F.video)
async def get_review_media(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    username = message.from_user.username or f"id:{message.from_user.id}"
    review_text = f"👤 @{username}\n\n" + data.get("review_text", "Без текста")
    channel_id = Review  # Заменить на ваш

    if message.photo:
        file_id = message.photo[-1].file_id
        await bot.send_photo(channel_id, file_id, caption=review_text)
    elif message.video:
        file_id = message.video.file_id
        await bot.send_video(channel_id, file_id, caption=review_text)

    await message.answer("Спасибо за ваш отзыв!")
    await state.clear()

@router.callback_query(F.data == "skip_media", FeedbackStates.waiting_for_media)
async def skip_media_callback(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    username = callback.from_user.username or f"id:{callback.from_user.id}"
    review_text = f"👤 @{username}\n\n" + data.get("review_text", "Без текста")
    channel_id = Review

    await bot.send_message(channel_id, review_text)
    await callback.message.answer("Спасибо за отзыв!")
    await state.clear()
    await callback.answer()


@router.callback_query(F.data.startswith("account_"))
async def show_account_options(callback: CallbackQuery, state: FSMContext):
    account_id = int(callback.data.split("_")[1])
    data = await state.get_data()
    lang = data.get("lang", "ru")

    await callback.message.edit_text(
        text="Вы выбрали аккаунт. Что хотите сделать?",
        reply_markup=get_payment_keyboard(account_id, lang)
    )

@router.callback_query(F.data.startswith("approve:"))
async def approve_user(callback: CallbackQuery):
    _, user_id, acc_data = callback.data.split(":", 2)

    try:
        login, password, binding = acc_data.split("|")
        message = (
            "✅ Ваша оплата успешно выполнена.\n\n"
            f"🔐 Логин: {login}\n"
            f"🔑 Пароль: {password}\n"
            f"🔗 Привязка: {binding}"
        )
        await callback.bot.send_message(int(user_id), message)
        await callback.message.edit_caption("Заявка одобрена.")
    except TelegramBadRequest:
        await callback.answer("Ошибка при отправке сообщения пользователю.", show_alert=True)
    except Exception as e:
        await callback.answer(f"Ошибка обработки: {e}", show_alert=True)

@router.callback_query(F.data.startswith("reject:"))
async def reject_user(callback: CallbackQuery):
    _, user_id = callback.data.split(":")

    try:
        await callback.bot.send_message(int(user_id), "❌ Ваша заявка на покупку аккаунта была отклонена.")
        await callback.message.edit_caption("Заявка отклонена.")
    except TelegramBadRequest:
        await callback.answer("Ошибка при отправке сообщения пользователю.", show_alert=True)
