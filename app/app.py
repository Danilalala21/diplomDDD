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
                        flash("Success login", category='success')
                        db.change_user_last_login(current_user.id)
                        db.history(current_user.id, 'the user has logged in')
                        return redirect("/")
                    
                    flash("Invalid username or password", category='error')
                    return render_template('login.html', page='login', form=form)
                flash("The user with this email was not found", 
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
        db.history(current_user.id, 'the user has logged out')
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
                flash('Registration was completed successfully!', 
                    category='success')
                return redirect('/login')
            flash('An error occurred while register!',
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
@login_required
def index():
    try:
        return render_template('index.html', page='_')
    except Exception as ex:
        logging.error(ex)
        raise InternalServerError
    

@app.route('/menu')
@login_required
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
def cart():
    try:
        cart_items = db.get_cart(current_user.id) 
        if not cart_items:
            flash('Your cart is currently empty.', 'info')
        return render_template(
            'cart.html', page='cart', cart_items=cart_items)
    except Exception as ex:
        logging.error(ex)
        raise InternalServerError


@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    try:
        form = AddDishForm()
        categories = db.get_category()
        form.category.choices = [(c.get('id'), c.get('name')) for c in categories]
        
        if form.validate_on_submit():
            image = form.image.data
            if image:
                filename = secure_filename(image.filename)
                file_path = os.path.join('path/to/save/images', filename)
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
    # Здесь код для обновления количества товара в корзине
    # Предположим, что это обновление происходит успешно
    return jsonify({'success': True})

@app.route('/place-order', methods=['POST'])
def place_order():
    # Здесь код для оформления заказа
    # Предположим, что заказ успешно оформлен
    return jsonify({'success': True, 'message': 'Заказ успешно оформлен'})

@app.route('/about')
@login_required
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
@user_check_password
def orders():
    try:
        return render_template(
            'orders.html', page='orders')
    except Exception as ex:
        logging.error(ex)
        raise InternalServerError
    

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
