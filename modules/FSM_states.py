from aiogram.filters.state import State, StatesGroup


# Состояния пользователя (нужны для перехода по меню)
class Form(StatesGroup):
    idle = State()
    edit_homework = State()
    edit_homework_add = State()
    edit_homework_delete = State()
    edit_schedule = State()
    edit_schedule_delete = State()
    edit_schedule_add = State()
    edit_elders = State()
    edit_elders_delete = State()
    edit_elders_add = State()
    edit_remind_time = State()
    create_announcement = State()
    create_event = State()
