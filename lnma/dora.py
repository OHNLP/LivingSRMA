import uuid
import datetime

from lnma import ss_state
from .models import Project
from .models import Paper
from .models import Note

from . import db

IS_DELETED_YES = 'yes'
IS_DELETED_NO = 'no'

def create_project(keystr, owner_uid, title, abstract, settings):
    """Create a project based on given parameter
    """
    project_id = str(uuid.uuid1())
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

    db.session.add(project)
    db.session.commit()

    return project


def create_paper_by_pmid(project_id, pmid):
    """Create a paper object by only the pmid
    """
    paper_id = str(uuid.uuid1())
    pid = pmid
    pid_type = 'pmid'
    title = ''
    pub_date = ''
    authors = ''
    journal = ''
    ss_st = ss_state.SS_ST_AUTO_PMID
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
    
