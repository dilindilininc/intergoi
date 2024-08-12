import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram import F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from app.dbmanager import get_db, DBManager
from config.config import BOT_TOKEN
import app.keyboard as kb
from app.admin import router as admin_router
from app.supervisor import router as supervisor_router

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

dp.include_router(admin_router)
dp.include_router(supervisor_router)

# Initialize DBManager
db = get_db()
db_manager = DBManager(db)

# Dictionary to store page states
user_pages = {}


# Function to escape markdown characters
def escape_markdown(text):
    escape_characters = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '.', '!']
    for char in escape_characters:
        text = text.replace(char, f'\\{char}')
    return text


# Function to format reasons
def format_reasons(reasons):
    reason_mapping = {
        "terrorism_onanism": "Терроризм и Онанизм",
        "secret_info": "Раскрытие секретной/совершенно секретной информации",
        "uk_vjl_violation": "Нарушение статьи УК ВЖЛ"
    }

    # Debug: Log the incoming reasons
    logging.info(f"Incoming reasons: {reasons}")

    # Filter out any reasons that are not in the mapping
    formatted_reasons = [reason_mapping.get(reason, reason) for reason in reasons if reason in reason_mapping]

    # Debug: Log the formatted reasons
    logging.info(f"Formatted reasons: {formatted_reasons}")

    # Join results with a comma
    return ", ".join(formatted_reasons) if formatted_reasons else "Причина не указана"


# Function to get a formatted string of goy details
def format_goy(goy):
    # Debug: Log the goy details
    logging.info(f"Goy details: {goy}")

    reasons = format_reasons(goy.get("Reason", []))
    # Escape markdown special characters in the fields
    fio = escape_markdown(goy['FIO'])
    birthday = escape_markdown(goy['Birthday'])
    reasons = escape_markdown(reasons)

    return (
        f"*РАЗЫСКИВАЕТСЯ!*\n"
        f"ФИО: {fio}\n"
        f"Дата рождения: {birthday}\n"
        f"Причина: {reasons}"
    )


# Handler for '✡ | Список | ✡' button
@dp.message(F.text == "✡ | Список | ✡")
async def list_goys(message: types.Message):
    goys = db_manager.collection_list.find()
    goys_list = list(goys)  # Convert cursor to list
    if not goys_list:
        await message.answer("Нет данных о гоях.")
        return

    user_pages[message.from_user.id] = {
        "goys": goys_list,
        "current_page": 0
    }

    await send_goy_page(message.from_user.id, 0)


# Function to send a goy page
async def send_goy_page(user_id, page_number):
    goys_data = user_pages.get(user_id, {})
    goys_list = goys_data.get("goys", [])
    if not goys_list:
        return

    # Ensure page_number is within bounds
    page_number = max(0, min(page_number, len(goys_list) - 1))
    goy = goys_list[page_number]

    formatted_goy = format_goy(goy)

    # Create navigation buttons
    keyboard_buttons = []
    if page_number > 0:
        keyboard_buttons.append(InlineKeyboardButton(text="« Назад", callback_data=f"goy_page_{page_number - 1}"))
    if page_number < len(goys_list) - 1:
        keyboard_buttons.append(InlineKeyboardButton(text="Далее »", callback_data=f"goy_page_{page_number + 1}"))

    # Only create InlineKeyboardMarkup if there are buttons
    keyboard = InlineKeyboardMarkup(inline_keyboard=[keyboard_buttons]) if keyboard_buttons else None

    await bot.send_message(
        user_id,
        formatted_goy,
        parse_mode="Markdown",
        reply_markup=keyboard
    )


# Handler for pagination callbacks
@dp.callback_query(F.data.startswith("goy_page_"))
async def handle_pagination(call: CallbackQuery):
    user_id = call.from_user.id
    page_number = int(call.data.split("_")[-1])

    await send_goy_page(user_id, page_number)
    await call.answer()  # Acknowledge the callback


# /start command handler
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        text=(
            f"✡ Шалом, {message.from_user.first_name}!\n"
            "Я виртуальный агент Интергой!\n"
            "Наша организация занимается поиском и отлавливанием гоев и харамников, нарушивших законы Великой Жидомасонской Ложи!\n\n"
            "❓ У тебя есть информация о вероятном местонахождении гоя? Ты хочешь отправить жалобу на вероятного гоя? Используй этого бота!\n\n"
            "[✡ Связаться с нами](https://t.me/sionatlantida)"
        ),
        parse_mode="Markdown",
        reply_markup=kb.main_keyboard  # Use the main_keyboard directly as it's not a function
    )


# Handler for 'Связь' button
@dp.message(F.text == "✡ | Связь | ✡")
async def contact(message: types.Message):
    await message.answer("Шалом! По всем вопросам к @sionatlantida")


# Handler for 'Задать вопрос' button
@dp.message(F.text == "❓ Задать вопрос")
async def ask_question(message: types.Message):
    await message.answer("Задай мне вопрос", reply_markup=kb.question_keyboard)  # Use the question_keyboard directly


# Main function to start polling
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
