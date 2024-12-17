from pathlib import Path

from aiogram import executor
from aiogram.dispatcher.filters.state import State, StatesGroup
from setup import dp
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()
    gender = State()


# Стартовое меню
kb = ReplyKeyboardMarkup(resize_keyboard=True)
button_calc = KeyboardButton(text='Рассчитать')
button_info = KeyboardButton(text='Информация')
button_buy = KeyboardButton(text='Купить')
kb.row(button_calc, button_info)
kb.add(button_buy)

# Выбор: Рассчитать, формулы и купить
kb_inline = InlineKeyboardMarkup()
button_calc_normal = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
button_formula = InlineKeyboardButton(text='Формулы расчета', callback_data='formulas')
kb_inline.row(button_calc_normal, button_formula)

# Инлайн при покупке
kb_inline_prods = InlineKeyboardMarkup()
button_prod_1 = InlineKeyboardButton(text='D-3', callback_data='product_buying_d-3')
button_prod_2 = InlineKeyboardButton(text='VITRUM', callback_data='product_buying_vitrum')
button_prod_3 = InlineKeyboardButton(text='Витамин A', callback_data='product_buying_vitamin_a')
button_prod_4 = InlineKeyboardButton(text='РЕВИТ', callback_data='product_buying_revit')
kb_inline_prods.row(button_prod_1, button_prod_2, button_prod_3, button_prod_4)


@dp.message_handler(commands=['start'])
async def start_message(message):
    await message.answer('Привет! Я бот помогающий твоему здоровью.')
    await message.answer('Нажмите кнопку "Рассчитать" для подсчета нормы калорий для поддержания нормального веса.',
                         reply_markup=kb)


@dp.message_handler(text='Рассчитать')
async def main_menu(message):
    await message.answer('Выберите опцию:', reply_markup=kb_inline)


@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer('Расчет ведется по формуле Миффлина-Сан Жеора:')
    await call.message.answer(f'''
* для мужчин (10 х вес (кг) + 6.25 х рост (см) - 5 х возраст (г) + 5) х A
* для женщин (10 х вес (кг) + 6.25 х рост (см) - 5 х возраст (г) - 161) х A

A - это уровень активности человека, его различают обычно по пяти степеням физических нагрузок в сутки.
В нашей формуле берется за основу коэффициент средней активности.
Средняя активность: A = 1,55. 
''')


@dp.message_handler(text='Купить')
async def get_buying_list(message):
    files = {num: file.name for num, file in enumerate(list(Path('files/').glob('*'))) if file.is_file()}
    descriptions = {
        'D-3': ['Поддерживает крепость костей и укрепляет иммунную систему', 1785],
        'VITRUM': ['13 Витаминов, 12 Минералов', 723],
        'А': ['Нормализация работы иммунной системы, улучшение состояния кожи и здоровья глаз', 1450],
        'РЕВИТ': ['Поддерживает баланс витаминов в организме', 83]
    }
    print(files)
    for i in range(4):
        file_values = files[i].rstrip(".jpg")
        await message.answer(f'Название: {file_values} | Описание: {descriptions[file_values][0]} | Цена: {descriptions[file_values][1]} руб.')
        with open(f'files/{files[i]}', 'rb') as img:
            await message.answer_photo(img)
    await message.answer('Выберите продукт для покупки:', reply_markup=kb_inline_prods)


@dp.callback_query_handler(text='product_buying_d-3')
async def send_confirm_message(call):
    await call.message.answer('Вы успешно приобрели Витамины D-3!')


@dp.callback_query_handler(text='product_buying_vitrum')
async def send_confirm_message(call):
    await call.message.answer('Вы успешно приобрели VITRUM!')


@dp.callback_query_handler(text='product_buying_vitamin_a')
async def send_confirm_message(call):
    await call.message.answer('Вы успешно приобрели Витамин А!')


@dp.callback_query_handler(text='product_buying_revit')
async def send_confirm_message(call):
    await call.message.answer('Вы успешно приобрели Ревит!')


@dp.callback_query_handler(text='calories')
async def set_age(call):
    await call.message.answer('Введите свой возраст.')
    await UserState.age.set()


@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    if message.text.isdigit() and 0 < int(message.text) < 120:
        await state.update_data(age=message.text)
        await message.answer('Введите свой рост в сантиметрах.')
        await UserState.growth.set()
    else:
        await message.answer(
            'Пожалуйста, введите корректный возраст (число в диапазоне от 1 до 120 лет). Попробуйте снова.')


@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    if message.text.isdigit() and 30 < int(message.text) < 300:
        await state.update_data(growth=message.text)
        await message.answer('Введите свой вес в килограммах.')
        await UserState.weight.set()
    else:
        await message.answer(
            'Пожалуйста, введите корректный рост (число в диапазоне от 30 до 300 см). Попробуйте снова.')


@dp.message_handler(state=UserState.weight)
async def set_gender(message, state):
    if message.text.isdigit() and 10 < int(message.text) < 400:
        await state.update_data(weight=message.text)
        await message.answer('Укажите свой пол (М/Ж)')
        await UserState.gender.set()
    else:
        await message.answer(
            'Пожалуйста, введите корректный вес (число в диапазоне от 10 до 400 кг). Попробуйте снова.')


@dp.message_handler(state=UserState.gender)
async def send_calories(message, state):
    gender = message.text.lower()
    if gender in ['м', 'ж']:
        await state.update_data(gender=message.text)
        data = await state.get_data()
        if data['gender'].lower() == 'м':
            result = (10 * float(data['weight']) + 6.25 * float(data['growth']) - 5 * float(
                data['age']) + 5) * 1.55  # выбрал среднюю активность
            await message.answer(f'Норма калорий для Вас {round(result, 2)}')
        elif data['gender'].lower() == 'ж':
            result = (10 * float(data['weight']) + 6.25 * float(data['growth']) - 5 * float(data['age']) - 161) * 1.55
            await message.answer(f'Норма калорий для Вас {round(result, 2)}')
    else:
        await message.answer(f'Неверно указан пол, Ваш ответ: {gender}')
        await message.answer('Начните сначала. Введите команду /start')
    await state.finish()


@dp.message_handler()
async def all_messages(message):
    await message.answer('Введите команду /start, чтобы начать общение!')


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
