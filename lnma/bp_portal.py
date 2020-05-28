from flask import request
from flask import flash
from flask import render_template
from flask import Blueprint
from flask import current_app

from flask_login import login_required
from flask_login import current_user

from lnma import dora

bp = Blueprint("portal", __name__, url_prefix="/portal")

@bp.route('/')
@login_required
def index():
    return render_template('portal.index.html')
