import config
import datetime
import psycopg2
import psycopg2.extras
import models as m
from werkzeug.security import generate_password_hash, check_password_hash

def get_data(query, values=None):
    """Функция для получения данных из базы данных (SELECT * FROM table_name). 
    Создается соединение (данные config считаются глобальными)

    Args:
        query (str): Запрос, исполняемый в бд.
        values (tuple, optional): Данные, по которым можно конкретизировать 
        запрос (например, указание id). По умолчанию None.

    Returns:
        list: Возвращает массив с данными из базы данных
    """
    try:
        connection = psycopg2.connect(**config.DB_CONFIG)
        cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute(query, values)
        return cursor.fetchall()
    except psycopg2.DatabaseError as ex:
        config.logging.error(ex)
    finally:
        connection.close()


def set_data(query, values=None):
    """Функция, в результате которой отправляюся данные в базу данных 
    (INSERT, UPDATE, DELETE)

    Args:
        query (str): Запрос, исполняемый в бд.
        values (tuple, optional): Данные, которые будут отправлены 
        в базу данных в качестве изменяемых. Defaults to None.

    Returns:
        int: В случае, если необходимо вернуть id внесенной записи 
        "RETURNING id;", то  возвращает это значение
    """
    try:
        connection = psycopg2.connect(**config.DB_CONFIG)
        cursor = connection.cursor()
        cursor.execute(query, values)
        connection.commit()
        if "RETURNING id;" in query:
            return cursor.fetchone()[0]
    except (Exception, psycopg2.DatabaseError) as ex:
        config.logging.error(ex)
    finally:
        connection.close()


def get_user_by_id(id): 
    try:
        user = get_data("""SELECT u.id, u.email, u.password, u.lastname,
                        u.firstname, r.role, u.last_activity, 
                        u.password_changed, u.status
                        FROM users u JOIN roles r on u.role = r.id 
                        WHERE u.id = %s""", (id,))
        if user != []:
            user = user[0]
            return m.User(
                user.get('id'), user.get('email'), user.get('password'),
                user.get('lastname'), user.get('firstname'), user.get('role'),
                user.get('last_activity'), user.get('password_changed'),
                user.get('status'))
    except Exception as ex:
        config.logging.error(ex)


def get_user_by_email(email): 
    try:
        user = get_data("""SELECT u.id, u.email, u.password, u.lastname,
                        u.firstname, r.role, u.last_activity, 
                        u.password_changed, u.status
                        FROM users u JOIN roles r on u.role = r.id 
                        WHERE u.email = %s""", (email,))
        if user != []:
            user = user[0]
            return m.User(
                user.get('id'), user.get('email'), user.get('password'),
                user.get('lastname'), user.get('firstname'), user.get('role'),
                user.get('last_activity'), user.get('password_changed'),
                user.get('status'))
    except Exception as ex:
        config.logging.error(ex)


def set_user_last_activity(user_id):
    """_summary_

    Args:
        user_id (_type_): _description_

    Returns:
        _type_: _description_
    """    
    last_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        return set_data("""UPDATE users SET last_activity = %s WHERE id = %s
                        RETURNING id;""", (last_date, user_id))
    except Exception as ex:
        config.logging.error(ex)


def get_users():
    try:
        return get_data("""SELECT u.id, u.email, u.lastname,
                        u.firstname, r.role, u.status, u.last_activity
                        FROM users u JOIN roles r on u.role = r.id 
                        ORDER BY u.lastname""")
    except Exception as ex:
        config.logging.error(ex)


def create_user(email, password, lastname, firstname):
    password_hash = generate_password_hash(password)
    try:
        role = get_data("SELECT id FROM roles WHERE role = 'customer';")
        if role:
            role_id = role[0].get('id')
            return set_data(
                '''INSERT INTO users (email, password, lastname, firstname,
                 role, status, password_changed) VALUES 
                (%s, %s, %s, %s, %s, True, False) RETURNING id;''',
                (email, password_hash, lastname, firstname, role_id))
    except Exception as error:
        config.logging.error(error)


