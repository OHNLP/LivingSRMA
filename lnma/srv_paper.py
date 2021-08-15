import time
import datetime

from sqlalchemy import and_, or_, not_
from sqlalchemy.orm.attributes import flag_modified

from tqdm import tqdm

from lnma import settings
from lnma import util
from lnma import dora
from lnma import ss_state
from lnma import db

from lnma.models import *


def set_paper_ss_label(paper_id, label, user=None):
    '''
    Set the ss label for paper
    '''
    paper = Paper.query.filter_by(
        paper_id=paper_id
    ).first()

    if 'label' not in paper.ss_ex:
        paper.ss_ex['label'] = {}

    # set the label
    paper.ss_ex['label'][label] = {
        'name': label,
        'date': datetime.datetime.now().strftime('%Y-%m-%d')
    }
    
    if user is not None:
        paper.ss_ex['label'][label]['user'] = {
            'uid': user.uid,
            'abbr': user.get_abbr()
        }

    flag_modified(paper, "ss_ex")

    # automatic update the date_updated
    paper.date_updated = datetime.datetime.now()

    db.session.add(paper)
    db.session.commit()
    return paper


def unset_paper_ss_label(paper_id, label):
    '''
    Unset the ss label for paper
    '''
    paper = Paper.query.filter_by(
        paper_id=paper_id
    ).first()

    # first, check the "label" category exists
    if 'label' not in paper.ss_ex:
        paper.ss_ex['label'] = {}

    # set the label itself
    if label in paper.ss_ex['label']:
        del paper.ss_ex['label'][label]
    
    flag_modified(paper, "ss_ex")

    # automatic update the date_updated
    paper.date_updated = datetime.datetime.now()

    db.session.add(paper)
    db.session.commit()
    return paper


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
    if len(project.settings['clinical_questions']) == 1:
        decision = settings.PAPER_SS_EX_SS_CQ_YES
    else:
        decision = settings.PAPER_SS_EX_SS_CQ_NO

    for cq in project.settings['clinical_questions']:
        d[cq['abbr']] = decision

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
    

def get_prisma_bef(project_id):
    '''
    Get the statistics for the PRISMA
    Including:

    - b: batch number
    - e: excluded
    - f: final number

    '''
    # get the basic stats
    stat = dora.get_screener_stat_by_project_id(project_id)

    # get the NCT number states
    papers = dora.get_papers(project_id)
    b1_study_list = []
    b4_study_list = []
    b5_study_list = []
    e1_study_list = []
    e2_study_list = []
    e3_study_list = []
    f1_study_list = []
    f2_study_list = []
    
    f1_paper_list = []
    f2_paper_list = []

    for paper in papers:
        rct_id = ''
        if 'rct_id' in paper.meta:
            rct_id = paper.meta['rct_id']
        
        # use the pid as rct id if it is missing
        if rct_id == '':
            rct_id = paper.pid

        stages = paper.get_ss_stages()
        # print(paper.ss_rs, stages)

        if ss_state.SS_STAGE_INCLUDED_SR in stages:
            f1_study_list.append(rct_id)
            f1_paper_list.append(paper.pid)

        if ss_state.SS_STAGE_INCLUDED_SRMA in stages:
            f2_study_list.append(rct_id)
            f2_paper_list.append(paper.pid)

    prisma = {
        'b1': {
            "n_ctids": len(b1_study_list),
            "n_pmids": stat[ss_state.SS_STAGE_ALL_OF_THEM],
        },
        'b2': {
            "n_ctids": 0,
            "n_pmids": 0,
        },
        'b3': {
            "n_ctids": 0,
            "n_pmids": 0,
        },
        'b4': {
            "n_ctids": len(b4_study_list),
            "n_pmids": stat[ss_state.SS_STAGE_DECIDED]
                - stat[ss_state.SS_STAGE_EXCLUDED_BY_FULLTEXT],
        },
        'b5': {
            "n_ctids": len(b5_study_list),
            "n_pmids": stat[ss_state.SS_STAGE_INCLUDED_SR]
                + stat[ss_state.SS_STAGE_EXCLUDED_BY_ABSTRACT]
        },

        'e1': {
            "n_ctids": len(e1_study_list),
            "n_pmids": stat[ss_state.SS_STAGE_EXCLUDED_BY_TITLE],
        },
        'e2': {
            "n_ctids": len(e2_study_list),
            "n_pmids": stat[ss_state.SS_STAGE_EXCLUDED_BY_ABSTRACT],
        },
        'e3': {
            "n_ctids": len(e3_study_list),
            "n_pmids": stat[ss_state.SS_STAGE_EXCLUDED_BY_FULLTEXT],
        },

        'f1': {
            "n_ctids": len(f1_study_list),
            "n_pmids": stat[ss_state.SS_STAGE_INCLUDED_SR],
            "study_list": f1_study_list,
            "paper_list": f1_paper_list
        },
        'f2': {
            "n_ctids": len(f2_study_list),
            "n_pmids": stat[ss_state.SS_STAGE_INCLUDED_SRMA],
            "study_list": f2_study_list,
            "paper_list": f2_paper_list
        }
    }

    return prisma, stat


