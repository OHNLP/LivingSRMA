import json

from flask import request
from flask import flash
from flask import render_template
from flask import Blueprint
from flask import current_app
from flask import jsonify
from flask import redirect
from flask import url_for

from flask_login import login_required
from flask_login import current_user

from lnma import dora, srv_paper
from lnma.models import *
from lnma import ss_state
from lnma.util import get_today_date_str

bp = Blueprint("screener", __name__, url_prefix="/screener")

@bp.context_processor
def inject_enumerate():
    return dict(enumerate=enumerate)


@bp.route('/')
@login_required
def index():
    return render_template('screener.index_v3.html')


@bp.route('/overview')
@login_required
def overview():
    project_id = request.cookies.get('project_id')

    if project_id is None:
        return redirect(url_for('project.mylist'))

    project = dora.get_project(project_id)

    return render_template(
        'screener/overview.html',
        project=project,
        project_json_str=json.dumps(project.as_dict())
    )


@bp.route('/pcq_selector')
@login_required
def pcq_selector():
    project_id = request.cookies.get('project_id')

    if project_id is None:
        return redirect(url_for('project.mylist'))

    project = dora.get_project(project_id)

    return render_template(
        'screener/pcq_selector.html',
        project=project,
        project_json_str=json.dumps(project.as_dict())
    )


###############################################################################
# AJAX API functions for screener
###############################################################################

@bp.route('/get_paper_by_id')
@login_required
def get_paper_by_id():
    paper_id = request.args.get('paper_id')
    project_id = request.cookies.get('project_id')

    if project_id is None:
        return redirect(url_for('project.mylist'))

    paper = dora.get_paper_by_id(paper_id)
    project = dora.get_project(project_id)

    # check this paper
    if paper is None:
        json_paper = None
    else:
        if paper.is_ss_included_in_project():
            paper.update_ss_cq_by_cqs(
                project.settings['clinical_questions']
            )
        json_paper = paper.as_dict()

    ret = {
        'success': True,
        'paper': json_paper
    }
    return jsonify(ret)


@bp.route('/get_papers')
@login_required
def get_papers():
    project_id = request.args.get('project_id')
    papers = dora.get_papers(project_id)

    json_papers = [ p.as_very_simple_dict() for p in papers ]

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
    json_papers = [  ]
    for p in papers:
        d = p.as_very_simple_dict()

        # remove some unused information in first look
        del d['date_updated']
        del d['year']
        if 'pred_dict' in d['meta']: del d['meta']['pred_dict']
        if 'all_rct_ids' in d['meta']: del d['meta']['all_rct_ids']

        json_papers.append(d)

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

    # 2021-08-17: extend the rst with cq-level result

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


@bp.route('/set_rct_id', methods=['GET', 'POST'])
@login_required
def set_rct_id():
    paper_id = request.form.get('paper_id')
    rct_id = request.form.get('rct_id')
    is_success, paper = dora.set_paper_rct_id(paper_id, rct_id)

    ret = {
        'success': True,
        'paper': paper.as_very_simple_dict()
    }
    return jsonify(ret)


@bp.route('/set_pmid', methods=['GET', 'POST'])
@login_required
def set_pmid():
    paper_id = request.form.get('paper_id')
    pmid = request.form.get('pmid')
    is_success, paper = dora.set_paper_pmid(paper_id, pmid)

    ret = {
        'success': is_success,
        'paper': paper.as_very_simple_dict()
    }
    
    return jsonify(ret)


@bp.route('/set_pub_date', methods=['GET', 'POST'])
@login_required
def set_pub_date():
    paper_id = request.form.get('paper_id')
    pub_date = request.form.get('pub_date')
    # TODO check the pub_date

    is_success, paper = dora.set_paper_pub_date(paper_id, pub_date)

    ret = {
        'success': is_success,
        'paper': paper.as_very_simple_dict()
    }
    
    return jsonify(ret)


@bp.route('/set_ss_cq', methods=['GET', 'POST'])
@login_required
def set_ss_cq():
    paper_id = request.form.get('paper_id')
    cq_abbr = request.form.get('cq_abbr')
    ss_cq = request.form.get('ss_cq')

    is_success, paper = srv_paper.set_paper_ss_cq(paper_id, cq_abbr, ss_cq)

    ret = {
        'success': is_success,
        'paper': paper.as_very_simple_dict() if is_success else None
    }
    return jsonify(ret)


@bp.route('/set_ss_cq_exclude_reason', methods=['GET', 'POST'])
@login_required
def set_ss_cq_exclude_reason():
    paper_id = request.form.get('paper_id')
    cq_abbr = request.form.get('cq_abbr')
    ss_cq = request.form.get('ss_cq')
    exclude_reason = request.form.get('reason')

    is_success, paper = srv_paper.set_paper_ss_cq(
        paper_id, cq_abbr, settings.PAPER_SS_EX_SS_CQ_NO,
        exclude_reason
    )

    ret = {
        'success': is_success,
        'paper': paper.as_very_simple_dict() if is_success else None
    }
    return jsonify(ret)