def change_user_password(user_id, new_password):
    password_hash = generate_password_hash(new_password)
    try:
        return set_data(
            '''UPDATE users SET password = %s, 
            password_changed = true WHERE id = %s RETURNING id;''', 
            (password_hash, user_id,))
    except Exception as error:
        config.logging.error(error)


def change_user_last_login(user_id):
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        return set_data(
            '''UPDATE users SET last_activity = %s 
            WHERE id = %s RETURNING id;''', 
            (now, user_id,))
    except Exception as error:
        config.logging.error(error)


def check_user_password(password_hash, password):
    try:
        return check_password_hash(password_hash, password)
    except Exception as ex:
        config.logging.error(ex)


def blocked_password(user_id):
    try:
        return set_data(
            '''UPDATE users SET status = False 
            WHERE users.id = %s RETURNING id;''',
            (user_id,))
    except Exception as error:
        config.logging.error(error)


def unblocked_password(user_id):
    try:
        return set_data(
            '''UPDATE users SET status = True 
            WHERE users.id = %s RETURNING id;''',
            (user_id,))
    except Exception as error:
        config.logging.error(error)


def get_roles():
    try:
        return get_data('SELECT * FROM roles')
    except Exception as ex:
        config.logging.error(ex)


# def edit_user(email, lastname, firstname, phone, role, id):
#     try:
#         return set_data("""
#                         UPDATE users SET email = %s,  lastname = %s, 
#                         firstname = %s, phone = %s, role = %s 
#                         WHERE id = %s RETURNING id;""",
#                         (email, lastname, firstname, phone, role, id))
#     except Exception as ex:
#         config.logging.error(ex)


def get_admins_count():
    try:
        role = get_data("SELECT id FROM roles WHERE role = 'admin';")
        if role:
            role_id = role[0].get('id')
        return get_data('SELECT count(*) FROM users WHERE role = %s;', (role_id,))
    except Exception as ex:
        config.logging.error(ex)
        

def history(user, action):
    try:
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return set_data(
            '''INSERT INTO history ("user", action, time) VALUES (%s, %s, %s)
            RETURNING id;''', 
            (user, action, now))
    except Exception as ex:
        config.logging.error(ex)

def get_menu():
    try:
        return get_data("""
        SELECT m.*, c.name as category_name 
        FROM menu m
        JOIN category c ON m.category = c.id
        ORDER BY m.category;
        """)
    except Exception as ex:
        config.logging.error(ex)
        

def add_food_to_cart(user_id, food_id, price):
    try:
        return set_data(
            '''INSERT INTO cart ("user", food, count, summ) 
            VALUES (%s, %s, %s, %s) RETURNING id;''', 
            (user_id, food_id, 1, price))
    except Exception as ex:
        config.logging.error(ex)
    


def get_cart(user_id):
    try:
        return get_data('''SELECT c.id, m.name, c.count, c.summ, m.price, c.food
                        FROM cart as c
                        JOIN menu as m ON m.id = c.food
                        WHERE "user" = %s;''', (user_id,))
    except Exception as ex:
        config.logging.error(ex)
        

def get_category():
    try:
        return get_data('''SELECT * FROM category;''', ())
    except Exception as ex:
        config.logging.error(ex)


def add_dish(name, description, price, category, photo):
    try:
        return set_data('''INSERT INTO menu 
                        (name, description, price, category, photo)
                        VALUES (%s, %s, %s, %s, %s) RETURNING id;''', 
                        (name, description, price, category, photo))
    except Exception as ex:
        config.logging.error(ex)
        
        
