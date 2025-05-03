import json
import os

# Функция для загрузки данных из JSON-файла
def load_schedule(file_name):
    if os.path.exists(file_name):
        with open(file_name, 'r', encoding='utf-8') as file:
            return json.load(file)
    return {}

# Функция для сохранения данных в JSON-файл
def save_schedule(file_name, schedule):
    with open(file_name, 'w', encoding='utf-8') as file:
        json.dump(schedule, file, ensure_ascii=False, indent=4)

# Функция для добавления расписания
def add_schedule(file_name, day: str, subject: str, start_time: str, end_time: str):
    schedule = load_schedule(file_name)

    if not day in schedule:
        schedule[day] = []

    lessons = schedule[day]
    lessons.append({
        "name": subject,
        "start_time": start_time,
        "end_time": end_time
    })

    save_schedule(file_name, schedule)

# Функция для удаления одного вхождения предмета
def remove_one_subject(file_name, subject: str):
    schedule = load_schedule(file_name)
    removed = False  # Флаг для проверки, был ли удален предмет

    for day, lessons in schedule.items():
        for lesson in lessons:
            if lesson["name"] == subject:
                lessons.remove(lesson)
                removed = True
                save_schedule(file_name, schedule)
                print(f"Предмет '{subject}' удален из дня '{day}'.")
                break

    if not removed:  
        print(f"Предмет '{subject}' не найден в расписании.")