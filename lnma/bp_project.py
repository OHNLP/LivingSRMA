from flask import request
from flask import flash
from flask import render_template
from flask import Blueprint

from flask_login import login_required
from flask_login import current_user

from lnma import dora

bp = Blueprint("project", __name__, url_prefix="/project")

@bp.route('/')
@login_required
def index():
    return render_template('project.index.html')


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'GET':
        return render_template('project.create.html')

    project = dora.create_project(
        keystr = request.form.get('keystr'),
        owner_uid = current_user.uid,
        title = request.form.get('title'),
        abstract = request.form.get('abstract'),
        settings={'collect_template': {}}
    )

    print(project)
    flash('Project is created!')

    return 'OK!'