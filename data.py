from aiogram import Bot, Dispatcher
import configparser
from aiogram.contrib.fsm_storage.memory import MemoryStorage

config = configparser.ConfigParser()
config.read('config.ini')
bot = Bot(token=config['telegram']['token'])

dp = Dispatcher(bot, storage=MemoryStorage())
