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
    project.users.append(owner)
    db.session.add(project)
    db.session.commit()

    return project


def list_projects_by_owner_uid(owner_uid):
    projects = Project.query.filter(Project.users.any(uid=owner_uid)).all()
    return projects


def is_existed_project(project_id):
    '''Check if a project exists
    '''
    project = Project.query.filter(Project.project_id==project_id).first()

    if project is None:
        return False
    else:
        return True


def is_existed_paper(project_id, pid, pid_type='pmid'):
    '''Check if a pid exists

    By default check the pmid
    '''
    paper = Paper.query.filter(and_(
        Paper.project_id == project_id,
        Paper.pid == pid,
        Paper.pid_type == pid_type
    )).first()

    if paper is None:
        return False
    else:
        return True


def create_paper(project_id, pid, 
    pid_type='pmid', title=None, 
    pub_date=None, authors=None, journal=None, ss_st=None):
    """Create a paper object, 

    By default, the pmid. 
    Please make sure the input pmid is NOT exist
    """
    paper_id = str(uuid.uuid1())
    pid = pid
    pid_type = pid_type
    title = '' if title is None else title
    pub_date = '' if pub_date is None else pub_date
    authors = '' if authors is None else authors
    journal = '' if journal is None else journal
    ss_st = ss_state.SS_ST_AUTO_PMID if ss_st is None else ss_st
    ss_pr = ss_state.SS_PR_NA
    ss_rs = ss_state.SS_RS_NA
    date_created = datetime.datetime.now()
    date_updated = datetime.datetime.now()
    is_deleted = IS_DELETED_NO

    paper = Paper(
        paper_id = paper_id,
        pid = pid,
        pid_type = pid_type,
        project_id = project_id,
        title = title,
        pub_date = pub_date,
        authors = authors,
        journal = journal,
        ss_st = ss_st,
        ss_pr = ss_pr,
        ss_rs = ss_rs,
        date_created = date_created,
        date_updated = date_updated,
        is_deleted = is_deleted
    )

    db.session.add(paper)
    db.session.commit()

    return paper
    

def create_paper_if_not_exist(project_id, pid, 
    pid_type='pmid', title=None, 
    pub_date=None, authors=None, journal=None, ss_st=None):
    '''A wrapper function for create_paper and is_existed_paper
    '''
    
    if is_existed_paper(project_id, pid, pid_type):
        return None
    else:
        p = create_paper(project_id, pid, 
            pid_type=pid_type, title=title, 
            pub_date=pub_date, authors=authors, journal=journal, ss_st=ss_st)
        return p


def get_papers(project_id):
    papers = Paper.query.filter(and_(
        Paper.project_id == project_id
    )).all()

    return papers


def get_unscreened_papers(project_id):
    papers = Paper.query.filter(and_(
        Paper.project_id == project_id,
        Paper.ss_rs == ss_state.SS_RS_NA
    )).all()

    return papers


def get_prisma(project_id):
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
        count(case when ss_st in ('a10', 'a11', 'a12') and ss_rs = 'na' then paper_id else null end) as a1_na_na,
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

    # put the values in prisma dict
    prisma = {
        'sskeys': r.keys()
    }
    for k in r.keys():
        prisma[k] = r[k]

    return prisma
