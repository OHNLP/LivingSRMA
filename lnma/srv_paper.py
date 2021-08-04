import time
from sqlalchemy import and_, or_, not_
from sqlalchemy.orm.attributes import flag_modified

from tqdm import tqdm 

from lnma import settings
from lnma import util
from lnma import dora
from lnma import ss_state
from lnma import db

from lnma.models import *


def get_paper_data_in_itable():
    '''
    '''
    pass


def get_included_papers_by_cq(project_id, cq_abbr):
    '''
    Get all papers that meet the requrements
    '''
    papers = Paper.query.filter(and_(
        Paper.project_id == project_id,
        Paper.ss_rs.in_([
            ss_state.SS_RS_INCLUDED_ONLY_SR,
            ss_state.SS_RS_INCLUDED_SRMA
        ]),
        Paper.is_deleted == settings.PAPER_IS_DELETED_NO,
        Paper.ss_ex['ss_cq'][cq_abbr] == settings.PAPER_SS_EX_SS_CQ_YES
    )).order_by(Paper.date_updated.desc()).all()

    return papers


def make_ss_cq_dict(project):
    '''
    Make an initial ss_cq based on a project
    '''
    d = {}
    for cq in project.settings['clinical_questions']:
        d[cq['abbr']] = settings.SCREENER_DEFAULT_DECISION_FOR_CQ_INCLUSION

    return d


def set_paper_ss_cq(paper_id, cq_abbr, ss_cq):
    '''
    Set the ss_cq for a paper
    '''
    paper = dora.get_paper_by_id(paper_id)

    if paper is None:
        return False, None

    if 'ss_cq' not in paper.ss_ex:
        paper.ss_ex['ss_cq'] = {}

    paper.ss_ex['ss_cq'][cq_abbr] = ss_cq

    flag_modified(paper, 'ss_ex')
    db.session.add(paper)
    db.session.commit()

    return True, paper


def set_paper_rct_id(keystr, pid, rct_id):
    '''
    Set the RCT ID for a paper
    '''
    if not util.is_valid_rct_id(rct_id):
        return False, None

    paper = dora.get_paper_by_keystr_and_pid(
        keystr, pid
    )

    # hmmm ... why?
    if paper is None:
        return False, None

    # if it's the same, no need to update
    if paper.meta['rct_id'] == rct_id:
        return True, paper

    # update the paper
    is_success, paper = dora.set_paper_rct_id(
        paper.paper_id, rct_id
    )

    return is_success, paper


def set_paper_ss_decision(keystr, pid, ss_pr, ss_rs, reason, stage):
    '''
    Set paper screening decision

    The input parameters must be decided in advance
    '''
    paper = dora.get_paper_by_keystr_and_pid(
        keystr, pid
    )

    # what??? 
    if paper is None:
        return False, None

    # create a dict for the details
    detail_dict = util.get_decision_detail_dict(
        reason, stage
    )

    # update the ss for this paper
    p = dora.set_paper_pr_rs_with_details(
        paper.paper_id, 
        pr=ss_pr,
        rs=ss_rs,
        detail_dict=detail_dict
    )

    return True, p


def set_paper_pred(keystr, pid, model_id, result):
    '''
    Set the paper prediction
    '''
    paper = dora.get_paper_by_keystr_and_pid(
        keystr, pid
    )

    # hmmm ... why?
    if paper is None:
        return False, None

    # check the `pred_dict` attribute in meta
    if 'pred_dict' not in paper.meta:
        # ok, this is a new record
        paper.meta['pred_dict'] = {}

        # put the existing result
        if 'pred' in paper.meta and len(paper.meta['pred'])>0:
            paper.meta['pred_dict'][settings.AI_MODEL_ROBOTSEARCH_RCT] = \
                paper.meta['pred'][0]

    # update the meta
    paper.meta['pred_dict'][model_id] = result
    dora._update_paper_meta(paper)

    return True, paper
    

def update_paper_pub_date(keystr, pid):
    '''
    Update the pub_date for the given paper in a project
    '''
    # first, get this paper
    # TODO check availablity
    paper = dora.get_paper_by_keystr_and_pid(
        keystr=keystr, pid=pid
    )

    # if this paper exists, then check the pid
    if not paper.is_pmid():
        # we don't have any way to update non-pmid records
        return False, paper

    # if this paper has the pmid
    ret = util.e_fetch([pid])

    # for most of the time
    pub_date = ret['result'][pid]['date_pub']

    # update the paper
    paper = dora.update_paper_pub_date(paper.paper_id, pub_date)

    return True, paper


def update_all_srma_paper_pub_date(keystr):
    '''
    Update all SRMA paper pub_date
    '''
    project = dora.get_project_by_keystr(keystr)
    papers = dora.get_papers_by_stage(
        project.project_id, 
        ss_state.SS_STAGE_INCLUDED_SR
    )

    cnt_success = 0
    for paper in tqdm(papers):
        success, p = update_paper_pub_date(project.keystr, paper.pid)
        if success: 
            print('* updated %s %s -> %s' % (
                p.pid, paper.pub_date, p.pub_date
            ))
            cnt_success += 1
        else:
            print('* NO %s %s -> %s' % (
                p.pid, paper.pub_date, p.pub_date
            ))

        time.sleep(1.5)

    print('* finished %s / %s success, %s not updated' % (
        cnt_success, len(papers), 
        len(papers) - cnt_success
    ))

    return True
    

if __name__ == '__main__':
    # for debug purpose
    from lnma import db, create_app
    app = create_app()
    db.init_app(app)
    app.app_context().push()

    update_all_srma_paper_pub_date('IO')