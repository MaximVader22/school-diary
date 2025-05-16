from aiogram import F
from aiogram.types import CallbackQuery, BufferedInputFile, InputMediaPhoto
from aiogram.filters.state import StateFilter
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

import main
from modules.FSM_states import *
from modules.create_menu import *
import modules.schedule_json as sch


router_callback = Router()

DAYS_OF_WEEK = ('Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье')


# Профиль
@router_callback.callback_query(F.data == "profile")
async def profile(call: CallbackQuery):
    await call.answer()
    user_id = call.from_user.id
    remind_time = get_remind_time(user_id)
    admin = is_admin(user_id)
    elder = is_elder(user_id)

    remind_time = "Нет" if remind_time is None else remind_time
    admin = "✅" if admin else "❌"
    elder = "✅" if elder else "❌"

    await call.message.answer(f"🏠 Это ваш профиль\n⏱️ Время напоминания: {remind_time}\n⚙️ Админ: {admin}\n📖 Староста: {elder}",
                              reply_markup=create_profile_menu())
    await main.delete_prev_message(call.from_user.id, call.message.message_id, False)


# Расписание
@router_callback.callback_query(F.data == "schedule", StateFilter(Form.idle))
async def schedule(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(Form.edit_schedule)
    await call.message.answer("🔎 Выберите действие:",
                              reply_markup=create_schedule_menu(call.from_user.id))
    await main.delete_prev_message(call.from_user.id, call.message.message_id)


# Старосты
@router_callback.callback_query(F.data == "elders", StateFilter(Form.idle))
async def elders(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(Form.edit_elders)
    await call.message.answer("🔎 Выберите действие:",
                              reply_markup=create_elders_menu(call.from_user.id))
    await main.delete_prev_message(call.from_user.id, call.message.message_id)


# Просмотр расписания
@router_callback.callback_query(F.data == "view_schedule")
async def view_schedule(call: CallbackQuery):
    await call.answer()

    schedule_data = sch.load_schedule('schedule.json')

    if not schedule_data:
        await call.message.answer("❌ Расписание пустое")
        return

    response_parts = ['Ваше текущее расписание:\n ', '', '', '', '', '', '']

    for day, lessons in schedule_data.items():
        response_part = f"{day}:\n"
        for lesson in lessons:
            response_part += f'{lesson["name"]}: {lesson["start_time"]}-{lesson["end_time"]}\n'
        response_part += '\n'
        response_parts[DAYS_OF_WEEK.index(day)] += response_part

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text='Назад',
                             callback_data='back_to_main')
    )

    await call.message.answer(' '.join(response_parts), reply_markup=builder.as_markup())
    await main.delete_prev_message(call.from_user.id, call.message.message_id, False)


