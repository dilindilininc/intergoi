from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.dbmanager import get_db, DBManager
import app.keyboard as kb

# Define the router
router = Router()

# FSM States
class AdminPanel(StatesGroup):
    awaiting_key = State()
    awaiting_command = State()
    awaiting_goy_full_name = State()
    awaiting_goy_birth_date = State()
    awaiting_goy_reason = State()
    awaiting_delete_criteria = State()
    awaiting_delete_value = State()

# Command /panel to start the admin process
@router.message(Command("panel"))
async def panel_start(message: Message, state: FSMContext):
    db = get_db()
    db_manager = DBManager(db)
    officer = db_manager.find_officer_by_user_id(str(message.from_user.id))

    if officer:
        await message.answer("Введите секретный ключ:")
        await state.update_data(officer=officer)  # Store officer in FSM context
        await state.set_state(AdminPanel.awaiting_key)
    else:
        print(f"Пользователь {message.from_user.id} не найден в коллекции офицеров.")
        await message.answer("У вас нет прав для доступа к этой команде.")

# Handler to check the officer's key
@router.message(AdminPanel.awaiting_key)
async def check_key(message: Message, state: FSMContext):
    data = await state.get_data()
    officer = data.get("officer")

    if officer:
        if message.text == officer.get("secret_code"):
            await message.answer(
                "Доступ к панели администратора предоставлен.",
                reply_markup=kb.admin_panel_keyboard
            )
            await state.set_state(AdminPanel.awaiting_command)
        else:
            await message.answer("Неверный ключ. Попробуйте снова.")
    else:
        await message.answer("Произошла ошибка. Попробуйте начать заново с /panel.")

# Command /exit to leave admin panel
@router.message(Command("exit"))
async def exit_panel(message: Message, state: FSMContext):
    await state.set_state(None)  # Завершаем состояние FSM
    await message.answer("Вы вышли из панели администратора.",
                         reply_markup=kb.main_keyboard)  # Возвращаем основную клавиатуру

# Handler for adding a goy
@router.message(F.text == "Добавить гоя", AdminPanel.awaiting_command)
async def add_goy_start(message: Message, state: FSMContext):
    await message.answer("Введите ФИО гоя:")
    await state.set_state(AdminPanel.awaiting_goy_full_name)

@router.message(AdminPanel.awaiting_goy_full_name)
async def add_goy_full_name(message: Message, state: FSMContext):
    goy_full_name = message.text
    db = get_db()
    db_manager = DBManager(db)

    # Проверяем, существует ли уже гой с таким ФИО
    existing_goy = db_manager.find_goy_by_full_name(goy_full_name)

    if existing_goy:
        await state.update_data(goy_full_name=goy_full_name)
        await message.answer("Этот гой уже существует. Выберите причину для обновления:",
                             reply_markup=kb.crime_categories_keyboard)
        await state.set_state(AdminPanel.awaiting_goy_reason)
    else:
        await state.update_data(goy_full_name=goy_full_name)
        await message.answer("Введите дату рождения гоя (в формате ГГГГ-ММ-ДД):")
        await state.set_state(AdminPanel.awaiting_goy_birth_date)

@router.message(AdminPanel.awaiting_goy_birth_date)
async def add_goy_birth_date(message: Message, state: FSMContext):
    await state.update_data(goy_birth_date=message.text)
    await message.answer("Выберите причину объявления в розыск:", reply_markup=kb.crime_categories_keyboard)
    await state.set_state(AdminPanel.awaiting_goy_reason)

# Обработчик причин с использованием F.data
@router.callback_query(F.data.in_(["terrorism_onanism", "secret_info", "uk_vjl_violation"]))
async def add_goy_reason(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    goy_full_name = data.get("goy_full_name")
    goy_reason = call.data

    db = get_db()
    db_manager = DBManager(db)

    # Проверяем, существует ли уже гой с таким ФИО
    existing_goy = db_manager.find_goy_by_full_name(goy_full_name)

    if existing_goy:
        # Добавляем причину к существующей записи как список
        current_reasons = existing_goy.get('Reason', [])
        if isinstance(current_reasons, str):
            current_reasons = [current_reasons]  # Преобразуем в список, если это строка

        # Проверяем, если причина уже существует, чтобы не дублировать
        if goy_reason not in current_reasons:
            current_reasons.append(goy_reason)
            db_manager.update_goy(existing_goy['_id'], {"Reason": current_reasons})
            await call.message.answer(f"Причина '{goy_reason}' успешно добавлена к существующему гою!")
        else:
            await call.message.answer("Эта причина уже была добавлена к гою.")
    else:
        # Логика для добавления нового гоев
        goy_birth_date = data.get("goy_birth_date")
        new_goy_id = db_manager.add_goy(goy_full_name, goy_birth_date, [goy_reason])  # Сохраняем как список

        await call.message.answer(f"Гой успешно добавлен!\nID: {new_goy_id}\nФИО: {goy_full_name}\nДата рождения: {goy_birth_date}\nПричина: {goy_reason}")

    await state.set_state(AdminPanel.awaiting_command)

# Handler for deleting a goy
@router.message(F.text == "Удалить гоя", AdminPanel.awaiting_command)
async def delete_goy_start(message: Message, state: FSMContext):
    await message.answer("Выберите метод поиска для удаления гоев:", reply_markup=kb.delete_criteria_keyboard)
    await state.set_state(AdminPanel.awaiting_delete_criteria)

@router.callback_query(F.data == "delete_by_id")  # Обработчик для поиска по ID
async def delete_goy_by_id(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Введите ID для поиска:")
    await state.set_state(AdminPanel.awaiting_delete_value)

@router.callback_query(F.data == "delete_by_name")  # Обработчик для поиска по ФИО
async def delete_goy_by_name(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Введите ФИО для поиска:")
    await state.set_state(AdminPanel.awaiting_delete_value)

@router.message(AdminPanel.awaiting_delete_value)
async def delete_goy_value(message: Message, state: FSMContext):
    search_value = message.text
    db = get_db()
    db_manager = DBManager(db)

    # Проверяем, является ли search_value целым числом (в виде строки)
    if search_value.isdigit():
        # Если search_value является числом, преобразуем в int и ищем по ID
        deleted = db_manager.delete_goy(int(search_value))
    else:
        # Если это строка, ищем только по ФИО
        deleted = db_manager.delete_goy(search_value)

    if deleted:
        await message.answer("Гой успешно удалён.")
    else:
        await message.answer("Гой не найден. Попробуйте снова.")

    await state.set_state(AdminPanel.awaiting_command)
