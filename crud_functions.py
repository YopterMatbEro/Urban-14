from setup import get_cursor


def execute_query(query, params: tuple = ()):
    cursor, connection = get_cursor()
    try:
        cursor.execute(query, params)
        connection.commit()
        return cursor, connection
    except Exception as e:
        print(f'Ошибка при выполнении запроса: {e}')
        connection.close()  # Закрываем соединение в случае ошибки
        return None, None  # Возвращаем None, если произошла ошибка


# Создание таблицы
def initiate_db():
    """Создает таблицы Products и Users, если её нет"""
    query = f"""
    CREATE TABLE IF NOT EXISTS Products(
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        price INTEGER NOT NULL
    )
    """
    try:
        execute_query(query)
        print('Таблица Products успешно создана!')
    except Exception as e:
        print(f'Ошибка при создании таблицы Products: {e}')

    query = f"""
    CREATE TABLE IF NOT EXISTS Users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        email TEXT NOT NULL,
        age INTEGER NOT NULL,
        balance INTEGER NOT NULL
    )
    """
    try:
        execute_query(query)
        print('Таблица Users успешно создана!')
    except Exception as e:
        print(f'Ошибка при создании таблицы Users: {e}')


def drop_table(table_name):
    """Удаляет таблицу <table_name>, если она существует"""
    try:
        execute_query(f'DROP TABLE IF EXISTS {table_name}')
        print(f'Таблица {table_name} успешно удалена!')
    except Exception as e:
        print(f'Ошибка при удалении таблицы: {e}')


def filling_products(prod_id, title, description, price):
    """Заполняет таблицу Products данными"""
    query_check = f'SELECT * FROM Products WHERE id = ? AND title = ?'
    cursor, connection = execute_query(query_check, (prod_id, title))

    if cursor is None:
        print('Ошибка при проверке данных. Перед заполнением таблицы Products')
        return

    check_data = cursor.fetchall()
    if check_data:
        raise ValueError(f'id: {prod_id}, name: {title} - уже существуют в базе данных.'
                         'Введите уникальные параметры.')

    query_insert = f'INSERT INTO Products VALUES (?, ?, ?, ?)'
    execute_query(query_insert, (prod_id, title, description, price))
    print(f'Таблица Products успешно заполнена с id: {prod_id} и title: {title}')

    connection.close()


def get_all_products():
    """Возвращает все данные из таблицы Products"""
    cursor, connection = get_cursor()

    try:
        prods = cursor.execute('SELECT * FROM Products').fetchall()
        print('Данные получены из таблицы')
        return prods
    except Exception as e:
        print(f'Ошибка при получении данных из таблицы: {e}')
    finally:
        connection.close()


def is_included(username):
    """Проверяет наличие пользователя в Базе Данных"""
    query = "SELECT * FROM Users WHERE username = ?"
    cursor, connection = execute_query(query, (username,))

    if cursor is None:
        print('Ошибка при проверке наличия пользователя в БД')
        return

    check_user = cursor.fetchall()
    connection.close()
    return True if check_user else False


def add_user(username, email, age):
    """Добавляет пользователя в таблицу Users, если такового нет"""
    check_data = is_included(username)

    if check_data:
        raise ValueError(f'username: {username} - занят. Просьба ввести уникальные параметры')

    try:
        query_insert = "INSERT INTO Users (username, email, age, balance) VALUES (?, ?, ?, ?)"
        cursor, connection = execute_query(query_insert, (username, email, age, 1000))
        if cursor:
            print('Регистрация прошла успешно!')
            connection.close()
            return True
        connection.close()
        return False
    except Exception as e:
        print(f'Ошибка выполнения запроса к БД: INSERT INTO Users - {e}')


def show_users():
    """Выводит в консоль всех пользователей. Для тех, кто поленился подключиться к БД"""
    query = 'SELECT * FROM Users'
    cursor, connection = execute_query(query)
    users_data = cursor.fetchall()

    print("\n(id, 'username', 'email', age, balance)")
    for user in users_data:
        print(user)


if __name__ == '__main__':
    initiate_db()

    products = {
        0: {'D-3': ['Поддерживает крепость костей и укрепляет иммунную систему', 1785]},
        1: {'VITRUM': ['13 Витаминов, 12 Минералов', 723]},
        2: {'А': ['Нормализация работы иммунной системы, улучшение состояния кожи и здоровья глаз', 1450]},
        3: {'РЕВИТ': ['Поддерживает баланс витаминов в организме', 83]}
    }

    for prod_id, product in products.items():
        name = list(product.keys())[0]
        description = list(product.values())[0][0]
        price = list(product.values())[0][1]
        filling_products(prod_id, name, description, price)

    # drop_table('Products')
    # drop_table('Users')

    # show_users()
