from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.dbmanager import get_db, DBManager
import config.config as conf

router = Router()

class OfficerForm(StatesGroup):
    user_id = State()
    officer_id = State()
    secret_code = State()

@router.message(Command("add_officer"))
async def add_officer(message: types.Message, state: FSMContext):
    if message.from_user.id == 918230700:
        await message.answer("Введите ТГ-ID офицера:")
        await state.set_state(OfficerForm.user_id)
    else:
        await message.answer("У вас нет прав на выполнение данной команды..")

@router.message(OfficerForm.user_id)
async def process_user_id(message: types.Message, state: FSMContext):
    await state.update_data(user_id=message.text)
    await message.answer("Введите Officer-ID (16 симв.):")
    await state.set_state(OfficerForm.officer_id)

@router.message(OfficerForm.officer_id)
async def process_officer_id(message: types.Message, state: FSMContext):
    await state.update_data(officer_id=message.text)
    await message.answer("Введите секретный ключ офицера:")
    await state.set_state(OfficerForm.secret_code)

@router.message(OfficerForm.secret_code)
async def process_secret_code(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = data['user_id']
    officer_id = data['officer_id']
    secret_code = message.text

    db = DBManager(get_db())
    db.collection_officers.insert_one({
        "user_id": user_id,
        "officer_id": officer_id,
        "secret_code": secret_code
    })

    await message.answer(f"Офицер с ID {officer_id} добавлен успешно.")
    await state.clear()