# Установка времени напоминания
@router_callback.callback_query(F.data == "edit_remind_time", StateFilter(Form.idle))
async def edit_remind_time_prompt(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(Form.edit_remind_time)
    await call.message.answer("✏️ Введите время напоминания в формате ЧЧ:ММ или 'Удалить', чтобы удалить напоминание:")
    await main.delete_prev_message(call.from_user.id, call.message.message_id)


# Добавление предмета
@router_callback.callback_query(F.data == "add_subject")
async def add_subject_prompt(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(Form.edit_schedule_add)
    await call.message.answer(
        "✏️ Введите день недели, предмет, время начала и время конца через запятую (например: `Понедельник, Математика, 8:30, 9:10`):")
    await main.delete_prev_message(call.from_user.id, call.message.message_id)

# Удаление предмета
@router_callback.callback_query(F.data == "remove_subject")
async def remove_subject_prompt(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(Form.edit_schedule_delete)
    await call.message.answer("✏️ Введите название предмета для удаления:")
    await main.delete_prev_message(call.from_user.id, call.message.message_id)

# Добавление старосты
@router_callback.callback_query(F.data == "add_elder")
async def add_elder_prompt(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(Form.edit_elders_add)
    await call.message.answer("✏️ Введите имя пользователя нового старосты:")
    await main.delete_prev_message(call.from_user.id, call.message.message_id)

# Удаление старосты
@router_callback.callback_query(F.data == "remove_elder")
async def remove_elder_prompt(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(Form.edit_elders_delete)
    await call.message.answer("✏️ Введите имя пользователя старосты, которого надо удалить:")
    await main.delete_prev_message(call.from_user.id, call.message.message_id)

# Создание объявления
@router_callback.callback_query(F.data == "create_announcement")
async def create_announcement(call: CallbackQuery, state: FSMContext):
    if not has_elder_rights(call.from_user.id):
        await call.answer("❌ У вас нет прав для этого.")
        return
    await state.set_state(Form.create_announcement)
    await call.message.answer("✏️ Введите ваше объявление или напишите *Отмена*, если вы не хотите создавать объявление",
                              parse_mode=ParseMode.MARKDOWN_V2)
    await main.delete_prev_message(call.from_user.id, call.message.message_id)

# Создание объявления о мероприятии
@router_callback.callback_query(F.data == "create_event")
async def create_event(call: CallbackQuery, state: FSMContext):
    if not has_elder_rights(call.from_user.id):
        await call.answer("❌ У вас нет прав для этого")
        return
    await state.set_state(Form.create_event)
    await call.message.answer("✏️ Введите ваше объявление в формате _Название, Время \(ДД\.ММ\.ГГГГ ЧЧ:ММ\)_ или напишите *Отмена*, если вы не хотите создавать объявление", parse_mode=ParseMode.MARKDOWN_V2)
    await main.delete_prev_message(call.from_user.id, call.message.message_id)

# В главное меню
@router_callback.callback_query(F.data == "back_to_main")
async def back_to_main(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(Form.idle)
    await call.message.answer("Вы вернулись в главное меню",
                              reply_markup=create_main_menu(call.from_user.id))
    await main.delete_prev_message(call.from_user.id, call.message.message_id)

# Домашнее задание
@router_callback.callback_query(F.data == "homework")
async def homework(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(Form.edit_homework)
    await call.message.answer("🔎 Выберите действие:",
                                reply_markup=create_homework_menu(call.from_user.id))
    await main.delete_prev_message(call.from_user.id, call.message.message_id)

# Добавление домашнего задания
@router_callback.callback_query(F.data == "add_homework")
async def add_homework_prompt(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(Form.edit_homework_add)
    await call.message.answer("""
✏️ Введите домашнее задание в формате:
{Дата истечения};{Название предмета};{Описание}

🖼️ Если вы хотите добавить изображения, отправьте их отдельными сообщениями перед основным.

❌ Чтобы отменить добавление домашнего задания, напишите Отмена
    """)
    await main.delete_prev_message(call.from_user.id, call.message.message_id)

# Просмотр домашнего задания
@router_callback.callback_query(F.data == "list_homework")
async def list_homework_prompt(call: CallbackQuery, state: FSMContext):
    await call.answer()
    collection = list_homework()

    if len(collection) == 0:
        await call.message.answer("❌ Нет домашнего задания")
        return

    builder = InlineKeyboardBuilder()

    for work in collection:
        builder.add(InlineKeyboardButton(text=f"[{work[0]}] {work[1]} - {work[3]}", callback_data=f"homework_get_{work[0]}", ))

    builder.add(InlineKeyboardButton(text="Назад", callback_data="back_to_main"))

    builder.adjust(1)

    await call.message.answer("📃 Список домашнего задания:", reply_markup=builder.as_markup())
    await main.delete_prev_message(call.from_user.id, call.message.message_id, False)


# Просмотр описания домашнего задания
@router_callback.callback_query(F.data.startswith('homework_get_'))
async def homework_get_prompt(call: CallbackQuery, state: FSMContext):
    homework_id = int(call.data.replace("homework_get_", ""))
    work = get_homework_data(homework_id)

    text = f"🏠 Домашнее задание по {work['subject']}:\n\n📝 Описание: {work['description']}\n\n⏰ Истекает {work['expires']}"

    photo_files = []
    first_photo = True
    for index, photo in enumerate(work["photos"]):
        file_buffer = BufferedInputFile(photo[2], filename=f"file_{index}.jpg")
        if first_photo:
            media_photo = InputMediaPhoto(media=file_buffer, caption=text)
            first_photo = False
        else:
            media_photo = InputMediaPhoto(media=file_buffer)
        photo_files.append(media_photo)

    await main.delete_prev_message(call.from_user.id, call.message.message_id, False)

    if len(photo_files) > 0:
        await call.message.answer_media_group(photo_files)
    else:
        await call.message.answer(text)
