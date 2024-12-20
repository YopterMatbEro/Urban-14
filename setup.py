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
    return sqlite3.connect('database.db')


def get_cursor():
    connect = get_connection()
    return connect.cursor(), connect
