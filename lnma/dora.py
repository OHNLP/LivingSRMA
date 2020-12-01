import uuid
import datetime

from sqlalchemy import and_, or_, not_
from sqlalchemy.orm.attributes import flag_modified

from lnma import ss_state
from .models import *

from . import db

from lnma.util import pred_rct

IS_DELETED_YES = 'yes'
IS_DELETED_NO = 'no'

REL_PROJECT_USER_CREATOR = 'creator'

def create_project(owner_uid, title, keystr=None, abstract="", settings={}):
    """Create a project based on given parameter
    """
    # create a project
    project_id = str(uuid.uuid1())
    keystr = str(uuid.uuid1()).split('-')[0].upper() if keystr is None else keystr
    date_created = datetime.datetime.now()
    date_updated = datetime.datetime.now()
    is_deleted = IS_DELETED_NO

    project = Project(
        project_id = project_id,
        keystr = keystr,
        owner_uid = owner_uid,
        title = title,
        abstract = abstract,
        date_created = date_created,
        date_updated = date_updated,
        settings = settings,
        is_deleted = is_deleted
    )
    owner = User.query.get(owner_uid)
    project.related_users.append(owner)
    db.session.add(project)
    db.session.commit()

    return project


def get_all_projects():
    '''Get all projects for test
    '''
    projects = Project.query.all()
    return projects


def get_project(project_id):
    project = Project.query.filter(and_(
        Project.project_id == project_id
    )).first()

    return project


def add_user_to_project(uid, project_id):
    project = get_project(project_id)
    ret = project.is_user_in(uid)
    if ret[0]:
        user = ret[1]
    else:
        user = User.query.get(uid)
        project.related_users.append(user)
        db.session.commit()

    return (user, project)


def get_user(uid):
    user = User.query.filter(User.uid == uid).first()
    return user


def list_projects_by_owner_uid(owner_uid):
    projects = Project.query.filter(Project.related_users.any(uid=owner_uid)).all()
    return projects


def list_projects_by_uid(uid):
    projects = db.session.query()


def is_existed_project(project_id):
    '''Check if a project exists
    '''
    project = Project.query.filter(Project.project_id==project_id).first()

    if project is None:
        return False
    else:
        return True


def is_existed_paper(project_id, pid):
    '''Check if a pid exists

    By default check the pmid
    '''
    paper = Paper.query.filter(and_(
        Paper.project_id == project_id,
        Paper.pid == pid
    )).first()

    if paper is None:
        return False
    else:
        return True


def create_paper(project_id, pid, 
    pid_type='pmid', title=None, abstract=None,
    pub_date=None, authors=None, journal=None, meta={},
    ss_st=None, ss_pr=None, ss_rs=None, ss_ex=None, seq_num=None):
    """Create a paper object, 

    By default, the pmid. 
    Please make sure the input pmid is NOT exist
    """
    paper_id = str(uuid.uuid1())
    pid = pid
    pid_type = pid_type
    title = '' if title is None else title
    abstract = '' if abstract is None else abstract
    pub_date = '' if pub_date is None else pub_date
    authors = '' if authors is None else authors
    journal = '' if journal is None else journal
    meta = {} if meta is None else meta
    ss_st = ss_state.SS_ST_AUTO_OTHER if ss_st is None else ss_st
    ss_pr = ss_state.SS_PR_NA if ss_pr is None else ss_pr
    ss_rs = ss_state.SS_RS_NA if ss_rs is None else ss_rs
    # ss_ex is an extend attribute for each record
    ss_ex = {
        'label': {}
    } if ss_ex is None else ss_ex
    date_created = datetime.datetime.now()
    date_updated = datetime.datetime.now()
    is_deleted = IS_DELETED_NO
    if seq_num is None:
        # need to get the current max number
        max_cur_seq = get_current_max_seq_num(project_id)
        # increase one bit
        seq_num = max_cur_seq + 1

    paper = Paper(
        paper_id = paper_id,
        pid = pid,
        pid_type = pid_type,
        project_id = project_id,
        title = title,
        abstract = abstract,
        pub_date = pub_date,
        authors = authors,
        journal = journal,
        meta = meta,
        ss_st = ss_st,
        ss_pr = ss_pr,
        ss_rs = ss_rs,
        ss_ex = ss_ex,
        date_created = date_created,
        date_updated = date_updated,
        is_deleted = is_deleted,
        seq_num = seq_num
    )

    db.session.add(paper)
    db.session.commit()

    return paper
    

