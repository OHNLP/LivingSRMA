import json

from flask import request
from flask import flash
from flask import render_template
from flask import Blueprint
from flask import current_app
from flask import jsonify

from flask_login import login_required
from flask_login import current_user

from lnma import dora
from lnma import ss_state

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
    papers = dora.get_papers_by_stage(project_id, stage)
    json_papers = [ p.as_very_simple_dict() for p in papers ]

    ret = {
        'success': True,
        'msg': '',
        'papers': json_papers
    }
    return jsonify(ret)


@bp.route('/create_extract', methods=['POST'])
@login_required
def create_extract():
    project_id = request.form.get('project_id')
    oc_type = request.form.get('oc_type')
    abbr = request.form.get('abbr')
    meta = json.loads(request.form.get('meta'))
    data = json.loads(request.form.get('data'))

    # get the exisiting extracts
    extract = dora.create_extract(
        project_id,
        oc_type,
        abbr,
        meta,
        data
    )

    # build the return obj
    ret = {
        'success': True,
        'msg': '',
        'extract': extract.as_dict()
    }
    return jsonify(ret)


@bp.route('/get_extract_and_papers')
@login_required
def get_extract_and_papers():
    project_id = request.args.get('project_id')
    abbr = request.args.get('abbr')
    
    # get the exisiting extracts
    extract = dora.get_extract_by_project_id_and_abbr(project_id, abbr)

    # get papers
    stage = ss_state.SS_STAGE_INCLUDED_SR
    papers = dora.get_papers_by_stage(project_id, stage)

    # merge the return obj
    ret = {
        'success': True,
        'msg': '',
        'extract': extract.as_dict(),
        'papers': [ p.as_simple_dict() for p in papers ]
    }
    return jsonify(ret)


@bp.route('/get_extracts')
@login_required
def get_extracts():
    project_id = request.args.get('project_id')
    
    # get the exisiting extracts
    extracts = dora.get_extracts_by_project_id(project_id)

    # build the return obj
    ret = {
        'success': True,
        'msg': '',
        'extracts': [ extr.as_dict() for extr in extracts ]
    }
    return jsonify(ret)
