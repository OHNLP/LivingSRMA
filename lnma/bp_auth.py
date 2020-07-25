import functools

from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from flask import current_app

from flask_login import UserMixin
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user
from flask_login import current_user

from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from .models import User

bp = Blueprint("auth", __name__, url_prefix="/auth")

def user_loader(email):
    user = User.query.get(email)
    return user


def request_loader(request):
    email = request.form.get('email')    
    pswd = request.form.get('password')
    user = User.query.get(email)

    if user is None:
        return None

    # DO NOT ever store passwords in plaintext and always compare password
    # hashes using constant-time comparison!
    if check_password_hash(user.password, pswd):
        user.is_authenticated = True
    else:
        user.is_authenticated = False
        
    return user


def is_role(role):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            if role in current_user.role:
                return func(*args, **kw)
            else:
                return redirect(url_for('index.err_permission_denied'))
        return wrapper
    return decorator


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('auth.login.html')

    email = request.form.get('email')
    pswd = request.form.get('password')

    user = User.query.get(email)
    
    if user is None:
        flash("User doesn't exist or wrong password")
        return render_template('auth.login.html')

    if check_password_hash(user.password, pswd):
        login_user(user)
        return redirect(url_for('portal.index'))

    flash("User doesn't exist or wrong password.")
    return render_template('auth.login.html')


@bp.route('/logout')
def logout():
    logout_user()
    flash("You have logged out.")
    return redirect(url_for('auth.login'))