from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin):
    def __init__(self, id, email, password, lastname, firstname,
                 role, last_activity, password_changed, status):
        self.id = id
        self.email = email
        self.password = password
        self.lastname = lastname
        self.firstname = firstname
        self.role = role
        self.last_activity = last_activity
        self.password_changed = password_changed
        self.status = status

    def get_id(self):
        return self.id

    def get_role(self):
        return self.role

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_old_password(self, password):
        return check_password_hash(self.password, password)


class Role:
    def __init__(self, role):
        self.id = id
        self.role = role
