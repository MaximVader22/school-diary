from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters.state import State, StatesGroup, StateFilter
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio
from aiogram.fsm.context import FSMContext
import schedule_json as sch
from new_db import *

# Вставьте ваш токен вместо 'YOUR_BOT_TOKEN'
with open('http_api.txt') as f:
    token = f.read().strip()

# Состояния
class Form(StatesGroup):
    idle = State()
    edit_schedule = State()

# Глобальные переменные
json_name = 'schedule.json'

# Инициализация бота и диспетчера
bot = Bot(token=token)
dp = Dispatcher()
router = Router()
dp.include_router(router)

'''
### Кнопки ###
'''
def create_main_menu():
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text='Профиль', callback_data='profile'),
        InlineKeyboardButton(text='Расписание', callback_data='schedule')
    )
    builder.adjust(1)
    return builder.as_markup()

def create_schedule_menu(user_id):
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text='Просмотреть расписание', callback_data='view_schedule'),
        InlineKeyboardButton(text='Назад', callback_data='back_to_main')
    )
    if has_elder_rights(user_id):
        builder.add(
            InlineKeyboardButton(text='Добавить предмет', callback_data='add_subject'),
            InlineKeyboardButton(text='Удалить предмет', callback_data='remove_subject'),
        )
    builder.adjust(1)
    return builder.as_markup()

# Обработчик команды /start
@router.message(Command("start"))
async def send_welcome(message: Message, state: FSMContext):
    create_user(message.from_user.id)
    await state.set_state(Form.idle)
    await message.answer("Приветствую! Используйте кнопки для навигации.", reply_markup=create_main_menu())

'''
### Callback-функции ###
'''
# Профиль
@router.callback_query(F.data == "profile")
async def profile(call: CallbackQuery):
    await call.answer()
    await call.message.answer("Это ваш профиль. Здесь пока ничего нет.")

# Расписание
@router.callback_query(F.data == "schedule", StateFilter(Form.idle))
async def schedule(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(Form.edit_schedule)
    await call.message.answer("Выберите действие:", reply_markup=create_schedule_menu(call.message.from_user.id))

# Просмотр расписания
@router.callback_query(F.data == "view_schedule")
async def view_schedule(call: CallbackQuery):
    await call.answer()
    schedule_data = sch.load_schedule(json_name)
    if not schedule_data:
        await call.message.answer("Расписание пустое.")
        return
    response = "Ваше текущее расписание:\n"
    for day, lessons in schedule_data.items():
        response += f"{day}: {', '.join(lessons)}\n"
    await call.message.answer(response)

# Добавление предмета
@router.callback_query(F.data == "add_subject")
async def add_subject_prompt(call: CallbackQuery):
    await call.answer()
    await call.message.answer("Введите день недели и предмет через запятую (например, Monday, Math):")

@router.message(F.text, StateFilter(Form.edit_schedule))
async def handle_add_subject(message: Message, state: FSMContext):
    if not has_elder_rights(message.from_user.id):
        await message.answer("У вас нет прав старосты.")
        return
    try:
        day, subject = map(str.strip, message.text.split(',', 1))
        sch.add_schedule(json_name, day, [subject])
        await message.answer(f"Предмет '{subject}' успешно добавлен на {day}.")
    except ValueError:
        await message.answer("Неверный формат ввода. Пожалуйста, используйте формат: день, предмет.")

# Удаление предмета
@router.callback_query(F.data == "remove_subject")
async def remove_subject_prompt(call: CallbackQuery):
    await call.answer()
    await call.message.answer("Введите название предмета для удаления:")

@router.message(F.text, StateFilter(Form.edit_schedule))
async def handle_remove_subject(message: Message, state: FSMContext):
    if not has_elder_rights(message.from_user.id):
        await message.answer("У вас нет прав старосты.")
        return
    subject = message.text.strip()
    sch.remove_one_subject(json_name, subject)
    await message.answer(f"Попытка удалить предмет '{subject}' завершена.")

# В главное меню
@router.callback_query(F.data == "back_to_main", StateFilter(Form.edit_schedule))
async def back_to_main(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(Form.idle)
    await call.message.answer("Вы вернулись в главное меню.", reply_markup=create_main_menu())

'''
### MAIN-функция ###
### Запуск бота ###
'''
async def main():
    await bot.delete_webhook()
    init_database()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
