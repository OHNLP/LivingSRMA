from flask import request
from flask import flash
from flask import render_template
from flask import Blueprint
from flask import current_app

from flask_login import login_required
from flask_login import current_user

from lnma import dora

bp = Blueprint("study", __name__, url_prefix="/study")

@bp.route('/')
@login_required
def index():
    return render_template('study.index.html')


@bp.route('/timeline')
@login_required
def timeline():
    return render_template('study.timeline.html')