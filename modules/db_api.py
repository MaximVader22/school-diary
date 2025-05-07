from datetime import datetime
import sqlite3


def create_connection():
    return sqlite3.connect("database.db")

def init_database():
    with create_connection() as client:
        cursor = client.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users(
                user_id INT PRIMARY KEY,
                username VARCHAR(32) UNIQUE DEFAULT NULL,
                is_admin INT DEFAULT 0,
                is_elder INT DEFAULT 0,
                remind_time VARCHAR(5)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS homework(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject VARCHAR(50),
                description VARCHAR(255),
                expires VARCHAR(10)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS homework_photos(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                homework_id INT,
                image MEDIUMBLOB,
                FOREIGN KEY(homework_id) REFERENCES homework(id)
            )
        """)

        client.commit()

def are_users_empty():
    with create_connection() as client:
        cursor = client.cursor()
        cursor.execute("SELECT * FROM users")
        return not bool(cursor.fetchone())

def create_user(user_id, username, is_admin=False, is_elder=False, remind_time=""):
    print(f"Trying to create user {user_id}...")
    with create_connection() as client:
        cursor = client.cursor()

        cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id, ))
        existing_user = cursor.fetchone()

        if not existing_user:
            cursor.execute(f"INSERT INTO users (user_id, username, is_admin, is_elder, remind_time) VALUES ('{user_id}', '{username}', {is_admin}, {is_elder}, '{remind_time}')")
            client.commit()
            print(f"Created user {user_id}...")

def user_exists(user_id) -> bool:
    with create_connection() as client:
        cursor = client.cursor()

        cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id, ))
        user = cursor.fetchone()

        return bool(user)

def username_exists(username) -> bool:
    with create_connection() as client:
        cursor = client.cursor()

        cursor.execute("SELECT * FROM users WHERE username=?", (username, ))
        user = cursor.fetchone()

        return bool(user)

def id_from_username(username):
    with create_connection() as client:
        cursor = client.cursor()

        cursor.execute("SELECT user_id FROM users WHERE username=?", (username, ))
        res = cursor.fetchone()

        return res[0]

def is_admin(user_id) -> bool:
    if not user_exists(user_id):
        return False

    with create_connection() as client:
        cursor = client.cursor()
        cursor.execute("SELECT is_admin FROM users WHERE user_id=?", (user_id, ))
        return bool(cursor.fetchone()[0])

def is_elder(user_id) -> bool:
    if not user_exists(user_id):
        return False

    with create_connection() as client:
        cursor = client.cursor()
        cursor.execute("SELECT is_elder FROM users WHERE user_id=?", (user_id, ))
        return bool(cursor.fetchone()[0])

def get_remind_time(user_id) -> str | None:
    with create_connection() as client:
        cursor = client.cursor()
        cursor.execute(f"SELECT remind_time FROM users WHERE user_id=?", (user_id, ))
        res = cursor.fetchone()

        if not bool(res) or res == "":
            return None

        return res[0]

def is_right_time_format(time: str) -> bool:
    try:
        datetime.strptime(time, "%H:%M")
        return True
    except ValueError:
        return False

def is_right_date_format(date: str) -> bool:
    try:
        datetime.strptime(date, "%d.%m.%Y %H:%M")
        return True
    except ValueError:
        return False

def is_right_homework_date_format(date: str) -> bool:
    try:
        datetime.strptime(date, "%d.%m.%Y")
        return True
    except ValueError:
        return False

def set_remind_time(user_id, time: str | None):
    if not user_exists(user_id):
        return

    if not is_right_time_format(time):
        return

    if time is None:
        time = ""

    with create_connection() as client:
        cursor = client.cursor()
        cursor.execute("UPDATE users SET remind_time=? WHERE user_id=?", (time, user_id))
        client.commit()

def set_username(user_id, username: str | None):
    if not user_exists(user_id):
        return

    with create_connection() as client:
        cursor = client.cursor()
        cursor.execute("UPDATE users SET username=? WHERE user_id=?", (username, user_id))
        client.commit()

def set_elder(username, elder: bool):
    if not username_exists(username):
        return

    with create_connection() as client:
        cursor = client.cursor()
        cursor.execute("UPDATE users SET is_elder=? WHERE username=?", (elder, username))
        client.commit()

def has_elder_rights(user_id) -> bool:
    if not user_exists(user_id):
        return False

    with create_connection() as client:
        cursor = client.cursor()
        cursor.execute("SELECT is_admin, is_elder FROM users WHERE user_id=?", (user_id, ))
        res = cursor.fetchone()
        return bool(res[0]) or bool(res[1])

def get_all_user_ids():
    with create_connection() as client:
        cursor = client.cursor()
        cursor.execute("SELECT user_id FROM users")
        return cursor.fetchall()

def add_homework(date, subject, description, photos):
    with create_connection() as client:
        cursor = client.cursor()

        cursor.execute("INSERT INTO homework (subject, description, expires) VALUES (?, ?, ?)", (subject, description, date))

        homework_id = cursor.lastrowid

        for photo in photos:
            print("Inserted an image into homework_photos")
            cursor.execute("INSERT INTO homework_photos (homework_id, image) VALUES (?, ?)", (homework_id, photo))

        client.commit()

def list_homework():
    with create_connection() as client:
        cursor = client.cursor()
        cursor.execute("SELECT * FROM homework")
        return cursor.fetchall()

def get_homework_data(homework_id: int):
    with create_connection() as client:
        cursor = client.cursor()
        cursor.execute("SELECT * FROM homework WHERE id=?", (homework_id, ))
        homework = cursor.fetchone()

        if not homework:
            return None

        cursor.execute("SELECT * FROM homework_photos WHERE homework_id=?", (homework_id, ))
        photos = cursor.fetchall()
        if not photos:
            photos = []

        return {
            "id": homework[0],
            "subject": homework[1],
            "description": homework[2],
            "expires": homework[3],
            "photos": photos
        }

def remove_homework(homework_id: int):
    with create_connection() as client:
        cursor = client.cursor()
        cursor.execute("DELETE FROM homework WHERE id=?", (homework_id, ))
        cursor.execute("DELETE FROM homework_photos WHERE homework_id=?", (homework_id, ))
        client.commit()

def create_homework_cleaning_process():
    pass

if __name__ == '__main__':
    init_database()