@bp.route('/add_tag', methods=['GET', 'POST'])
@login_required
def add_tag():
    paper_id = request.form.get('paper_id')
    tag = request.form.get('tag')
    is_success, paper = dora.add_paper_tag(paper_id, tag)

    ret = {
        'success': True,
        'paper': paper.as_very_simple_dict()
    }
    return jsonify(ret)


@bp.route('/toggle_tag', methods=['GET', 'POST'])
@login_required
def toggle_tag():
    paper_id = request.form.get('paper_id')
    tag = request.form.get('tag')
    is_success, paper = dora.toggle_paper_tag(paper_id, tag)

    ret = {
        'success': True,
        'paper': paper.as_very_simple_dict()
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
        papers.append(p.as_simple_dict())

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
        papers.append(p.as_simple_dict())

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
        papers.append(p.as_simple_dict())

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
        papers.append(p.as_simple_dict())

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
        papers.append(p.as_simple_dict())

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
        papers.append(p.as_simple_dict())

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
    reason = request.form.get('reason')
    paper_ids = paper_ids.split(',')

    papers = []
    
    # create a dict for the details
    # detail_dict = {
    #     'date_decided': get_today_date_str(),
    #     'reason': reason,
    #     'decision': ss_state.SS_STAGE_INCLUDED_SR
    # }

    detail_dict = util.get_decision_detail_dict(
        reason, ss_state.SS_STAGE_INCLUDED_SR
    )

    project = dora.get_project(project_id)
    # for those included in sr, also included in each sub cq
    detail_dict['ss_cq'] = srv_paper.make_ss_cq_dict(project)

    for paper_id in paper_ids:
        p = dora.set_paper_pr_rs_with_details(
            paper_id, 
            pr=ss_state.SS_PR_CHECKED_SR,
            rs=ss_state.SS_RS_INCLUDED_ONLY_SR,
            detail_dict=detail_dict)
        papers.append(p.as_simple_dict())

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
        papers.append(p.as_simple_dict())

    ret = {
        'success': True,
        'papers': papers
    }
    return jsonify(ret)


@bp.route('/sspr/set_label_ckl', methods=['GET', 'POST'])
@login_required
def sspr_set_label_ckl():
    project_id = request.form.get('project_id')
    paper_ids = request.form.get('paper_ids')
    paper_ids = paper_ids.split(',')
    
    papers = []

    for paper_id in paper_ids:
        p = srv_paper.set_paper_ss_label(
            paper_id, ss_state.SS_LABEL_CKL,
            current_user
        )
        papers.append(p.as_simple_dict())

    ret = {
        'success': True,
        'papers': papers
    }
    return jsonify(ret)


@bp.route('/sspr/unset_label_ckl', methods=['GET', 'POST'])
@login_required
def sspr_unset_label_ckl():
    project_id = request.form.get('project_id')
    paper_ids = request.form.get('paper_ids')
    paper_ids = paper_ids.split(',')
    
    papers = []

    for paper_id in paper_ids:
        p = srv_paper.unset_label_check_later(paper_id)
        papers.append(p.as_simple_dict())

    ret = {
        'success': True,
        'papers': papers
    }
    return jsonify(ret)


@bp.route('/sspr/set_rct_feedback', methods=['GET', 'POST'])
@login_required
def sspr_set_rct_feedback():
    project_id = request.form.get('project_id')
    paper_ids = request.form.get('paper_ids')
    paper_ids = paper_ids.split(',')
    
    feedback = request.form.get('feedback')
    papers = []

    for paper_id in paper_ids:
        paper = dora.set_rct_user_feedback(paper_id, feedback)
        papers.append(paper.as_simple_dict())

    ret = {
        'success': True,
        'papers': papers
    }
    return jsonify(ret)


###############################################################################
# Internal functions for screener
###############################################################################

# def set_label_check_later(paper_id):
#     '''
#     Set the "check later" label for study
#     '''
#     paper = dora.set_paper_ss_label(paper_id, ss_state.SS_LABEL_CKL)
#     return paper


# def unset_label_check_later(paper_id):
#     '''
#     Unset the "check later" label for study
#     '''
#     paper = dora.unset_paper_ss_label(paper_id, ss_state.SS_LABEL_CKL)
#     return paper


def create_pr_rs_details(reason, decision):
    """
    Create detail_dict
    """
    detail_dict = {
        'date_decided': get_today_date_str(),
        'reason': reason,
        'decision': decision
    }

    return detail_dict