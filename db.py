import datetime
import sqlite3

client = sqlite3.connect("database.db")

client.execute("PRAGMA foreign_keys = ON")
client.execute('''
    CREATE TABLE IF NOT EXISTS subjects(
        subject_id INTEGER PRIMARY KEY,
        subject VARCHAR(30) NOT NULL
    );
''')

client.execute('''
    CREATE TABLE IF NOT EXISTS schedule(
        schedule_id INTEGER PRIMARY KEY,
        subject INTEGER NOT NULL,
        week_day DATE NOT NULL,
        FOREIGN KEY (subject) REFERENCES subjects(subject_id) ON DELETE RESTRICT ON UPDATE RESTRICT
    );
''')

client.execute('''
    CREATE TABLE IF NOT EXISTS homework(
        homework_id INTEGER PRIMARY KEY,
        subject INTEGER NOT NULL,
        description VARCHAR(350) NOT NULL,
        begin_date DATE NOT NULL,
        end_date DATE NOT NULL,
        FOREIGN KEY (subject) REFERENCES subjects(subject_id) ON DELETE RESTRICT ON UPDATE RESTRICT
    )
''')

client.execute('''
    CREATE TABLE IF NOT EXISTS students(
        student_id INTEGER PRIMARY KEY,
        name VARCHAR(70) NOT NULL,
        surname VARCHAR(70) NOT NULL,
        patronymic VARCHAR(70),
        username VARCHAR(50) NOT NULL UNIQUE,
        administrator BOOLEAN DEFAULT FALSE,
        elder BOOLEAN DEFAULT FALSE
    )
''')

today = datetime.date.today()

client.execute('INSERT INTO subjects(subject) VALUES(?)', ("Русский язык",))
client.execute('INSERT INTO schedule(subject, week_day) VALUES(?, ?)', (1, today))
client.execute('INSERT INTO students(name, surname, patronymic, username) VALUES (?, ?, ?, ?)', ("Иван", "Иванов", "Иванович", "12345Q"))
client.execute('INSERT INTO homework(subject, description, begin_date, end_date) VALUES (?, ?, ?, ?)', (1, "Учить правило", today, today))

client.commit()
