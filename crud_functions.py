from setup import get_cursor


# Создание таблицы
def initiate_db():
    cursor, connection = get_cursor()

    try:
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Products(
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        price INTEGER NOT NULL
        )''')
        connection.commit()
        print('Таблица успешно создана!')
    except Exception as e:
        print(f'Ошибка при создании таблицы: {e}')
    finally:
        connection.close()


def drop_db():
    cursor, connection = get_cursor()
    try:
        cursor.execute('DROP TABLE IF EXISTS Products')
        connection.commit()
        print('Таблица успешно удалена!')
    except Exception as e:
        print(f'Ошибка при удалении таблицы: {e}')
    finally:
        connection.close()


def filling_db(prod_id, title, description, price):
    cursor, connection = get_cursor()

    try:
        cursor.execute('SELECT * FROM Products WHERE id = ? AND title = ?', (prod_id, title))
        check_data = cursor.fetchall()
        if check_data:
            raise ValueError(f' id: {prod_id}, name: {title} - уже существуют в Базе Данных. Введите уникальные параметры')
        cursor.execute("INSERT INTO Products VALUES (?, ?, ?, ?)", (prod_id, title, description, price))
        connection.commit()
        print(f'Таблица успешно заполнена с id: {prod_id} и title: {title}')
    except ValueError as ve:
        print(f'Ошибка! Повторение данных: {ve}')
    except Exception as e:
        print(f'Ошибка при наполнении таблицы: {e}')
    finally:
        connection.close()


def get_all_products():
    cursor, connection = get_cursor()

    try:
        prods = cursor.execute('SELECT * FROM Products').fetchall()
        print('Данные получены из таблицы')
        return prods
    except Exception as e:
        print(f'Ошибка при получении данных из таблицы: {e}')
    finally:
        connection.close()


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
        filling_db(prod_id, name, description, price)

    # drop_db()
