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

from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

bp = Blueprint("sysmgr", __name__, url_prefix="/sysmgr")


@bp.route('/')
@login_required
def index():
    return render_template('sysmgr.index.html')

