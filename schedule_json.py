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
def add_schedule(file_name, day, lessons):
    schedule = load_schedule(file_name)
    if day in schedule:
        schedule[day].extend(lessons)
    else:
        schedule[day] = lessons
    save_schedule(file_name, schedule)

# Функция для удаления одного вхождения предмета
def remove_one_subject(file_name, subject):
    schedule = load_schedule(file_name)
    removed = False  # Флаг для проверки, был ли удален предмет

    for day, lessons in schedule.items():  
        if subject in lessons:  
            lessons.remove(subject)  
            removed = True
            save_schedule(file_name, schedule)
            print(f"Предмет '{subject}' удален из дня '{day}'.")
            break  

    if not removed:  
        print(f"Предмет '{subject}' не найден в расписании.")