def update_paper_rct_result(project_id, pid):
    '''Update the RCT detection result
    '''
    paper = get_paper(project_id, pid)

    # TODO catch exception
    pred = pred_rct(paper.title, paper.abstract)
    paper.meta['pred'] = pred['pred']
    flag_modified(paper, "meta")
    
    # commit this
    db.session.add(paper)
    db.session.commit()

    return pred


def create_paper_if_not_exist(project_id, pid, 
    pid_type='pmid', title=None, abstract=None,
    pub_date=None, authors=None, journal=None, 
    ss_st=None, ss_pr=None, ss_rs=None, ss_ex=None, seq_num=None):
    '''A wrapper function for create_paper and is_existed_paper
    '''
    
    if is_existed_paper(project_id, pid, pid_type):
        return None
    else:
        p = create_paper(project_id, pid, 
            pid_type=pid_type, title=title, 
            pub_date=pub_date, authors=authors, journal=journal, 
            ss_st=ss_st, ss_pr=ss_pr, ss_rs=ss_rs, ss_ex=None, seq_num=seq_num)
        return p


def get_paper(project_id, pid):
    paper = Paper.query.filter(and_(
        Paper.project_id == project_id,
        Paper.pid == pid
    )).first()

    return paper


def get_paper_by_id(paper_id):
    paper = Paper.query.filter(and_(
        Paper.paper_id == paper_id
    )).first()

    return paper


def get_paper_by_seq(project_id, seq_num):
    paper = Paper.query.filter(and_(
        Paper.project_id == project_id,
        Paper.seq_num == seq_num
    )).first()

    return paper


def get_papers(project_id):
    papers = Paper.query.filter(and_(
        Paper.project_id == project_id
    )).order_by(Paper.date_created.desc()).all()

    return papers
    

def get_papers_by_stage(project_id, stage):
    '''Get all papers of specified stage
    '''
    print('* get_papers_by_stage [%s]' % stage)
    if stage == ss_state.SS_STAGE_ALL_OF_THEM:
        papers = Paper.query.filter(
            Paper.project_id == project_id
        ).order_by(Paper.date_updated.desc()).all()

    elif stage == ss_state.SS_STAGE_UNSCREENED:
        papers = Paper.query.filter(and_(
            Paper.project_id == project_id,
            Paper.ss_st.in_([
                ss_state.SS_ST_AUTO_EMAIL,
                ss_state.SS_ST_AUTO_SEARCH,
                ss_state.SS_ST_AUTO_OTHER
            ]),
            Paper.ss_pr == ss_state.SS_PR_NA,
            Paper.ss_rs == ss_state.SS_RS_NA
        )).order_by(Paper.date_updated.desc()).all()

    elif stage == ss_state.SS_STAGE_DECIDED:
        papers = Paper.query.filter(
            Paper.ss_rs != ss_state.SS_RS_NA
        ).order_by(Paper.date_updated.desc()).all()

    elif stage == ss_state.SS_STATE_PASSED_TITLE_NOT_FULLTEXT:
        papers = Paper.query.filter(and_(
            Paper.ss_pr == ss_state.SS_PR_PASSED_TITLE,
            Paper.ss_rs == ss_state.SS_RS_NA
        )).order_by(Paper.date_updated.desc()).all()

    elif stage == ss_state.SS_STAGE_INCLUDED_SR:
        papers = Paper.query.filter(and_(
            Paper.ss_rs.in_([
                ss_state.SS_RS_INCLUDED_ONLY_SR,
                ss_state.SS_RS_INCLUDED_SRMA
            ]),
        )).order_by(Paper.date_updated.desc()).all()

    elif stage == ss_state.SS_STAGE_INCLUDED_SRMA:
        papers = Paper.query.filter(and_(
            Paper.ss_rs == ss_state.SS_RS_INCLUDED_SRMA
        )).order_by(Paper.date_updated.desc()).all()

    elif stage == ss_state.SS_STAGE_EXCLUDED_BY_TITLE_ABSTRACT:
        papers = Paper.query.filter(and_(
            Paper.project_id == project_id,
            Paper.ss_rs.in_([
                ss_state.SS_RS_EXCLUDED_TITLE,
                ss_state.SS_RS_EXCLUDED_ABSTRACT
            ])
        )).order_by(Paper.date_updated.desc()).all()

    elif stage == ss_state.SS_STAGE_EXCLUDED_BY_TITLE:
        papers = Paper.query.filter(and_(
            Paper.project_id == project_id,
            Paper.ss_rs == ss_state.SS_RS_EXCLUDED_TITLE
        )).order_by(Paper.date_updated.desc()).all()

    elif stage == ss_state.SS_STAGE_EXCLUDED_BY_ABSTRACT:
        papers = Paper.query.filter(and_(
            Paper.project_id == project_id,
            Paper.ss_rs == ss_state.SS_RS_EXCLUDED_ABSTRACT
        )).order_by(Paper.date_updated.desc()).all()

    elif stage == ss_state.SS_STAGE_EXCLUDED_BY_FULLTEXT:
        papers = Paper.query.filter(and_(
            Paper.project_id == project_id,
            Paper.ss_rs == ss_state.SS_RS_EXCLUDED_FULLTEXT
        )).order_by(Paper.date_updated.desc()).all()

    else:
        print('* NOT found specified stage [%s]' % stage)
        papers = []
        
    return papers


