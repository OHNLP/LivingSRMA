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
from lnma import ss_state
from lnma.util import get_today_date_str

bp = Blueprint("screener", __name__, url_prefix="/screener")

@bp.route('/')
@login_required
def index():
    return render_template('screener.index_v3.html')


@bp.route('/overview')
@login_required
def overview():
    return render_template('screener/overview.html')


@bp.route('/get_papers')
@login_required
def get_papers():
    project_id = request.args.get('project_id')
    papers = dora.get_papers(project_id)

    json_papers = [ p.as_dict() for p in papers ]

    ret = {
        'success': True,
        'papers': json_papers
    }
    return jsonify(ret)


@bp.route('/get_papers_by_stage')
@login_required
def get_papers_by_stage():
    project_id = request.args.get('project_id')
    stage = request.args.get('stage')
    papers = dora.get_papers_by_stage(project_id, stage)
    json_papers = [ p.as_dict() for p in papers ]

    ret = {
        'success': True,
        'papers': json_papers
    }
    return jsonify(ret)


@bp.route('/get_stat')
@login_required
def get_stat():
    project_id = request.args.get('project_id')
    rst = dora.get_screener_stat_by_project_id(project_id)
    ret = {
        'success': True,
        'stat': rst
    }
    return jsonify(ret)


@bp.route('/get_prisma')
@login_required
def get_prisma():
    project_id = request.args.get('project_id')
    prisma = dora.get_prisma(project_id)
    ret = {
        'success': True,
        'prisma': prisma
    }
    return jsonify(ret)


@bp.route('/sspr/exclude_all', methods=['GET', 'POST'])
@login_required
def sspr_exclude_all():
    project_id = request.form.get('project_id')

    return ''


@bp.route('/sspr/set_papers_unscreened', methods=['GET', 'POST'])
@login_required
def sspr_set_papers_unscreened():
    project_id = request.form.get('project_id')
    paper_ids = request.form.get('paper_ids')
    paper_ids = paper_ids.split(',')

    papers = []
    
    # create a dict for the details
    # this stage is not a decision stage
    detail_dict = {
        'date_decided': None,
        'reason': None,
        'decision': None
    }
    for paper_id in paper_ids:
        p = dora.set_paper_pr_rs_with_details(
            paper_id,
            pr=ss_state.SS_PR_NA, 
            rs=ss_state.SS_RS_NA,
            detail_dict=detail_dict)
        papers.append(p.as_dict())

    ret = {
        'success': True,
        'papers': papers
    }
    return jsonify(ret)


@bp.route('/sspr/set_papers_needchkft', methods=['GET', 'POST'])
@login_required
def sspr_set_papers_needchkft():
    project_id = request.form.get('project_id')
    paper_ids = request.form.get('paper_ids')
    paper_ids = paper_ids.split(',')

    papers = []
    
    # create a dict for the details
    # this stage is not a decision stage
    detail_dict = {
        'date_decided': None,
        'reason': None,
        'decision': None
    }
    for paper_id in paper_ids:
        p = dora.set_paper_pr_rs_with_details(
            paper_id,
            pr=ss_state.SS_PR_PASSED_TITLE, 
            rs=ss_state.SS_RS_NA,
            detail_dict=detail_dict)
        papers.append(p.as_dict())

    ret = {
        'success': True,
        'papers': papers
    }
    return jsonify(ret)


@bp.route('/sspr/exclude_papers_ta', methods=['GET', 'POST'])
@login_required
def sspr_exclude_papers_ta():
    '''Deprecated. Use specified reason instead.
    '''
    project_id = request.form.get('project_id')
    paper_ids = request.form.get('paper_ids')
    paper_ids = paper_ids.split(',')

    papers = []
    for paper_id in paper_ids:
        p = dora.set_paper_pr_rs(paper_id, 
            pr=ss_state.SS_PR_PASSED_TITLE, 
            rs=ss_state.SS_RS_EXCLUDED_TITLE)
        papers.append(p.as_dict())

    ret = {
        'success': True,
        'papers': papers
    }
    return jsonify(ret)


