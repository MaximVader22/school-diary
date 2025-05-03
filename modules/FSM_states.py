from aiogram.filters.state import State, StatesGroup

class Form(StatesGroup):
    idle = State()
    edit_schedule = State()
    edit_schedule_delete = State()
    edit_schedule_add = State()
    edit_elders = State()
    edit_elders_delete = State()
    edit_elders_add = State()
    edit_remind_time = State()
    create_announcement = State()
    create_event = State()