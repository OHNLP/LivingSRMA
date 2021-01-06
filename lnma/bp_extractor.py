from flask import request
from flask import flash
from flask import render_template
from flask import Blueprint
from flask import current_app
from flask import jsonify

from flask_login import login_required
from flask_login import current_user

from lnma import dora

bp = Blueprint("extractor", __name__, url_prefix="/extractor")

@bp.route('/v1')
@login_required
def v1():
    return render_template('extractor/v1.html')


@bp.route('/get_papers_by_stage')
@login_required
def get_papers_by_stage():
    project_id = request.args.get('project_id')
    stage = request.args.get('stage')
    if stage != 'f1':
        return jsonify({
            'success': False,
            'msg': 'wrong stage'
        })

    papers = dora.get_papers_by_stage(project_id, stage)
    json_papers = [ p.as_very_simple_dict() for p in papers ]

    ret = {
        'success': True,
        'msg': '',
        'papers': json_papers
    }
    return jsonify(ret)


@bp.route('/get_outcome_and_papers')
@login_required
def get_outcome_and_papers():
    project_id = request.args.get('project_id')
    stage = 'f1'

    papers = dora.get_papers_by_stage(project_id, stage)
    json_papers = [ p.as_very_simple_dict() for p in papers ]

    # merge the papers and the existing outcome 

    ret = {
        'success': True,
        'msg': '',
        'oc': json_papers
    }
    return jsonify(ret)