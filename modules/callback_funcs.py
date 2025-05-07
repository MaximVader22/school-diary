from aiogram import F
from aiogram.types import CallbackQuery, BufferedInputFile, InputMediaPhoto
from aiogram.filters.state import StateFilter
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from modules.FSM_states import *
from modules.create_menu import *
import modules.schedule_json as sch


router_callback = Router()

DAYS_OF_WEEK = ('Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье')


# Профиль
@router_callback.callback_query(F.data == "profile")
async def profile(call: CallbackQuery):
    await call.answer()
    await call.message.answer("Это ваш профиль",
                              reply_markup=create_profile_menu())


# Расписание
@router_callback.callback_query(F.data == "schedule", StateFilter(Form.idle))
async def schedule(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(Form.edit_schedule)
    await call.message.answer("Выберите действие:",
                              reply_markup=create_schedule_menu(call.from_user.id))


# Старосты
@router_callback.callback_query(F.data == "elders", StateFilter(Form.idle))
async def elders(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(Form.edit_elders)
    await call.message.answer("Выберите действие:",
                              reply_markup=create_elders_menu(call.from_user.id))


# Просмотр расписания
@router_callback.callback_query(F.data == "view_schedule")
async def view_schedule(call: CallbackQuery):
    await call.answer()

    schedule_data = sch.load_schedule('schedule.json')

    if not schedule_data:
        await call.message.answer("Расписание пустое")
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
@router_callback.callback_query(F.data == "edit_remind_time", StateFilter(Form.idle))
async def edit_remind_time_prompt(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(Form.edit_remind_time)
    await call.message.answer("Введите время напоминания в формате ЧЧ:ММ :")


# Добавление предмета
@router_callback.callback_query(F.data == "add_subject")
async def add_subject_prompt(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(Form.edit_schedule_add)
    await call.message.answer(
        "Введите день недели, предмет, время начала и время конца через запятую (например: `Понедельник, Математика, 8:30, 9:10`):")

# Удаление предмета
@router_callback.callback_query(F.data == "remove_subject")
async def remove_subject_prompt(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(Form.edit_schedule_delete)
    await call.message.answer("Введите название предмета для удаления:")

# Добавление старосты
@router_callback.callback_query(F.data == "add_elder")
async def add_elder_prompt(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(Form.edit_elders_add)
    await call.message.answer("Введите имя пользователя нового старосты:")

# Удаление старосты
@router_callback.callback_query(F.data == "remove_elder")
async def remove_elder_prompt(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(Form.edit_elders_delete)
    await call.message.answer("Введите имя пользователя старосты, которого надо удалить:")

# Создание объявления
@router_callback.callback_query(F.data == "create_announcement")
async def create_announcement(call: CallbackQuery, state: FSMContext):
    if not has_elder_rights(call.from_user.id):
        await call.answer("У вас нет прав для этого.")
        return
    await state.set_state(Form.create_announcement)
    await call.message.answer("Введите ваше объявление или напишите *Отмена*, если вы не хотите создавать объявление",
                              parse_mode=ParseMode.MARKDOWN_V2)

# Создание объявления о мероприятии
@router_callback.callback_query(F.data == "create_event")
async def create_event(call: CallbackQuery, state: FSMContext):
    if not has_elder_rights(call.from_user.id):
        await call.answer("У вас нет прав для этого")
        return
    await state.set_state(Form.create_event)
    await call.message.answer("Введите ваше объявление в формате _Название, Время \(ДД\.ММ\.ГГГГ ЧЧ:ММ\)_ или напишите *Отмена*, если вы не хотите создавать объявление", parse_mode=ParseMode.MARKDOWN_V2)

# В главное меню
@router_callback.callback_query(F.data == "back_to_main")
async def back_to_main(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(Form.idle)
    await call.message.answer("Вы вернулись в главное меню",
                              reply_markup=create_main_menu(call.from_user.id))

# Домашнее задание
@router_callback.callback_query(F.data == "homework", StateFilter(Form.idle))
async def homework(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(Form.edit_homework)
    await call.message.answer("Выберите действие:",
                                reply_markup=create_homework_menu(call.from_user.id))

# Добавление домашнего задания
@router_callback.callback_query(F.data == "add_homework")
async def add_homework_prompt(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(Form.edit_homework_add)
    await call.message.answer("Введите дату истечения домашнего задания, название предмета и описание, разделяя их знаком ';'\nЧтобы добавить изображение, отправьте его отдельно.\nВы можете добавить до 10 изображений")

# Просмотр домашнего задания
@router_callback.callback_query(F.data == "list_homework")
async def list_homework_prompt(call: CallbackQuery, state: FSMContext):
    await call.answer()
    collection = list_homework()

    if len(collection) == 0:
        await call.message.answer("Нет домашнего задания")
        return

    builder = InlineKeyboardBuilder()

    for work in collection:
        builder.add(InlineKeyboardButton(text=f"[{work[0]}] {work[1]} - {work[3]}", callback_data=f"homework_get_{work[0]}", ))

    builder.adjust(1)
    builder.add(InlineKeyboardButton(text="Назад", callback_data="back_to_main"))

    await call.message.answer("Список домашнего задания:", reply_markup=builder.as_markup())


# Просмотр описания домашнего задания
@router_callback.callback_query(F.data.startswith('homework_get_'))
async def homework_get_prompt(call: CallbackQuery, state: FSMContext):
    homework_id = int(call.data.replace("homework_get_", ""))
    homework = get_homework_data(homework_id)

    text = f"Домашнее задание по {homework['subject']}:\n\nОписание: {homework['description']}\n\nИстекает {homework['expires']}"

    photo_files = []
    first_photo = True
    for index, photo in enumerate(homework["photos"]):
        file_buffer = BufferedInputFile(photo[2], filename=f"file_{index}.jpg")
        if first_photo:
            media_photo = InputMediaPhoto(media=file_buffer, caption=text)
            first_photo = False
        else:
            media_photo = InputMediaPhoto(media=file_buffer)
        photo_files.append(media_photo)

    ##await call.message.answer(text, reply_markup=InlineKeyboardBuilder()
    ##                        .add(InlineKeyboardButton(text="Назад", callback_data="list_homework"))
    ##                        .as_markup())
    await call.message.answer_media_group(photo_files)
