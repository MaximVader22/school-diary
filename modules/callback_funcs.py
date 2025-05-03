from aiogram import F
from aiogram.types import CallbackQuery
from aiogram.filters.state import StateFilter
from aiogram import Router, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from modules.FSM_states import *
from modules.create_menu import *
import modules.schedule_json as sch

router = Router()

DAYS_OF_WEEK = ('Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье')

# Профиль
@router.callback_query(F.data == "profile")
async def profile(call: CallbackQuery):
    await call.answer()
    await call.message.answer("Это ваш профиль. Здесь пока ничего нет.",
                              reply_markup=create_profile_menu(call.from_user.id))


# Расписание
@router.callback_query(F.data == "schedule", StateFilter(Form.idle))
async def schedule(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(Form.edit_schedule)
    await call.message.answer("Выберите действие:",
                              reply_markup=create_schedule_menu(call.from_user.id))


# Старосты
@router.callback_query(F.data == "elders", StateFilter(Form.idle))
async def elders(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(Form.edit_elders)
    await call.message.answer("Выберите действие:",
                              reply_markup=create_elders_menu(call.from_user.id))


# Просмотр расписания
@router.callback_query(F.data == "view_schedule")
async def view_schedule(call: CallbackQuery):
    await call.answer()

    schedule_data = sch.load_schedule('schedule.json')

    if not schedule_data:
        await call.message.answer("Расписание пустое.")
        return

    response_parts = ['Ваше текущее расписание:\n ', '', '', '', '', '', '']

    for day, lessons in schedule_data.items():
        response_part = f"{day}:\n"
        for lesson in lessons:
            response_part += f'{lesson["name"]}: {lesson["start_time"]}-{lesson["end_time"]}\n'
        response_part += '\n'
        response_parts[DAYS_OF_WEEK.index(day)] += response_part

    await call.message.answer(' '.join(response_parts))


# Установка времени напоминания
@router.callback_query(F.data == "edit_remind_time", StateFilter(Form.idle))
async def edit_remind_time_prompt(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(Form.edit_remind_time)
    await call.message.answer("Введите время напоминания в формате HH:MM :")

@router.callback_query(F.data == "add_subject")
async def add_subject_prompt(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(Form.edit_schedule_add)
    await call.message.answer(
        "Введите день недели, предмет, время начала и время конца через запятую (например: `Monday, Math, 8:30, 9:10`):")

# Удаление предмета
@router.callback_query(F.data == "remove_subject")
async def remove_subject_prompt(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(Form.edit_schedule_delete)
    await call.message.answer("Введите название предмета для удаления:")

# Добавление старосты
@router.callback_query(F.data == "add_elder")
async def add_elder_prompt(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(Form.edit_elders_add)
    await call.message.answer("Введите имя пользователя нового старосты:")

# Удаление старосты
@router.callback_query(F.data == "remove_elder")
async def remove_elder_prompt(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(Form.edit_elders_delete)
    await call.message.answer("Введите имя пользователя старосты, которого надо удалить:")

# Создание объявления
@router.callback_query(F.data == "create_announcement")
async def create_announcement(call: CallbackQuery, state: FSMContext):
    if not has_elder_rights(call.from_user.id):
        await call.answer("У вас нет прав для этого.")
        return
    await state.set_state(Form.create_announcement)
    await call.message.answer("Введите ваше объявление или напишите *Отмена*, если вы не хотите создавать объявление",
                              parse_mode=ParseMode.MARKDOWN_V2)

# Создание объявления о мероприятии
@router.callback_query(F.data == "create_event")
async def create_event(call: CallbackQuery, state: FSMContext):
    if not has_elder_rights(call.from_user.id):
        await call.answer("У вас нет прав для этого.")
        return
    await state.set_state(Form.create_event)
    await call.message.answer("Введите ваше объявление в формате _Название, Время \(DD\.MM\.YYYY HH:MM\)_ или напишите *Отмена*, если вы не хотите создавать объявление", parse_mode=ParseMode.MARKDOWN_V2)

# В главное меню
@router.callback_query(F.data == "back_to_main")
async def back_to_main(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(Form.idle)
    await call.message.answer("Вы вернулись в главное меню.",
                              reply_markup=create_main_menu(call.from_user.id))