def get_papers_by_stage_v1(project_id, stage):
    '''Deprecated.
    '''
    if stage == 'a1':
        papers = Paper.query.filter(and_(
            Paper.project_id == project_id,
            Paper.ss_st.in_([
                ss_state.SS_ST_AUTO_EMAIL,
                ss_state.SS_ST_AUTO_SEARCH,
                ss_state.SS_ST_AUTO_OTHER
            ])
        )).order_by(Paper.date_created.desc()).all()
    elif stage == 'a1_na_na':
        papers = Paper.query.filter(and_(
            Paper.project_id == project_id,
            Paper.ss_pr == ss_state.SS_PR_NA,
            Paper.ss_rs == ss_state.SS_RS_NA
        )).order_by(Paper.date_created.desc()).all()
    elif stage == 'a1_p2_na':
        papers = Paper.query.filter(and_(
            Paper.project_id == project_id,
            Paper.ss_pr == ss_state.SS_PR_PASSED_TITLE,
            Paper.ss_rs == ss_state.SS_RS_NA
        )).order_by(Paper.date_created.desc()).all()
    elif stage == 'a2':
        papers = Paper.query.filter(and_(
            Paper.project_id == project_id,
            Paper.ss_st.in_([
                ss_state.SS_ST_AUTO_EMAIL,
                ss_state.SS_ST_AUTO_SEARCH,
                ss_state.SS_ST_AUTO_OTHER
            ]),
            Paper.ss_rs.in_([
                ss_state.SS_RS_INCLUDED_ONLY_SR,
                ss_state.SS_RS_INCLUDED_SRMA
            ])
        )).order_by(Paper.date_created.desc()).all()
    elif stage == 'a3':
        papers = Paper.query.filter(and_(
            Paper.project_id == project_id,
            Paper.ss_st.in_([
                ss_state.SS_ST_AUTO_EMAIL,
                ss_state.SS_ST_AUTO_SEARCH,
                ss_state.SS_ST_AUTO_OTHER
            ]),
            Paper.ss_rs.in_([
                ss_state.SS_RS_INCLUDED_SRMA
            ])
        )).order_by(Paper.date_created.desc()).all()
    elif stage == 'u1':
        papers = Paper.query.filter(and_(
            Paper.project_id == project_id,
            Paper.ss_st.in_([
                ss_state.SS_ST_AUTO_EMAIL,
                ss_state.SS_ST_AUTO_SEARCH,
                ss_state.SS_ST_AUTO_OTHER
            ]),
            Paper.ss_pr == ss_state.SS_PR_UPDATE_EXIST,
            Paper.ss_rs.in_([
                ss_state.SS_RS_INCLUDED_ONLY_SR,
                ss_state.SS_RS_INCLUDED_SRMA
            ])
        )).order_by(Paper.date_created.desc()).all()
    elif stage == 'u2':
        papers = Paper.query.filter(and_(
            Paper.project_id == project_id,
            Paper.ss_st.in_([
                ss_state.SS_ST_AUTO_EMAIL,
                ss_state.SS_ST_AUTO_SEARCH,
                ss_state.SS_ST_AUTO_OTHER
            ]),
            Paper.ss_pr == ss_state.SS_PR_UPDATE_EXIST,
            Paper.ss_rs.in_([
                ss_state.SS_RS_INCLUDED_SRMA
            ])
        )).order_by(Paper.date_created.desc()).all()
    elif stage == 'f1':
        papers = Paper.query.filter(and_(
            Paper.project_id == project_id,
            Paper.ss_rs.in_([
                ss_state.SS_RS_INCLUDED_ONLY_SR,
                ss_state.SS_RS_INCLUDED_SRMA
            ])
        )).order_by(Paper.date_created.desc()).all()
    elif stage == 'f2':
        papers = Paper.query.filter(and_(
            Paper.project_id == project_id,
            Paper.ss_rs.in_([
                ss_state.SS_RS_INCLUDED_SRMA
            ])
        )).order_by(Paper.date_created.desc()).all()
    elif stage == 'e1':
        papers = Paper.query.filter(and_(
            Paper.project_id == project_id,
            Paper.ss_rs.in_([
                ss_state.SS_RS_EXCLUDED_TITLE
            ])
        )).order_by(Paper.date_created.desc()).all()
    elif stage == 'e2':
        papers = Paper.query.filter(and_(
            Paper.project_id == project_id,
            Paper.ss_rs.in_([
                ss_state.SS_RS_EXCLUDED_FULLTEXT
            ])
        )).order_by(Paper.date_created.desc()).all()
    elif stage == 'e3':
        papers = Paper.query.filter(and_(
            Paper.project_id == project_id,
            Paper.ss_rs.in_([
                ss_state.SS_RS_INCLUDED_ONLY_SR
            ])
        )).order_by(Paper.date_created.desc()).all()
    else:
        papers = []

    return papers


