from aiogram import Router
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import Message
from aiogram import F

from modules.FSM_states import *
from modules.create_menu import *
import modules.schedule_json as sch
import modules.notifier as notifier

router2 = Router()

DAYS_OF_WEEK = ('Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье')

# Обработчик команды /start
@router2.message(Command("start"))
async def send_welcome(message: Message, state: FSMContext):
    create_user(message.from_user.id, None, is_admin=are_users_empty())
    set_username(message.from_user.id, message.from_user.username)
    await state.set_state(Form.idle)
    await message.answer("Приветствую! Используйте кнопки для навигации.",
                         reply_markup=create_main_menu(message.from_user.id))

@router2.message(F.text, StateFilter(Form.edit_remind_time))
async def handle_edit_remind_time(message: Message, state: FSMContext):
    time = message.text

    if not is_right_time_format(time):
        await message.answer(f"Укажите время в формате HH:MM.")
        return

    set_remind_time(message.from_user.id, time)
    notifier.add_notifier(message.from_user.id, time)
    await message.answer(f"Время напоминания установлено.")



@router2.message(F.text, StateFilter(Form.edit_schedule_add))
async def handle_add_subject(message: Message, state: FSMContext):
    if not has_elder_rights(message.from_user.id):
        await message.answer("У вас нет прав старосты.")
        return
    try:
        if message.text == "Отмена":
            await state.set_state(Form.idle)
            await message.answer("Вы возвращены в главное меню", reply_markup=create_main_menu(message.from_user.id))
            return

        await message.delete()

        day, subject, start_time, end_time = map(str.strip, message.text.split(',', 3))
        assert day in DAYS_OF_WEEK

        if not is_right_time_format(start_time) or not is_right_time_format(end_time):
            await message.answer("Неверный формат ввода времени: HH:MM")
            return

        sch.add_schedule('schedule.json', day, subject, start_time, end_time)
        await message.answer(f"Предмет '{subject}' успешно добавлен на {day}.")
    except ValueError:
        await message.answer("Неверный формат ввода. Пожалуйста, используйте формат: день, предмет.")
    except AssertionError:
        await message.answer("Неверный формат ввода дня недели.")



@router2.message(F.text, StateFilter(Form.edit_schedule_delete))
async def handle_remove_subject(message: Message, state: FSMContext):
    if not has_elder_rights(message.from_user.id):
        await message.answer("У вас нет прав старосты.")
        return

    subject = message.text.strip()
    sch.remove_one_subject('schedule.json', subject)
    await message.answer(f"Попытка удалить предмет '{subject}' завершена.")



@router2.message(F.text, StateFilter(Form.edit_elders_add))
async def handle_add_elder(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("У вас нет прав администратора.")
        return

    username = message.text.strip()

    if not username_exists(username):
        await message.answer("Не найден пользователь с таким именем.")
        return

    set_elder(username, True)
    await message.answer(f"{username} назначен старостой.")



@router2.message(F.text, StateFilter(Form.edit_elders_delete))
async def handle_remove_elder(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("У вас нет прав администратора.")
        return

    username = message.text.strip()

    if not username_exists(username):
        await message.answer("Не найден пользователь с таким именем.")
        return

    set_elder(id_from_username(username), False)
    await message.answer(f"{username} больше не староста.")

@router2.message(F.text, StateFilter(Form.edit_homework_add))
async def handle_add_homework(message: Message, state: FSMContext):
    content = message.text.split(";")
 
    if len(content) != 3:
        await message.answer("Неверное количество аргументов")
        return
 
    date = content[0]
    subject = content[1]
    description = content[2]
 
    if not is_right_homework_date_format(date):
        await message.answer("Неверный формат даты")
        return
 
    data = await state.get_data()
    photos = data.get("photos", [])
 
    add_homework(date, subject, description, photos)
 
    await message.answer(f"Домашнее задание было добавлено")
    await state.clear()
