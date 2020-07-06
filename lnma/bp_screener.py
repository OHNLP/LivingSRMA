from flask import request
from flask import flash
from flask import render_template
from flask import Blueprint
from flask import current_app
from flask import jsonify

from flask_login import login_required
from flask_login import current_user

from lnma import dora
from lnma.models import *

bp = Blueprint("screener", __name__, url_prefix="/screener")

@bp.route('/')
@login_required
def index():
    return render_template('screener.index.html')


@bp.route('/get_papers', methods=['GET', 'POST'])
@login_required
def get_papers():
    project_id = request.form.get('project_id')
    papers = dora.get_papers(project_id)

    json_papers = [ p.as_dict() for p in papers ]

    ret = {
        'success': True,
        'papers': json_papers
    }
    return jsonify(ret)
