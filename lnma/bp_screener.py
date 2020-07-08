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

bp = Blueprint("screener", __name__, url_prefix="/screener")

@bp.route('/')
@login_required
def index():
    return render_template('screener.index_v3.html')


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


@bp.route('/get_papers_by_stage', methods=['GET', 'POST'])
@login_required
def get_papers_by_stage():
    project_id = request.form.get('project_id')
    stage = request.form.get('stage')
    papers = dora.get_papers_by_stage(project_id, stage)
    json_papers = [ p.as_dict() for p in papers ]

    ret = {
        'success': True,
        'papers': json_papers
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


@bp.route('/sspr/exclude_papers_ta', methods=['GET', 'POST'])
@login_required
def sspr_exclude_papers_ta():
    project_id = request.form.get('project_id')
    paper_ids = request.form.get('paper_ids')
    paper_ids = paper_ids.split(',')
    print(paper_ids)

    papers = []
    for paper_id in paper_ids:
        p = dora.set_paper_pr_rs(paper_id, 
            pr=ss_state.SS_PR_CHECKED_TITLE, 
            rs=ss_state.SS_RS_EXCLUDED_TITLE)
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
    paper_ids = paper_ids.split(',')
    print(paper_ids)

    papers = []
    for paper_id in paper_ids:
        p = dora.set_paper_pr_rs(paper_id, 
            pr=ss_state.SS_PR_CHECKED_FULLTEXT, 
            rs=ss_state.SS_RS_EXCLUDED_FULLTEXT)
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
    print(paper_ids)

    papers = []
    for paper_id in paper_ids:
        p = dora.set_paper_pr_rs(paper_id,
            pr=ss_state.SS_PR_CHECKED_TITLE, 
            rs=ss_state.SS_RS_NA)
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
    paper_ids = paper_ids.split(',')
    print(paper_ids)

    papers = []
    for paper_id in paper_ids:
        p = dora.set_paper_pr_rs(paper_id, rs='f1')
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
    paper_ids = paper_ids.split(',')
    print(paper_ids)

    papers = []
    for paper_id in paper_ids:
        p = dora.set_paper_pr_rs(paper_id, rs='f3')
        papers.append(p.as_dict())

    ret = {
        'success': True,
        'papers': papers
    }
    return jsonify(ret)


