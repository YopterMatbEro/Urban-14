from aiogram import Bot, Dispatcher
import configparser
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import sqlite3

# Получение токена из конфиг-файла, подключение бота и диспатчера
config = configparser.ConfigParser()
config.read('config.ini')
bot = Bot(token=config['telegram']['token'])

dp = Dispatcher(bot, storage=MemoryStorage())


# Настройки подключения к БД
def get_connection():
    return sqlite3.connect('not_telegram.db')


def get_cursor():
    connect = get_connection()
    return connect.cursor(), connect


if __name__ == '__main__':
    cursor, connection = get_cursor()
    # Создание таблицы и её структуры
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Users(
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    email TEXT NOT NULL,
    age INTEGER,
    balance INTEGER NOT NULL
    )
    """)

    # Удаление таблицы (чтобы начать с нуля, в случае непредвиденных обстоятельств :D )
    # try:
    #     cursor.execute("DROP TABLE Users")
    #     print('Таблица User удалена')
    # except Exception as e:
    #     print(f'Непредвиденная ошибка: {e}')

    connection.commit()
    connection.close()
