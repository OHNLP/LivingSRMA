from flask import Blueprint
from flask import render_template
from flask import send_from_directory
from flask import current_app

from flask_login import login_required
from flask_login import current_user

from lnma.settings import *

bp = Blueprint("index", __name__, url_prefix="/")

@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/f/<fn>')
def f(fn):
    return send_from_directory(TMP_FOLDER, fn)


@bp.route('/err_permission_denied')
def err_permission_denied():
    return render_template('index.err_permission_denied.html')