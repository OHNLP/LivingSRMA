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
    # make a ref in the extract for frontend display
    # make sure every selected paper is listed in extract.data
    pids = set([])
    for paper in papers:
        pid = paper.pid
        # record this pid for next step
        pids.add(pid)

        # check if this pid exists in extract
        if pid in extract.data:
            # nothing to do if has added
            continue

        # if not exist, add this paper
        extract.data[pid] = {
            'selected': False,
            'attrs': {}
        }
        # put the attrs
        for attr in extract.meta['attrs']:
            extract.data[pid]['attrs'][attr] = ''

    # reverse search, unselect those are not in papers
    for pid in extract.data:
        if pid in pids:
            # which means this pid is in the SR stage
            continue

        # if not, just unselect this paper
        # don't delete
        extract.data[pid]['selected'] = False
        
    ret = {
        'success': True,
        'msg': '',
        'extract': extract.as_dict(),
        'papers': [ p.as_simple_dict() for p in papers ]
    }
    return jsonify(ret)


@bp.route('/update_extract', methods=['POST'])
@login_required
def update_extract():
    project_id = request.form.get('project_id')
    oc_type = request.form.get('oc_type')
    abbr = request.form.get('abbr')
    # the meta of the extract settings
    meta = json.loads(request.form.get('meta'))
    # the data of the extracted infos
    data = json.loads(request.form.get('data'))
    
    # update the extract with given info
    extract = dora.update_extract_meta_and_data(
        project_id, oc_type, abbr, meta, data
    )

    # build the return obj
    ret = {
        'success': True,
        'msg': '',
        'extract': extract.as_dict()
    }
    return jsonify(ret)


@bp.route('/copy_extract', methods=['POST'])
@login_required
def copy_extract():
    project_id = request.form.get('project_id')
    oc_type = request.form.get('oc_type')
    abbr = request.form.get('abbr')
    # the meta of the extract settings
    meta = json.loads(request.form.get('meta'))
    # the data of the extracted infos
    data = json.loads(request.form.get('data'))

    # the new extract
    new_abbr = request.form.get('new_abbr')
    new_full_name = request.form.get('new_full_name')
    
    # update the extract with given info
    _ = dora.update_extract_meta_and_data(
        project_id, oc_type, abbr, meta, data
    )

    # update the meta
    meta['abbr'] = new_abbr
    meta['full_name'] = new_full_name

    # save the extract with given info
    extract = dora.create_extract(
        project_id, oc_type, new_abbr, meta, data
    )

    # build the return obj
    ret = {
        'success': True,
        'msg': '',
        'extract': extract.as_dict()
    }
    return jsonify(ret)


@bp.route('/delete_extract', methods=['POST'])
@login_required
def delete_extract():
    project_id = request.form.get('project_id')
    oc_type = request.form.get('oc_type')
    abbr = request.form.get('abbr')
    
    # get the exisiting extracts
    _ = dora.delete_extract(project_id, oc_type, abbr)

    # build the return obj
    ret = {
        'success': True,
        'msg': ''
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

