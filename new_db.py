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

    if not user_exists("JarPishik"):
        create_user("JarPishik", True, True)

def create_user(user_id, is_admin=False, is_elder=False, remind_time=""):
    with create_connection() as client:
        if not client.execute(f"SELECT * FROM users WHERE user_id='{user_id}'").fetchall():
            client.execute(f"INSERT INTO users (user_id, is_admin, is_elder, remind_time) VALUES ('{user_id}', {is_admin}, {is_elder}, '{remind_time}')")
            client.commit()

def user_exists(user_id) -> bool:
    with create_connection() as client:
        res = client.execute(f"SELECT * FROM users WHERE user_id='{user_id}'").fetchone()
        return bool(res)

def is_admin(user_id) -> bool:
    if not user_exists(user_id):
        return False

    with create_connection() as client:
        res = client.execute(f"SELECT is_admin FROM users WHERE user_id='{user_id}'").fetchone()
        return bool(res[0])

def is_elder(user_id) -> bool:
    if not user_exists(user_id):
        return False

    with create_connection() as client:
        res = client.execute(f"SELECT is_elder FROM users WHERE user_id='{user_id}'").fetchone()
        return bool(res[0])

def get_remind_time(user_id) -> str:
    with create_connection() as client:
        res = client.execute(f"SELECT remind_time FROM users WHERE user_id='{user_id}'").fetchone()
        return res[0]

def has_elder_rights(user_id) -> bool:
    if not user_exists(user_id):
        return False

    with create_connection() as client:
        res = client.execute(f"SELECT is_admin, is_elder FROM users WHERE user_id='{user_id}'").fetchone()
        return bool(res[0]) or bool(res[1])

if __name__ == '__main__':
    init_database()