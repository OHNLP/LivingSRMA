from flask import request
from flask import flash
from flask import render_template
from flask import Blueprint
from flask import current_app

from flask_login import login_required
from flask_login import current_user

from lnma import dora

bp = Blueprint("collector", __name__, url_prefix="/collector")

@bp.route('/')
@login_required
def index():
    return render_template('collector.index.html')


@bp.route('/pdfviewer')
@login_required
def pdfviewer():
    return render_template('collector.pdfviewer.html')