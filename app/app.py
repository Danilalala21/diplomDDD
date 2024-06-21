import os
from flask_login import LoginManager, current_user, login_user, login_required, logout_user
from flask import Flask, jsonify, render_template, redirect, request, url_for, flash,session
import db as db
import models as m
import constant as const
import functools
from config import *
from forms import *
from werkzeug.exceptions import InternalServerError
from collections import defaultdict
from werkzeug.utils import secure_filename


def organize_menu_by_categories(menu_items):
    categorized_menu = defaultdict(list)
    for item in menu_items:
        categorized_menu[item['category_name']].append(item)
    return categorized_menu

app = Flask(__name__)
app.config['SECRET_KEY'] = 'key'


login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.get_user_by_id(user_id)


def admin_required(funct):
    """ Проверка, что пользователь является администратором. """
    try:
        # сохраняет __name__ и __doc__ за функцией.
        @functools.wraps(funct)
        # создаём "обёрнутую" функцию, имплементирующую (реализующую) 
        # функционал изначальной, но с проверкой
        def wrapped(*args, **kwargs):
            # если текущий пользователь не администратор
            if current_user.is_authenticated and current_user.get_role() != const.ADMINISTRATOR:
                # сообщаем об этом
                flash("Access denied", category='error')
                # переадресуем на главную страницу
                return redirect(url_for('index'))
            # возвращаем результат исполнения "оборачиваемой" функции
            return funct(*args, **kwargs)
        # возвращаем "обёрнутую" функцию
        return wrapped
    except Exception as ex:
        logging.error(f"An unexpected error occurred: {ex}")
        raise InternalServerError


def user_check_password(funct):
    """ Проверка, что пользователь сменил пароль. """
    try:
        # сохраняет __name__ и __doc__ за функцией.
        @functools.wraps(funct)
        # создаём "обёрнутую" функцию, имплементирующую (реализующую) 
        # функционал изначальной, но с проверкой, что пользователь входил уже 
        def wrapped(*args, **kwargs):
            if isinstance(current_user, m.User) and not current_user.password_changed:
                return redirect(url_for('change_password'))
            # возвращаем результат исполнения "оборачиваемой" функции
            return funct(*args, **kwargs)
        # возвращаем "обёрнутую" функцию
        return wrapped
    except Exception as ex:
        logging.error(f"An unexpected error occurred: {ex}")
        raise InternalServerError


@app.route('/login', methods=["GET", "POST"])
def login():
    try:
        if not current_user.is_authenticated:
            form = LoginForm()
            if form.validate_on_submit():  
                user = db.get_user_by_email(form.email.data)
                if user is not None:
                    if db.check_user_password(
                        user.password, form.password.data):
                        login_user(user, remember=form.remember_me.data)
                        flash("Успещная авторизация", category='success')
                        db.change_user_last_login(current_user.id)
                        db.history(current_user.id,'Пользователь авторизовался')
                        return redirect("/")
                    
                    flash("Неверный логин или пароль", category='error')
                    return render_template('login.html', page='login', form=form)
                flash("Пользователь с таким email не найден", 
                      category='error')
                return render_template('login.html', page='login', form=form)
            return render_template('login.html', page='login', form=form)
        return redirect("/")
    except Exception as ex:
        logging.error(ex)
        raise InternalServerError


@app.route('/logout')
@login_required
def logout():
    if current_user.get_id():
        db.history(current_user.id, 'Пользователь вышел из системы')
        logout_user()
    return redirect("/")


@app.route('/register', methods=["GET", "POST"])
def registration():
    try:
        if current_user.is_authenticated:
            return redirect('/')
        form = RegistrationForm()
        

        if form.validate_on_submit():  
            if db.create_user(
                form.email.data, form.password.data,
                form.lastname.data, form.firstname.data) is not None:
                flash('Регистрация прошла успешно!', 
                    category='success')
                return redirect('/login')
            flash('Ошибка во время регистрации!',
                      category='error')
            
        return render_template('register.html', page='register', form=form)
    except Exception as ex:
        logging.error(ex)
        raise InternalServerError
    

@app.route('/change_password', methods=['POST', 'GET'])
@login_required
def change_password():
    try:
        form = ResetPasswordForm()
        if form.validate_on_submit():  
            if form.confirm_new_password.data != form.old_password.data:
                if db.change_user_password(
                    current_user.id, 
                    form.confirm_new_password.data) is not None:
                    db.history(current_user.id, 'the user changed the password')
                    flash('The user\'s password has been successfully changed!', category='success')
                    return redirect('/login')
                flash('An error occurred while changing the password!',
                        category='error')
        return render_template('change_password.html', page='change_password', form=form)
    except Exception as ex:
        logging.error(ex)
        raise InternalServerError



@app.route('/')
def index():
    try:
        return render_template('index.html', page='_')
    except Exception as ex:
        logging.error(ex)
        raise InternalServerError


@app.route('/menu')
def menu():
    try:
        categorized_menu = organize_menu_by_categories(db.get_menu())
        return render_template('menu.html', menu_items=categorized_menu)
    except Exception as ex:
        logging.error(ex)
        raise InternalServerError


@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    food_id = request.json.get('food_id')
    price = request.json.get('price')
    try:
        result =  db.add_food_to_cart(current_user.id, food_id, price)
        if result:
            return jsonify({'success': True, 'cart_id': result})
    except Exception as ex:
        logging.error(ex)
        return jsonify({'success': False, 'error': str(ex)})


