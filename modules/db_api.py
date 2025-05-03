import mysql.connector as mysql

mysql_connection = {}

with open('mysql_connection.txt') as f:
    connection_info = f.read().strip()
    splitted = connection_info.split(" || ")
    mysql_connection["host"] = splitted[0]
    mysql_connection["user"] = splitted[1]
    mysql_connection["password"] = splitted[2]
    mysql_connection["database"] = splitted[3]

def create_connection():
    return mysql.connect(
        host=mysql_connection["host"],
        user=mysql_connection["user"],
        password=mysql_connection["password"],
        database=mysql_connection["database"]
    )

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
                id INT PRIMARY KEY AUTO_INCREMENT,
                subject VARCHAR(50),
                description VARCHAR(255),
                expires VARCHAR(10)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS homework_photos(
                id INT PRIMARY KEY AUTO_INCREMENT,
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

        cursor.execute("SELECT * FROM users WHERE user_id=%s", (user_id, ))
        existing_user = cursor.fetchone()

        if not existing_user:
            cursor.execute(f"INSERT INTO users (user_id, username, is_admin, is_elder, remind_time) VALUES ('{user_id}', '{username}', {is_admin}, {is_elder}, '{remind_time}')")
            client.commit()
            print(f"Created user {user_id}...")

def user_exists(user_id) -> bool:
    with create_connection() as client:
        cursor = client.cursor()

        cursor.execute("SELECT * FROM users WHERE user_id=%s", (user_id, ))
        user = cursor.fetchone()

        return bool(user)

def username_exists(username) -> bool:
    with create_connection() as client:
        cursor = client.cursor()

        cursor.execute("SELECT * FROM users WHERE username=%s", (username, ))
        user = cursor.fetchone()

        return bool(user)

def id_from_username(username):
    with create_connection() as client:
        cursor = client.cursor()

        cursor.execute("SELECT user_id FROM users WHERE username=%s", (username, ))
        res = cursor.fetchone()

        return res[0]

def is_admin(user_id) -> bool:
    if not user_exists(user_id):
        return False

    with create_connection() as client:
        cursor = client.cursor()
        cursor.execute("SELECT is_admin FROM users WHERE user_id=%s", (user_id, ))
        return bool(cursor.fetchone()[0])

def is_elder(user_id) -> bool:
    if not user_exists(user_id):
        return False

    with create_connection() as client:
        cursor = client.cursor()
        cursor.execute("SELECT is_elder FROM users WHERE user_id=%s", (user_id, ))
        return bool(cursor.fetchone()[0])

def get_remind_time(user_id) -> str | None:
    with create_connection() as client:
        cursor = client.cursor()
        cursor.execute(f"SELECT remind_time FROM users WHERE user_id=%s", (user_id, ))
        res = cursor.fetchone()

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

def is_right_date_format(date: str) -> bool:
    if len(date) < 16:
        return False

    for i in (0, 1, 3, 4, 6, 7, 8, 9, 11, 12, 14, 15):
        if not date[i].isnumeric():
            return False

    if date[2] == '.' and date[5] == '.' and date[10] == ' ' and date[13] == ':':
        return True

    return False

def is_right_homework_date_format(date: str) -> bool:
    content = date.split(".")

    if len(content) != 3:
        return False

    if len(content[0]) != 2 or len(content[1]) != 2:
        return False

    if len(content[2]) != 4:
        return False

    for part in content:
        for char in part:
            if not char.isnumeric():
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
        cursor = client.cursor()
        cursor.execute("UPDATE users SET remind_time=%s WHERE user_id=%s", (time, user_id))
        client.commit()

def set_username(user_id, username: str | None):
    if not user_exists(user_id):
        return

    with create_connection() as client:
        cursor = client.cursor()
        cursor.execute("UPDATE users SET username=%s WHERE user_id=%s", (username, user_id))
        client.commit()

def set_elder(username, elder: bool):
    if not username_exists(username):
        return

    with create_connection() as client:
        cursor = client.cursor()
        cursor.execute("UPDATE users SET is_elder=%s WHERE username=%s", (elder, username))

def has_elder_rights(user_id) -> bool:
    if not user_exists(user_id):
        return False

    with create_connection() as client:
        cursor = client.cursor()
        cursor.execute("SELECT is_admin, is_elder FROM users WHERE user_id=%s", (user_id, ))
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

        cursor.execute("INSERT INTO homework (subject, description, expires) VALUES (%s, %s, %s)", (subject, description, date))

        homework_id = cursor.lastrowid

        for photo in photos:
            print("Inserted an image into homework_photos")
            cursor.execute("INSERT INTO homework_photos (homework_id, image) VALUES (%s, %s)", (homework_id, photo))

        client.commit()

def list_homework():
    with create_connection() as client:
        cursor = client.cursor()
        cursor.execute("SELECT expires, subject, description FROM homework")
        return cursor.fetchall()

if __name__ == '__main__':
    init_database()