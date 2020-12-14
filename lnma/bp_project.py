from flask import request
from flask import flash
from flask import render_template
from flask import Blueprint
from flask import jsonify
from flask import current_app
from flask import redirect

from flask_login import login_required
from flask_login import current_user

from lnma import dora

bp = Blueprint("project", __name__, url_prefix="/project")

@bp.route('/')
@login_required
def index():
    return render_template('project/index.html')


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'GET':
        return render_template('project/create.html')

    query = request.form.get('query')

    project = dora.create_project(
        owner_uid = current_user.uid,
        title = request.form.get('title'),
        keystr = request.form.get('keystr'),
        abstract = request.form.get('abstract'),
        settings={
            'collect_template': {},
            'query': query
        }
    )

    flash('Project is created!')

    return redirect(url_for('project.list'))


@bp.route('/list', methods=['GET', 'POST'])
@login_required
def list():
    if request.method == 'GET':
        return render_template('project/list.html')

    projects = dora.list_projects_by_uid(current_user.uid)


@bp.route('/editor')
@login_required
def editor():
    return render_template('project/editor.html')


###############################################################
# APIs for project
###############################################################

@bp.route('/api/list')
@login_required
def api_list():
    projects = dora.list_projects_by_uid(current_user.uid)

    ret = {
        'success': True,
        'projects': [ project.as_dict() for project in projects ]
    }

    return jsonify(ret)


@bp.route('/api/get_project')
@login_required
def api_get_project():
    projects = dora.list_projects_by_uid(current_user.uid)

    ret = {
        'success': True,
        'projects': [ project.as_dict() for project in projects ]
    }

    return jsonify(ret)


@bp.route('/api/add_user_to_project', methods=['GET', 'POST'])
@login_required
def api_add_user_to_project():
    if request.method == 'GET':
        return redirect(url_for('project.list'))

    to_add_uid = request.form.get('uid', None)
    project_id = request.form.get('project_id', None)
    current_user_uid = current_user.uid

    # TODO validate the project is belong to current user

    # add the to_add_uid
    to_add_user, project = dora.add_user_to_project(to_add_uid, project_id)

    # TODO check the result
    
    flash("Added %s to Project [%s]" % (user.uid, project.title))

    return redirect(url_for('project.list'))