@app.route('/cart')
@login_required
@user_check_password
def cart():
    try:
        cart_items = db.get_cart(current_user.id) 
        if not cart_items:
            flash('Ваша корзина пуста!.', 'info')
        return render_template(
            'cart.html', page='cart', cart_items=cart_items)
    except Exception as ex:
        logging.error(ex)
        raise InternalServerError


@app.route('/create', methods=['GET', 'POST'])
@login_required
@user_check_password
def create():
    try:
        form = AddDishForm()
        categories = db.get_category()
        form.category.choices = [(c.get('id'), c.get('name')) for c in categories]
        
        if form.validate_on_submit():
            image = form.image.data
            if image:
                filename = secure_filename(image.filename)
                file_path = os.path.join(const.IMAGES_FOLDER, filename)
                image.save(file_path)
            else:
                file_path = None
            if db.add_dish(
                form.name.data, form.description.data, 
                form.price.data, form.category.data, file_path):
                flash('Новое блюдо успешно добавлено!', 'success')
                return redirect(url_for('create'))  
            flash('Новое блюдо успешно добавлено!', 'error')
            return redirect(url_for('menu'))  
        return render_template('create.html', page='create', form=form)
    except Exception as ex:
        logging.error(ex)
        raise InternalServerError
    
    
@app.route('/update-quantity', methods=['POST'])
def update_quantity():
    data = request.get_json()
    item_id = data.get('itemId')
    change = data.get('change')
    user_id = current_user.id # Пример получения ID пользователя, предполагается, что аутентификация уже реализована

    success, message = db.update_cart_count(item_id, change, user_id)

    if success:
        # Вычислить новую сумму в корзине
        new_sum = db.calculate_cart_total(user_id)
        return jsonify({'success': True, 'message': message, 'newSum': new_sum})
    return jsonify({'success': False, 'message': message})

@app.route('/place-order', methods=['POST'])
@login_required
@user_check_password
def place_order():
    if not current_user.is_authenticated:
        return jsonify({'success': False, 'message': 'Пользователь не авторизован'}), 401
    
    data = request.get_json()  # Получение JSON данных из запроса
    table_number = data.get('table_number') if data else None
    
    if not table_number:
        return jsonify({'success': False, 'message': 'Номер стола не указан'}), 400
    
    try:
        # Преобразование номера стола из строки в число, если это необходимо
        table_number = int(table_number)
        order_created = db.create_order(current_user.id, table_number)

        if order_created:
            return jsonify({'success': True, 'message': 'Заказ успешно оформлен'})
        return jsonify({'success': False, 'message': 'Не удалось оформить заказ'})
    except ValueError:
        return jsonify({'success': False, 'message': 'Некорректные данные номера стола'}), 400
    except Exception as ex:
        return jsonify({'success': False, 'message': str(ex)}), 500
    
    
@app.route('/about')
def about():
    try:
        return render_template('about.html', page='menu')
    except Exception as ex:
        logging.error(ex)
        raise InternalServerError



# ВЫВОД ПРОФИЛЯ ПОЛЬЗОВАТЕЛЯ
@app.route('/profile')
@login_required
@user_check_password
def profile():
    try:
        return render_template(
            'profile.html', page='profile')
    except Exception as ex:
        logging.error(ex)
        raise InternalServerError


@app.route('/orders')
@login_required
def orders():
    # Если пользователь не аутентифицирован, перенаправляем его на страницу входа
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    # Проверяем роль пользователя и получаем соответствующие данные заказа
    if current_user.role in ['admin', 'staff']:
        # Для администраторов и персонала загружаем все заказы
        orders = db.get_all_orders()
    else:
        # Для обычных пользователей загружаем только их заказы
        orders = db.get_user_orders(current_user.id)

    grouped_orders = {}
    for order in orders:
        if order['id'] not in grouped_orders:
            grouped_orders[order['id']] = {
                'user_email': order['user_email'],  # Email пользователя, сделавшего заказ
                'time': order['time'],              # Время заказа
                'summa': order['summa'],            # Сумма заказа
                'status': order['status'],          # Статус заказа
                'items': []                         # Список позиций в заказе
            }
        grouped_orders[order['id']]['items'].append({
            'food': order['food_name'],  # Имя блюда вместо ID
            'count': order['count'],     # Количество заказанного блюда
            'summ': order['summ']         # Сумма по позиции
        })

    return render_template('orders.html', orders=grouped_orders)


@app.route('/users')
@admin_required
@user_check_password
@login_required
def users():
    try:
        return render_template('users.html', page='users', users=db.get_users())
    except Exception as ex:
        logging.error(ex)
        raise InternalServerError



@app.errorhandler(404)
def not_found_error(error):   
    try:
        return render_template('404.html', page='404', error=error), 404
    except Exception as ex:
        logging.error(f"An unexpected error occurred: {ex}")


@app.errorhandler(InternalServerError)
def internal_error(error):
    try:
        return render_template('500.html', page='500', error=error), 500
    except Exception as ex:
        logging.error(f"An unexpected error occurred: {ex}")


@login_manager.unauthorized_handler
def unauthorized():
    try:
        flash("Log in to visit this page.","error")
        return redirect(url_for('login'))
    except Exception as ex:
        logging.error(f"An unexpected error occurred: {ex}")
        raise InternalServerError


if __name__ == "__main__":
    app.run(debug=True)
