import sqlite3
import os
from dotenv import load_dotenv
from datetime import datetime

# Load data from .env
load_dotenv()

DB_PATH = os.getenv("DB_PATH")
if not DB_PATH:
    raise ValueError("Путь к базе данных не найден! Убедитесь, что файл .env существует и содержит DB_PATH.")

SQL_GET_FILLING_PATH = os.getenv("SQL_GET")
if not SQL_GET_FILLING_PATH:
    raise ValueError("Путь к SQL-файлу не найден! Убедитесь, что файл .env существует и содержит SQL_GET.")

def init_db(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id        INTEGER PRIMARY KEY,
            access    TEXT,
            username  TEXT,  
            progress  BLOB,
            data_last_update TEXT      
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS verbs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            base_form       TEXT NOT NULL,
            past_simple     TEXT NOT NULL,
            past_participle TEXT NOT NULL,
            translate       TEXT NOT NULL
        )
    ''')
    conn.commit()

def clear_verbs_table(conn):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM verbs")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='verbs'")
    conn.commit()

def filling_verbs_table(conn):
    with open(SQL_GET_FILLING_PATH, "r", encoding="utf-8") as file:
        content = file.read()
        cursor = conn.cursor()
        cursor.executescript(content)
        conn.commit()

def month_count(time, now_time):
    years = int(now_time[0:4]) - int(time[0:4])
    months = int(now_time[5:7]) - int(time[5:7])
    months += years * 12
    return months

async def delete_users_from_table(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id, data_last_update FROM users")
    users = cursor.fetchall()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    to_delete = []

    for user in users:
        time = user[1]
        if time is not None and month_count(time, now) >= 6:
            to_delete.append(user[0])

    if to_delete:
        placeholders = ",".join("?" for _ in to_delete)
        await conn.execute(f"DELETE FROM users WHERE id IN ({placeholders})", to_delete)
        await conn.commit()


def main():
    print("\n------------------------------------------------\n")
    print("Начало работы: 'initialization_data_base.py'\n\n")

    print(f"Путь к базе данных: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    init_db(conn)
    print("База данных была создана!\n")

    clear_verbs_table(conn)
    print("Все данные из таблицы verbs удалены!\n")

    filling_verbs_table(conn)
    print("Таблица verbs была заполнена!\n\n")
    conn.close()

    print("Завершение работы: 'initialization_data_base.py'\n")
    print("------------------------------------------------\n")

if __name__ == "__main__":
    main()