@bp.route('/sspr/exclude_papers_tt', methods=['GET', 'POST'])
@login_required
def sspr_exclude_papers_tt():
    project_id = request.form.get('project_id')
    paper_ids = request.form.get('paper_ids')
    reason = ""
    paper_ids = paper_ids.split(',')

    papers = []

    # create a dict for the details
    detail_dict = {
        'date_decided': get_today_date_str(),
        'reason': reason,
        'decision': ss_state.SS_STAGE_EXCLUDED_BY_TITLE
    }
    for paper_id in paper_ids:
        p = dora.set_paper_pr_rs_with_details(
            paper_id, 
            pr=ss_state.SS_PR_PASSED_TITLE, 
            rs=ss_state.SS_RS_EXCLUDED_TITLE,
            detail_dict=detail_dict)
        papers.append(p.as_dict())

    ret = {
        'success': True,
        'papers': papers
    }
    return jsonify(ret)


@bp.route('/sspr/exclude_papers_ab', methods=['GET', 'POST'])
@login_required
def sspr_exclude_papers_ab():
    project_id = request.form.get('project_id')
    paper_ids = request.form.get('paper_ids')
    reason = ""
    paper_ids = paper_ids.split(',')

    papers = []

    # create a dict for the details
    detail_dict = {
        'date_decided': get_today_date_str(),
        'reason': reason,
        'decision': ss_state.SS_STAGE_EXCLUDED_BY_ABSTRACT
    }

    for paper_id in paper_ids:
        p = dora.set_paper_pr_rs_with_details(
            paper_id, 
            pr=ss_state.SS_PR_PASSED_TITLE, 
            rs=ss_state.SS_RS_EXCLUDED_ABSTRACT,
            detail_dict=detail_dict)
        papers.append(p.as_dict())

    ret = {
        'success': True,
        'papers': papers
    }
    return jsonify(ret)


@bp.route('/sspr/exclude_papers_ft', methods=['GET', 'POST'])
@login_required
def sspr_exclude_papers_ft():
    project_id = request.form.get('project_id')
    paper_ids = request.form.get('paper_ids')
    # need to provide reason for ex ft
    reason = request.form.get('reason')
    paper_ids = paper_ids.split(',')
    
    papers = []
    
    # create a dict for the details
    detail_dict = {
        'date_decided': get_today_date_str(),
        'reason': reason,
        'decision': ss_state.SS_STAGE_EXCLUDED_BY_FULLTEXT
    }

    for paper_id in paper_ids:
        p = dora.set_paper_pr_rs_with_details(
            paper_id, 
            pr=ss_state.SS_PR_CHECKED_FULLTEXT, 
            rs=ss_state.SS_RS_EXCLUDED_FULLTEXT,
            detail_dict=detail_dict)
        papers.append(p.as_dict())

    ret = {
        'success': True,
        'papers': papers
    }
    return jsonify(ret)


@bp.route('/sspr/include_papers_sr', methods=['GET', 'POST'])
@login_required
def sspr_include_papers_sr():
    project_id = request.form.get('project_id')
    paper_ids = request.form.get('paper_ids')
    reason = ""
    paper_ids = paper_ids.split(',')

    papers = []
    
    # create a dict for the details
    detail_dict = {
        'date_decided': get_today_date_str(),
        'reason': reason,
        'decision': ss_state.SS_STAGE_INCLUDED_SR
    }

    for paper_id in paper_ids:
        p = dora.set_paper_pr_rs_with_details(
            paper_id, 
            pr=ss_state.SS_PR_CHECKED_SR,
            rs=ss_state.SS_RS_INCLUDED_ONLY_SR,
            detail_dict=detail_dict)
        papers.append(p.as_dict())

    ret = {
        'success': True,
        'papers': papers
    }
    return jsonify(ret)


@bp.route('/sspr/include_papers_srma', methods=['GET', 'POST'])
@login_required
def sspr_include_papers_srma():
    project_id = request.form.get('project_id')
    paper_ids = request.form.get('paper_ids')
    reason = ""
    paper_ids = paper_ids.split(',')

    papers = []

    # create a dict for the details
    detail_dict = {
        'date_decided': get_today_date_str(),
        'reason': reason,
        'decision': ss_state.SS_STAGE_INCLUDED_SR
    }

    for paper_id in paper_ids:
        p = dora.set_paper_pr_rs_with_details(
            paper_id,
            pr=ss_state.SS_PR_CHECKED_SRMA,
            rs=ss_state.SS_RS_INCLUDED_SRMA,
            detail_dict=detail_dict)
        papers.append(p.as_dict())

    ret = {
        'success': True,
        'papers': papers
    }
    return jsonify(ret)


