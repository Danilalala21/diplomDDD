from flask_wtf import FlaskForm
from wtforms import (
    DecimalField, StringField, PasswordField, SubmitField, 
    BooleanField, SelectField, TextAreaField)
from wtforms.validators import (
    DataRequired, EqualTo, ValidationError, Length, Email, NumberRange)
from wtforms.widgets import TextArea
from flask_wtf.file import FileField, FileAllowed, FileRequired
import re


class PasswordValidator:
    def __init__(self, password):
        self.password = password

    def is_valid_length(self, min_length):
        return len(self.password) >= min_length

    def has_uppercase(self):
        return any(c.isupper() for c in self.password)

    def has_lowercase(self):
        return any(c.islower() for c in self.password)

    def has_digit(self):
        return any(c.isdigit() for c in self.password)

    def has_special_character(self):
        special_chars = r"[~\!@#\$%\^&\*\(\)_\+{}\":;'\[\]]"
        return bool(re.search(special_chars, self.password))


class LoginForm(FlaskForm):
    email = StringField('Электронная почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

    def validate_password(self, password):
        validator = PasswordValidator(password.data)
        if not validator.is_valid_length(8):
            raise ValidationError('Пароль должен быть не менее 8 символов')
        if not validator.has_uppercase():
            raise ValidationError('Пароль должен содержать хотя бы одну заглавную букву')
        if not validator.has_lowercase():
            raise ValidationError('Пароль должен содержать хотя бы одну строчную букву')
        if not validator.has_digit():
            raise ValidationError('Пароль должен содержать хотя бы одну цифру')
        if not validator.has_special_character():
            raise ValidationError('Пароль должен содержать хотя бы один специальный символ')

class RegistrationForm(FlaskForm):
    email = StringField('Электронная почта', validators=[DataRequired(), Email()])
    lastname = StringField('Фамилия', validators=[DataRequired()])
    firstname = StringField('Имя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    confirm_password = PasswordField('Подтвердите пароль', 
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Зарегистрироваться')

    def validate_password(self, password):
        validator = PasswordValidator(password.data)
        if not validator.is_valid_length(8) or not validator.has_uppercase() or not validator.has_lowercase() or not validator.has_digit() or not validator.has_special_character():
            raise ValidationError(
                '''Пароль должен соответствовать следующим требованиям:\n
                Пароль должен быть не менее 8 символов длиной.\n
                Пароль должен содержать хотя бы одну заглавную букву.\n
                Пароль должен содержать хотя бы одну строчную букву.\n
                Пароль должен содержать хотя бы одну цифру.\n
                Пароль должен содержать хотя бы один специальный символ.\n''')


class ResetPasswordForm(FlaskForm):
    old_password = PasswordField('Старый пароль', validators=[DataRequired()])
    new_password = PasswordField('Новый пароль', validators=[DataRequired()])
    confirm_new_password = PasswordField(
        'Подтвердите новый пароль', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Сменить пароль')

    def validate_new_password(self, new_password):
        validator = PasswordValidator(new_password.data)
        if not validator.is_valid_length(8) or not validator.has_uppercase() or not validator.has_lowercase() or not validator.has_digit() or not validator.has_special_character():
            raise ValidationError('Новый пароль должен соответствовать определенным требованиям')

    def validate_old_password(self, old_password_field):
        if old_password_field.data == self.new_password.data:
            raise ValidationError('Новый пароль должен отличаться от старого')


class AddDishForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired(), Length(min=2, max=100)])
    description = StringField('Описание', validators=[DataRequired(), Length(min=10, max=500)])
    price = DecimalField('Цена', validators=[DataRequired(), NumberRange(min=0)])
    category = SelectField('Категория', choices=[], coerce=int, validators=[DataRequired()])
    image = FileField('Фото', validators=[FileAllowed(['jpg', 'png'], 'Images only!')])