def update_cart_count(item_id, change, user_id):
    """
    Обновляет количество указанного товара в корзине пользователя.

    Args:
        item_id (int): ID товара в корзине.
        change (int): Изменение количества товара (может быть положительным или отрицательным).
        user_id (int): ID пользователя.

    Returns:
        tuple: (bool, str) успех операции и сообщение.
    """
    try:
        connection = psycopg2.connect(**config.DB_CONFIG)
        cursor = connection.cursor()

        # Начало транзакции
        connection.autocommit = False
        # Получить текущее количество товара в корзине
        cursor.execute('SELECT count FROM cart WHERE "user" = %s AND food = %s', (user_id, int(item_id)))
        result = cursor.fetchone()
        if result:
            current_quantity = result[0]
            new_quantity = current_quantity + change

            if new_quantity <= 0:
                # Если количество становится нулевым или меньше, удаляем товар из корзины
                cursor.execute('DELETE FROM cart WHERE "user" = %s AND food = %s', (user_id, item_id))
            else:
                # Обновляем количество товара в корзине
                cursor.execute('UPDATE cart SET count = %s WHERE "user" = %s AND food = %s', (new_quantity, user_id, item_id))

            # Подтверждаем изменения
            connection.commit()
            return True, "Количество успешно обновлено"
        return False, "Товар не найден в корзине"

    except Exception as e:
        if connection:
            connection.rollback()  # Откатываем изменения в случае ошибки
        config.logging.error(str(e))
        return False, str(e)
    finally:
        if connection:
            connection.close()


def calculate_cart_total(user_id):
    """Вычисляет общую сумму в корзине пользователя."""
    try:
        result = get_data("SELECT SUM(count * price) as total FROM cart JOIN food ON cart.food = food.id WHERE user_id = %s", (user_id,))
        return result[0]['total'] if result[0]['total'] is not None else 0
    except Exception as e:
        config.logging.error(str(e))


def create_order(user_id, table_number):
    """
    Создает новый заказ, копирует содержимое корзины в список заказов и очищает корзину.

    Args:
        user_id (int): ID пользователя, который делает заказ.

    Returns:
        bool: True, если заказ успешно создан и корзина очищена; False в случае ошибки.
    """
    try:
        connection = psycopg2.connect(**config.DB_CONFIG)
        cursor = connection.cursor()
        
        # Начать транзакцию
        connection.autocommit = False

        # Получить данные из корзины
        cursor.execute('SELECT food, count, count * summ AS total FROM cart WHERE "user" = %s', (user_id,))
        cart_items = cursor.fetchall()
        if not cart_items:
            raise Exception("Корзина пуста")

        # Расчет суммы заказа
        total_sum = sum(item['total'] for item in cart_items)
        print(total_sum)
        # Создание заказа
        cursor.execute("INSERT INTO orders (user, time, summa, table, status) VALUES (%s, NOW(), %s, %s, 1) RETURNING id;", 
                       (user_id, total_sum, table_number))
        order_id = cursor.fetchone()[0]
        print(order_id)
        # Добавление элементов в order_list
        for item in cart_items:
            cursor.execute("INSERT INTO order_list (order, food, count, summ) VALUES (%s, %s, %s, %s);", 
                           (order_id, item['food'], item['count'], item['total']))

        # Очистка корзины
        cursor.execute('DELETE FROM cart WHERE "user" = %s;', (user_id,))

        # Подтверждение транзакции
        connection.commit()
        return True
    except Exception as ex:
        config.logging.error(ex)
        if connection:
            connection.rollback()
        return False
    finally:
        if connection:
            connection.close()

def get_user_orders(user_id):
    try:
        return get_data("""
    SELECT o.id, o.time, o.summa, o.status, ol.food, ol.count, ol.summ
    FROM orders o
    JOIN order_list ol ON o.id = ol.order
    WHERE o.user = %s
    ORDER BY o.id;
    """, (user_id,))
    except Exception as ex:
        config.logging.error(ex)
        
def get_all_orders():
    try:
        return get_data("""
    SELECT o.id, o.time, o.summa, o.status, ol.food, ol.count, ol.summ
    FROM orders o
    JOIN order_list ol ON o.id = ol.order
    ORDER BY o.id;
    """)
    except Exception as ex:
        config.logging.error(ex)