def set_paper_pr_rs(paper_id, pr=None, rs=None):
    paper = Paper.query.filter_by(
        paper_id=paper_id
    ).first()
    
    if pr is not None: paper.ss_pr = pr
    if rs is not None: paper.ss_rs = rs

    # automatic update the date_updated
    paper.date_updated = datetime.datetime.now()

    db.session.add(paper)
    db.session.commit()

    return paper


def set_paper_pr_rs_with_details(paper_id, pr=None, rs=None, detail_dict=None):
    '''Set the pr and rs state with more detail

    The detail is a dict that will be added/overwrite the paper.
    '''
    paper = Paper.query.filter_by(
        paper_id=paper_id
    ).first()
    
    if pr is not None: paper.ss_pr = pr
    if rs is not None: paper.ss_rs = rs
    if detail_dict is not None:
        for key in detail_dict:
            if detail_dict[key] is None:
                # which means remove this key
                if key in paper.ss_ex:
                    del paper.ss_ex[key]
                else:
                    pass
            else:
                paper.ss_ex[key] = detail_dict[key]
        flag_modified(paper, "ss_ex")

    # automatic update the date_updated
    paper.date_updated = datetime.datetime.now()

    db.session.add(paper)
    db.session.commit()
    return paper


def set_paper_ss_label(paper_id, label):
    '''Set the ss label for paper
    '''
    paper = Paper.query.filter_by(
        paper_id=paper_id
    ).first()

    if 'label' not in paper.ss_ex:
        paper.ss_ex['label'] = {}

    # set the label
    paper.ss_ex['label'][label] = {
        'name': label
    }
    flag_modified(paper, "ss_ex")

    # automatic update the date_updated
    paper.date_updated = datetime.datetime.now()

    db.session.add(paper)
    db.session.commit()
    return paper