def get_prisma_abeuf(project_id):
    '''
    Get the statistics of the project for the PRISMA
    Including:

    - a auto update
    - b batch number
    - e excluded
    - u updated
    - f final

    '''
    stages = [
        { "stage": "b1", "text": "Records retrieved from database search" },
        { "stage": "b2", "text": "Records identified through other sources" },
        { "stage": "b3", "text": "Records after removing dupicates" },
        { "stage": "b4", "text": "Records initialized screened" },
        { "stage": "b5", "text": "Full-text articles assessed for eligibility" },
        { "stage": "b6", "text": "Studies included in systematic review" },
        { "stage": "b7", "text": "Studies included in meta-analysis" },
        { "stage": "e1", "text": "Excluded by title and abstract review" },
        { "stage": "e2", "text": "Excluded by full text review" },
        { "stage": "e3", "text": "Studies not included in meta-analysis" },
        { "stage": "a1", "text": "Records identified through automated search" },
        { "stage": "a1_na_na", "text": "Unscreened records" },
        { "stage": "a1_p2_na", "text": "Records need to check full text" },
        { "stage": "a2", "text": "New studies included in systematic review" },
        { "stage": "a3", "text": "New studies included in meta-analysis" },
        { "stage": "u1", "text": "Updated studies in SR" },
        { "stage": "u2", "text": "Updated studies in MA" },
        { "stage": "f1", "text": "Final number in qualitative synthesis (systematic review)" },
        { "stage": "f2", "text": "Final number in quantitative synthesis (meta-analysis)" }
    ]
    sql = """
    select project_id,
        count(*) as cnt,
        count(case when ss_st = 'b10' then paper_id else null end) as b1,
        count(case when ss_st = 'b12' then paper_id else null end) as b2,
        count(case when ss_st in ('b10', 'b12') and ss_rs != 'e1' then paper_id else null end) as b3,
        count(case when ss_st in ('b10', 'b12') and ss_rs != 'e1' then paper_id else null end) as b4,
        count(case when ss_st in ('b10', 'b12') and ss_rs != 'e1' and ss_rs != 'e2' then paper_id else null end) as b5,
        count(case when ss_st in ('b10', 'b12') and ss_rs in ('f1', 'f3') then paper_id else null end) as b6,
        count(case when ss_st in ('b10', 'b12') and ss_rs = 'f3' then paper_id else null end) as b7,
        
        count(case when ss_rs = 'e2' then paper_id else null end) as e1,
        count(case when ss_rs = 'e3' then paper_id else null end) as e2,
        count(case when ss_rs = 'f1' then paper_id else null end) as e3,

        count(case when ss_st in ('a10', 'a11', 'a12') then paper_id else null end) as a1,
        count(case when ss_st in ('a10', 'a11', 'a12') and ss_pr = 'na' and ss_rs = 'na' then paper_id else null end) as a1_na_na,
        count(case when ss_st in ('a10', 'a11', 'a12') and ss_pr = 'p20' and ss_rs = 'na' then paper_id else null end) as a1_p2_na,
        count(case when ss_st in ('a10', 'a11', 'a12') and ss_rs in ('f1', 'f3') then paper_id else null end) as a2,
        count(case when ss_st in ('a10', 'a11', 'a12') and ss_rs = 'f3' then paper_id else null end) as a3,
        
        count(case when ss_st in ('a10', 'a11', 'a12') and ss_pr = 'p40' and ss_rs in ('f1', 'f3') then paper_id else null end) as u1,
        count(case when ss_st in ('a10', 'a11', 'a12') and ss_pr = 'p40' and ss_rs = 'f3' then paper_id else null end) as u2,
        
        count(case when ss_rs in ('f1', 'f3') then paper_id else null end) as f1,
        count(case when ss_rs = 'f3' then paper_id else null end) as f2

    from papers
    where project_id = '{project_id}'
        and is_deleted = 'no'
    group by project_id
    """.format(project_id=project_id)
    r = db.session.execute(sql).fetchone()

    if r is None:
        prisma = {
            'stages': stages
        }
        for k in stages:
            prisma[k['stage']] = 0
        return prisma

    # put the values in prisma dict
    prisma = {
        'stages': stages
    }
    for k in r.keys():
        prisma[k] = r[k]

    return prisma
    

# if __name__ == '__main__':
#     # for debug purpose
#     from lnma import db, create_app
#     app = create_app()
#     db.init_app(app)
#     app.app_context().push()

#     update_all_srma_paper_pub_date('IO')