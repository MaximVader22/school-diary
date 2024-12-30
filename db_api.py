import sqlite3

class Subject:
    def __init__(self, day: int, position: int, name: str, begin_time: str, end_time: str):
        self._day = day
        self._position = position
        self._name = name
        self._begin_time = begin_time
        self._end_time = end_time

    def __set_data(self, data_name, data):
        with create_connection() as client:
            client.execute(
                f"UPDATE schedule SET {data_name}={data} WHERE day={self._day} AND position={self._position}")
            client.commit()

    def get_day(self):
        return self._day

    def set_day(self, day: int):
        self.__set_data("day", day)
        self._day = day

    def get_position(self):
        return self._position

    def set_position(self, position: int):
        self.__set_data("position", position)
        self._position = position

    def get_name(self):
        return self._name

    def set_name(self, name: str):
        self.__set_data("name", name)
        self._name = name

    def get_begin_time(self):
        return self._begin_time

    def set_begin_time(self, begin_time: str):
        self.__set_data("begin_time", begin_time)
        self._begin_time = begin_time

    def get_end_time(self):
        return self._end_time

    def set_end_time(self, end_time: str):
        self.__set_data("end_time", end_time)
        self._end_time = end_time


class Homework:
    def __init__(self, date: str, subject: str, description: str):
        self._date = date
        self._subject = subject
        self._description = description

    def __set_data(self, data_name, data):
        with create_connection() as client:
            client.execute(
                f"UPDATE homeowrk SET {data_name}={data} WHERE date={self._date} AND subject={self._subject}")
            client.commit()

    def get_date(self):
        return self._date

    def set_date(self, date: str):
        self.__set_data("date", date)
        self._date = date

    def get_subject(self):
        return self._subject

    def set_subject(self, subject: str):
        self.__set_data("subject", subject)
        self._subject = subject

    def get_description(self):
        return self._description

    def set_description(self, description: str):
        self.__set_data("description", description)


def create_connection():
    return sqlite3.connect("database.db")


def init_database():
    with create_connection() as client:
        client.execute("""
            CREATE TABLE IF NOT EXISTS schedule(
                schedule_id INTEGER PRIMARY KEY,
                subject VARCHAR(30) NOT NULL,
                weekday VARCHAR(3) NOT NULL,
                begin TIME NOT NULL,
                end TIME NOT NULL
            )
        """)

        client.execute("""
            CREATE TABLE IF NOT EXISTS homework(
                homework_id INTEGER PRIMARY KEY,
                subject VARCHAR(30) NOT NULL,
                description VARCHAR(300) NOT NULL,
                date DATE NOT NULL
            )
        """)

        client.execute("""
            CREATE TABLE IF NOT EXISTS users(
                student_id INTEGER PRIMARY KEY,
                username VARCHAR(35) NOT NULL UNIQUE,
                state VARCHAR (50) NOT NULL
            )
        """)


def get_subject(day: int, position: int) -> Subject | None:
    with create_connection() as client:
        data = client.execute("SELECT * FROM schedule WHERE day=? AND position=?", (day, position)).fetchone()

        if data is None:
            return None

        return Subject(data[0], data[1], data[2], data[3], data[4])


def create_subject(day: int, position: int, name: str, begin_time: str, end_time: str) -> Subject:
    with create_connection() as client:
        client.execute("INSERT INTO schedule (day, position, name, begin_time, end_time) VALUES (?, ?, ?, ?, ?)",
                       (day, position, name, begin_time, end_time))
        client.commit()
        return Subject(day, position, name, begin_time, end_time)


def create_homework(date, subject, description) -> Homework:
    with create_connection() as client:
        client.execute("INSERT INTO homework (date, subject, description) VALUES (?, ?, ?)",
                       (date, subject, description))
        client.commit()
        return Homework(date, subject, description)


def get_schedule(day):
    with create_connection() as client:
        cursor = client.execute("SELECT position FROM schedule WHERE day=?", (day,))
        result = []
        for row in cursor.fetchall():
            result.append(get_subject(day, row[0]))
        return result


def get_all_homework(date: str = None):
    with create_connection() as client:
        cursor = None
        if date is not None:
            cursor = client.execute("SELECT * FROM homework WHERE date=?", (date,))
        else:
            cursor = client.execute("SELECT * FROM homework")

        result = []

        for row in cursor.fetchall():
            result.append(Homework(row[0], row[1], row[2]))

        return result


def get_homework(date, subject):
    collection = get_all_homework(date)
    result = []
    for homework in collection:
        if homework.get_subject() == subject:
            result.append(homework)
    return result

def create_user(username):
    with create_connection() as client:
        if not client.execute(
            f"SELECT * FROM users WHERE username='{username}'").fetchall():
            client.execute(
                f"INSERT INTO users (username, state) VALUES ('{username}', 'idle')")

def get_user_state(username):
    with create_connection() as client:
        res = client.execute(
            f"SELECT * FROM users WHERE username='{username}'").fetchall()[0][2]
    return res

def update_user_state(username, state="idle"):
    with create_connection() as client:
        client.execute(
            f"UPDATE users SET state={state} WHERE username={username}")