def unset_paper_ss_label(paper_id, label):
    '''Unset the ss label for paper
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


def set_rct_user_feedback(paper_id, usr_fb):
    '''Set the user feedback for RCT result
    '''
    paper = Paper.query.filter_by(
        paper_id=paper_id
    ).first()

    if 'usr_fb' not in paper.meta['pred'][0]:
        paper.meta['pred'][0]['usr_fb'] = ''

    paper.meta['pred'][0]['usr_fb'] = usr_fb
    flag_modified(paper, "meta")

    db.session.add(paper)
    db.session.commit()
    
    return paper


def get_screener_stat_by_stage(project_id, stage):
    '''Get the statistics on specified type
    '''
    ss_cond = ''
    if stage not in ss_state.SS_STAGE_CONDITIONS:
        return None

    # get condition for this type, e.g., 
    ss_cond = ss_state.SS_STAGE_CONDITIONS[stage]

    # get the stat on the given type
    sql = """
    select project_id,
        count(case when {ss_cond} then paper_id else null end) as {stage}
    from papers
    where project_id = '{project_id}'
    group by project_id
    """.format(project_id=project_id, ss_cond=ss_cond, stage=stage)
    r = db.session.execute(sql).fetchone()
    
    if r == None: 
        result = {
            stage: None
        }
    else:
        result = {
            stage: r[stage]
        }

    return result


def get_screener_stat_by_project_id(project_id):
    '''Get the statistics of the project for the screener
    '''
    sql = """
    select project_id,
        count(*) as all_of_them,
        count(case when ss_st in ('a10', 'a11', 'a12') and ss_pr = 'na' and ss_rs = 'na' then paper_id else null end) as unscreened,
        count(case when ss_st in ('a10', 'a11', 'a12') and ss_pr = 'na' and ss_rs = 'na' and json_contains_path(ss_ex->'$.label', 'one', '$.CKL') then paper_id else null end) as unscreened_ckl,

        count(case when ss_pr = 'p20' and ss_rs = 'na' then paper_id else null end) as passed_title_not_fulltext,
        count(case when ss_pr = 'p20' and ss_rs = 'na' and json_contains_path(ss_ex->'$.label', 'one', '$.CKL') then paper_id else null end) as passed_title_not_fulltext_ckl,
        
        count(case when ss_rs = 'e2' then paper_id else null end) as excluded_by_title,
        count(case when ss_rs = 'e22' then paper_id else null end) as excluded_by_abstract,
        count(case when ss_rs in ('e2', 'e22') then paper_id else null end) as excluded_by_title_abstract,
        count(case when ss_rs = 'e21' then paper_id else null end) as excluded_by_rct_classifier,
        count(case when ss_rs = 'e3' then paper_id else null end) as excluded_by_fulltext,

        count(case when ss_rs = 'f1' then paper_id else null end) as included_only_sr,
        count(case when ss_rs in ('f1', 'f3') then paper_id else null end) as included_sr,
        count(case when ss_rs = 'f3' then paper_id else null end) as included_srma,

        count(case when ss_rs != 'na' then paper_id else null end) as decided
    
    from papers
    where project_id = '{project_id}'
        and is_deleted = 'no'
    group by project_id
    """.format(project_id=project_id)
    r = db.session.execute(sql).fetchone()

    # put the values in result data
    attrs = [
        'all_of_them',
        'unscreened',
        'unscreened_ckl',

        'passed_title_not_fulltext',
        'passed_title_not_fulltext_ckl',

        'excluded_by_title',
        'excluded_by_abstract',
        'excluded_by_title_abstract',
        'excluded_by_rct_classifier',
        'excluded_by_fulltext',
        'included_only_sr',
        'included_sr',
        'included_srma',
        'decided'
    ]
    result = {}
    for attr in attrs:
        result[attr] = r[attr]

    return result


def get_current_max_seq_num(project_id):
    '''Get the max seq number
    '''
    sql = """
    select max(seq_num) as max_cur_seq
    from papers
    where project_id = '{project_id}';
    """.format(project_id=project_id)

    r = db.session.execute(sql).fetchone()

    # the max_cur_seq should be an integer
    # but it also can be None
    max_cur_seq = r['max_cur_seq']
    if max_cur_seq is None:
        max_cur_seq = 0

    return max_cur_seq


def get_prisma(project_id):
    '''Get the statistics of the project for the PRISMA
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
