from aiogram import executor
from aiogram.dispatcher.filters.state import State, StatesGroup
from setup import dp
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from crud_functions import get_all_products, is_included, add_user


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()
    gender = State()


class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()


# Стартовое меню
kb = ReplyKeyboardMarkup(resize_keyboard=True)
button_calc = KeyboardButton(text='Рассчитать')
button_info = KeyboardButton(text='Информация')
button_buy = KeyboardButton(text='Купить')
button_registration = KeyboardButton(text='Регистрация')
kb.row(button_calc, button_info)
kb.row(button_buy, button_registration)

# Выбор: Рассчитать и формулы
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
    all_products = get_all_products()

    for prod in all_products:
        await message.answer(f'Название: {prod[1]} | Описание: {prod[2]} | Цена: {prod[3]} руб.')
        with open(f'files/{prod[1]}.jpg', 'rb') as img:
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
    await call.message.answer('Введите свой возраст:')
    await UserState.age.set()


@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    if message.text.isdigit() and 0 < int(message.text) < 120:
        await state.update_data(age=message.text)
        await message.answer('Введите свой рост в сантиметрах:')
        await UserState.growth.set()
    else:
        await message.answer(
            'Пожалуйста, введите корректный возраст (число в диапазоне от 1 до 120 лет). Попробуйте снова.')
        # Ожидаем нового ввода, состояние остаётся тем же


@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    if message.text.isdigit() and 30 < int(message.text) < 300:
        await state.update_data(growth=message.text)
        await message.answer('Введите свой вес в килограммах:')
        await UserState.weight.set()
    else:
        await message.answer(
            'Пожалуйста, введите корректный рост (число в диапазоне от 30 до 300 см). Попробуйте снова.')
        # Ожидаем нового ввода, состояние остаётся тем же


@dp.message_handler(state=UserState.weight)
async def set_gender(message, state):
    if message.text.isdigit() and 10 < int(message.text) < 400:
        await state.update_data(weight=message.text)
        await message.answer('Укажите свой пол (М/Ж)')
        await UserState.gender.set()
    else:
        await message.answer(
            'Пожалуйста, введите корректный вес (число в диапазоне от 10 до 400 кг). Попробуйте снова.')
        # Ожидаем нового ввода, состояние остаётся тем же


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
        # Финализация состояния происходит только после успешной обработки
        await state.finish()
    else:
        await message.answer(f'Неверно указан пол, Ваш ответ: {gender}. Укажите один из двух (м/ж):')
        # Ожидаем нового ввода, состояние остаётся тем же


@dp.message_handler(text='Регистрация')
async def sing_up(message):
    await message.answer('Введите имя пользователя (только латинский алфавит):')
    await RegistrationState.username.set()


@dp.message_handler(state=RegistrationState.username)
async def set_username(message, state):
    if not is_included(message.text):
        if message.text.isascii() and message.text.isalpha():
            await state.update_data(username=message.text)
            await message.answer('Укажите свой email:')
            await RegistrationState.email.set()
        else:
            await message.answer('Введите корректное имя пользователя (только латинский алфавит):')
    else:
        await message.answer('Пользователь существует, введите другое имя')
        await RegistrationState.username.set()


@dp.message_handler(state=RegistrationState.email)
async def set_email(message, state):
    # Проверка корректности адреса
    check_address = ['@mail.ru', '@yandex.ru', '@ya.ru', '@gmail.com']
    acceptable_address = any(address in message.text for address in check_address)

    if acceptable_address:
        await state.update_data(email=message.text)
        await message.answer('Введите свой возраст:')
        await RegistrationState.age.set()
    else:
        await message.answer(
            'Укажите корректный (полный) адрес, включающий символ @ и почтовый домен (например @mail.ru)')
        # Ожидаем нового ввода, состояние остаётся тем же


@dp.message_handler(state=RegistrationState.age)
async def user_registration(message, state):
    if message.text.isdigit() and 0 < int(message.text) < 120:
        await state.update_data(age=message.text)
        data = await state.get_data()
        try:
            registration_status = add_user(data['username'], data['email'], data['age'])
            if registration_status:
                await message.answer(f'Регистрация прошла успешно!')
            else:
                await message.answer('Ошибка при регистрации! Обратитесь к администратору.')  # Описание в консоли
            await state.finish()
        except Exception as e:
            await message.answer(f'Ошибка при регистрации! Обратитесь к администратору.')
            print(f'Ошибка при регистрации: {e}')
    else:
        await message.answer(
            'Пожалуйста, введите корректный возраст (число в диапазоне от 1 до 120 лет). Попробуйте снова.')
        # Ожидаем нового ввода, состояние остаётся тем же


@dp.message_handler()
async def all_messages(message):
    await message.answer('Введите команду /start, чтобы начать общение!')


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
