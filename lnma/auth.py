import functools

from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for

from flask_login import UserMixin
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user

from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from .models import User

bp = Blueprint("auth", __name__, url_prefix="/auth")

users = {'sysadmin@linma.org': {'password': 'lnma2020'}}


def user_loader(email):
    user = User.query.get(email)
    return user


def request_loader(request):
    email = request.form.get('email')
    if email not in users:
        return

    user = User()
    user.id = email

    # DO NOT ever store passwords in plaintext and always compare password
    # hashes using constant-time comparison!
    user.is_authenticated = request.form['password'] == users[email]['password']

    return user


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('auth_login.html')

    email = request.form['email']

    if email not in users:
        return 'No such user'

    if request.form['password'] == users[email]['password']:
        user = User()
        user.id = email
        login_user(user)
        return redirect(url_for('user_portal.index'))

    return 'Bad login'


@bp.route('/logout')
def logout():
    logout_user()
    return 'Logged out'