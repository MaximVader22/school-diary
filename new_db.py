import sqlite3


def create_connection():
    return sqlite3.connect("database.db")

def init_database():
    with create_connection() as client:
        client.execute("""
            CREATE TABLE IF NOT EXISTS users(
                user_id TEXT PRIMARY KEY,
                is_admin INTEGER DEFAULT 0,
                is_elder INTEGER DEFAULT 0,
                remind_time TEXT
            )
        """)

        client.commit()

def are_users_empty():
    with create_connection() as client:
        return not bool(client.execute("SELECT * FROM users").fetchone())

def create_user(user_id, is_admin=False, is_elder=False, remind_time=""):
    print(f"Trying to create user {user_id}...")
    with create_connection() as client:
        if not client.execute(f"SELECT * FROM users WHERE user_id='{user_id}'").fetchone():
            client.execute(f"INSERT INTO users (user_id, is_admin, is_elder, remind_time) VALUES ('{user_id}', {is_admin}, {is_elder}, '{remind_time}')")
            print(f"Created user {user_id}...")
            client.commit()

def user_exists(user_id) -> bool:
    with create_connection() as client:
        res = client.execute(f"SELECT * FROM users WHERE user_id='{user_id}'").fetchone()
        print(f"User {user_id} exists: {bool(res)}")
        return bool(res)

def is_admin(user_id) -> bool:
    if not user_exists(user_id):
        return False

    with create_connection() as client:
        res = client.execute(f"SELECT is_admin FROM users WHERE user_id='{user_id}'").fetchone()
        print(f"Is {user_id} admin: {bool(res[0])}")
        return bool(res[0])

def is_elder(user_id) -> bool:
    if not user_exists(user_id):
        return False

    with create_connection() as client:
        res = client.execute(f"SELECT is_elder FROM users WHERE user_id='{user_id}'").fetchone()
        print(f"Is {user_id} elder: {bool(res[0])}")
        return bool(res[0])

def get_remind_time(user_id) -> str | None:
    with create_connection() as client:
        res = client.execute(f"SELECT remind_time FROM users WHERE user_id='{user_id}'").fetchone()

        if not bool(res) or res == "":
            return None

        return res[0]

def is_right_time_format(time: str) -> bool:
    split = time.split(":")

    if len(split) != 2:
        return False

    if not split[0].isnumeric() or not split[1].isnumeric():
        return False

    hour = int(split[0])
    minute = int(split[1])

    if hour < 0 or hour > 24:
        return False

    if minute < 0 or minute > 60:
        return False

    return True

def set_remind_time(user_id, time: str | None):
    if not user_exists(user_id):
        return

    if not is_right_time_format(time):
        return

    if time is None:
        time = ""

    with create_connection() as client:
        client.execute(f"UPDATE users SET remind_time='{time}' WHERE user_id='{user_id}'")

def has_elder_rights(user_id) -> bool:
    if not user_exists(user_id):
        return False

    with create_connection() as client:
        res = client.execute(f"SELECT is_admin, is_elder FROM users WHERE user_id='{user_id}'").fetchone()
        print(f"Is {user_id} admin: {bool(res[0])}")
        print(f"Is {user_id} elder: {bool(res[1])}")
        return bool(res[0]) or bool(res[1])

if __name__ == '__main__':
    init_database()