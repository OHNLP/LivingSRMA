import uuid
import datetime

from sqlalchemy import and_, or_, not_

from lnma import ss_state
from .models import *

from . import db

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
    ss_st=None, ss_pr=None, ss_rs=None, ss_ex=None):
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
    ss_ex = {} if ss_ex is None else ss_ex
    date_created = datetime.datetime.now()
    date_updated = datetime.datetime.now()
    is_deleted = IS_DELETED_NO

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
        is_deleted = is_deleted
    )

    db.session.add(paper)
    db.session.commit()

    return paper
    

def create_paper_if_not_exist(project_id, pid, 
    pid_type='pmid', title=None, abstract=None,
    pub_date=None, authors=None, journal=None, 
    ss_st=None, ss_pr=None, ss_rs=None, ss_ex=None):
    '''A wrapper function for create_paper and is_existed_paper
    '''
    
    if is_existed_paper(project_id, pid, pid_type):
        return None
    else:
        p = create_paper(project_id, pid, 
            pid_type=pid_type, title=title, 
            pub_date=pub_date, authors=authors, journal=journal, 
            ss_st=ss_st, ss_pr=ss_pr, ss_rs=ss_rs, ss_ex=None)
        return p


def get_papers(project_id):
    papers = Paper.query.filter(and_(
        Paper.project_id == project_id
    )).order_by(Paper.date_created.desc()).all()

    return papers


def get_papers_by_stage(project_id, stage):
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
            Paper.ss_pr == ss_state.SS_PR_CHECKED_TITLE,
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

    db.session.commit()

    return paper


def get_prisma(project_id):
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
