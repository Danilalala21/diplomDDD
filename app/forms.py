from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SubmitField, 
    BooleanField, SelectField, TextAreaField)
from wtforms.validators import (
    DataRequired, EqualTo, ValidationError, Length, Email)
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
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Login')

    def validate_password(self, password):
        validator = PasswordValidator(password.data)
        if not validator.is_valid_length(8):
            raise ValidationError('Password must be at least 8 characters long')
        if not validator.has_uppercase():
            raise ValidationError('Password must contain at least one uppercase letter')
        if not validator.has_lowercase():
            raise ValidationError('Password must contain at least one lowercase letter')
        if not validator.has_digit():
            raise ValidationError('Password must contain at least one digit')
        if not validator.has_special_character():
            raise ValidationError('Password must contain at least one special character')

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    firstname = StringField('First Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', 
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_password(self, password):
        validator = PasswordValidator(password.data)
        if not validator.is_valid_length(8) or not validator.has_uppercase() or not validator.has_lowercase() or not validator.has_digit() or not validator.has_special_character():
            raise ValidationError(
                '''Password must meet certain requirements:\n
                Password must be at least 8 characters long.\n
                Password must contain at least one uppercase letter.\n
                Password must contain at least one lowercase letter.\n
                Password must contain at least one digit.\n
                Password must contain at least one special character.\n''')


class ResetPasswordForm(FlaskForm):
    old_password = PasswordField('Old password', validators=[DataRequired()])
    new_password = PasswordField('New password', validators=[DataRequired()])
    confirm_new_password = PasswordField(
        'Confirm new password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Change password')

    def validate_new_password(self, new_password):
        validator = PasswordValidator(new_password.data)
        if not validator.is_valid_length(8) or not validator.has_uppercase() or not validator.has_lowercase() or not validator.has_digit() or not validator.has_special_character():
            raise ValidationError('New password must meet certain requirements')
        
    def validate_old_password(self, old_password_field):
        if old_password_field.data == self.new_password.data:
            raise ValidationError('New password must be different from old password')
