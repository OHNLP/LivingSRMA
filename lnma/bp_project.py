from flask import request
from flask import flash
from flask import render_template
from flask import Blueprint
from flask import jsonify
from flask import current_app

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
        owner_uid = current_user.uid,
        title = request.form.get('title'),
        keystr = request.form.get('keystr'),
        abstract = request.form.get('abstract'),
        settings={'collect_template': {}}
    )

    flash('Project is created!')

    return 'OK!'


@bp.route('/list', methods=['GET', 'POST'])
@login_required
def list():
    if request.method == 'GET':
        return render_template('project.list.html')

    projects = dora.list_projects_by_owner_uid(current_user.uid)


@bp.route('/editor')
@login_required
def editor():
    return render_template('project.editor.html')


###############################################################
# APIs for project
###############################################################

@bp.route('/api/list')
@login_required
def api_list():
    projects = dora.list_projects_by_owner_uid(current_user.uid)

    ret = {
        'success': True,
        'projects': [ project.as_dict() for project in projects ]
    }

    return jsonify(ret)