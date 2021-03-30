import uuid
import datetime

from werkzeug.security import generate_password_hash

from sqlalchemy import and_, or_, not_
from sqlalchemy.orm.attributes import flag_modified

from lnma import ss_state
from .models import *

from . import db

from lnma.util import get_year, pred_rct
from lnma.util import get_nct_number

IS_DELETED_YES = 'yes'
IS_DELETED_NO = 'no'

REL_PROJECT_USER_CREATOR = 'creator'

def create_project(owner_uid, title, keystr=None, abstract="", settings=None):
    """Create a project based on given parameter
    """
    # create a project
    project_id = str(uuid.uuid1())
    if keystr is None or keystr.strip() == '':
        keystr = str(uuid.uuid1()).split('-')[0].upper()
    else:
        pass

    # detect if the keystr exists
    _p = get_project_by_keystr(keystr)
    if _p is not None:
        # existed???
        return None

    date_created = datetime.datetime.now()
    date_updated = datetime.datetime.now()
    is_deleted = IS_DELETED_NO

    # settings is very very very important!
    if settings is None:
        settings = {
            'collect_template': {},
            'query': '',
            'criterias': {
                "inclusion": "",            # string, the inclusion criteria
                "exclusion": "",            # string, the exclusion criteria
            },
            "exclusion_reasons": [          # a list of strings for the reasons
                "Conference Abstract"
            ],
            "highlight_keywords": {         # the keywords for highlight title or abs
                "inclusion": [              # the inclusion keywords
                    'phase 3'
                ],             
                "exclusion": [              # the exclusion keywords
                    'meta-analysis'
                ]              
            },
            "tags": [                       # a list of strings for the tags
                "Other MA"
            ],
        }

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


def get_project_by_keystr(keystr):
    project = Project.query.filter(and_(
        Project.keystr == keystr
    )).first()

    return project


def list_all_projects():
    '''Get all projects for test
    '''
    projects = Project.query.all()
    return projects


def create_user(uid, first_name, last_name, password, role='user'):
    '''
    Create a user in this database
    '''
    user = User(
        uid = uid,
        password = generate_password_hash(password),
        first_name = first_name,
        last_name = last_name,
        role = role,
        is_deleted = IS_DELETED_NO
    )
    db.session.add(user)
    db.session.commit()

    return user


def reset_user_password(uid, password):
    '''
    Reset user password
    '''
    user = User.query.get(uid)

    if user is None:
        return False, None
    else:
        user.password = generate_password_hash(password)
        db.session.commit()
        return True, user
        

def is_existed_user(uid):
    '''
    Check whether the specified user exists
    '''
    user = get_user(uid)

    if user is None:
        return False, None
    else:
        return True, user


def create_user_if_not_exist(uid, first_name, last_name, password, role='user'):
    '''
    Create a user in this database if not existed
    '''
    is_existed, user = is_existed_user(uid)

    if is_existed:
        return is_existed, user
    else:
        user = create_user(
            uid = uid, 
            first_name = first_name,
            last_name = last_name,
            password = password,
            role = role
        )
        return is_existed, user


def add_user_to_project_by_keystr_if_not_in(uid, keystr):
    '''
    Add user to a project by the keystr
    '''
    project = get_project_by_keystr(keystr)
    if project is None:
        return None, None, None

    return add_user_to_project_if_not_in(uid, project.project_id)


def add_user_to_project_if_not_in(uid, project_id):
    project = get_project(project_id)
    if project is None:
        return None, None, None

    is_in, user = project.is_user_in(uid)
    if is_in:
        pass
    else:
        user = User.query.get(uid)
        if user is None:
            return None, None, project

        project.related_users.append(user)
        db.session.commit()

    return (is_in, user, project)


def remove_user_from_project_by_keystr_if_in(uid, keystr):
    '''
    Remove user from a project
    '''
    project = get_project_by_keystr(keystr)
    if project is None:
        return None, None, None

    is_in, user = project.is_user_in(uid)

    if is_in:
        user = User.query.get(uid)
        if user is None:
            return None, None, project
        project.related_users.remove(user)
        db.session.commit()

    return (is_in, user, project)


def get_user(uid):
    user = User.query.filter(User.uid == uid).first()
    return user


def list_all_users():
    users = User.query.all()
    return users


def count_projects(uid=None):
    '''
    Count how many projects a user has
    '''

    if uid is None:
        cnt = Project.query.count()
    else:
        cnt = Project.query.filter_by(
            Project.related_users.any(
                uid=uid
            )
        ).count()

    return cnt
    

def list_projects_by_uid(owner_uid):
    projects = Project.query.filter(Project.related_users.any(uid=owner_uid)).all()
    return projects


def delete_project(project_id):
    '''
    Delete a project (and related relations with users)
    '''
    p = Project.query.filter_by(
        project_id=project_id
    ).first()

    if p is None:
        return False

    db.session.delete(p)
    db.session.commit()

    return True


def delete_project_and_papers(project_id):
    '''
    Delete a project and related papers
    '''
    prj = Project.query.filter_by(
        project_id=project_id
    ).first()

    if prj is None:
        return False

    # first, delete those papers
    Paper.query.filter_by(
        project_id=project_id
    ).delete()

    # second, delete the project
    db.session.delete(prj)

    # commit
    db.session.commit()

    return True


def is_existed_project(project_id):
    '''Check if a project exists
    '''
    project = Project.query.filter(Project.project_id==project_id).first()

    if project is None:
        return False
    else:
        return True


def set_project_criterias(project_id, inclusion_criterias, exclusion_criterias):
    '''
    Set the inclusion/exclusion criterias list for a project
    '''
    project = get_project(project_id)
    if project is None:
        return False, None

    if 'criterias' not in project.settings:
        project.settings['criterias'] = {
            "inclusion": '',
            "exclusion": ''
        }

    project.settings['criterias']['inclusion'] = inclusion_criterias
    project.settings['criterias']['exclusion'] = exclusion_criterias
    
    flag_modified(project, "settings")

    # commit this
    db.session.add(project)
    db.session.commit()

    return True, project


def set_project_exclusion_reasons(project_id, exclusion_reasons):
    '''
    Set the exclusion_reasons for a project
    '''
    project = get_project(project_id)
    if project is None:
        return False, None

    if 'exclusion_reasons' not in project.settings:
        project.settings['exclusion_reasons'] = []

    project.settings['exclusion_reasons'] = exclusion_reasons
    flag_modified(project, "settings")

    # commit this
    db.session.add(project)
    db.session.commit()

    return True, project


def set_project_highlight_keywords(project_id, highlight_keywords):
    '''
    Set the highlight_keywords list for a project
    '''
    project = get_project(project_id)
    if project is None:
        return False, None

    if 'highlight_keywords' not in project.settings:
        project.settings['highlight_keywords'] = {
            "inclusion": [],
            "exclusion": []
        }

    project.settings['highlight_keywords'] = highlight_keywords
    flag_modified(project, "settings")

    # commit this
    db.session.add(project)
    db.session.commit()

    return True, project


def set_project_tags(project_id, tags):
    '''
    Set the tag list for a project
    '''
    project = get_project(project_id)
    if project is None:
        return False, None

    if 'tags' not in project.settings:
        project.settings['tags'] = []

    project.settings['tags'] = tags
    flag_modified(project, "settings")

    # commit this
    db.session.add(project)
    db.session.commit()

    return True, project


def set_project_pdf_keywords(project_id, keywords, other_keywords=None):
    '''
    Set the pdf keywords list for a project
    '''
    project = get_project(project_id)
    if project is None:
        return False, None

    if 'pdf_keywords' not in project.settings:
        project.settings['pdf_keywords'] = {
            "main": []
        }

    if 'main' not in project.settings['pdf_keywords']:
        project.settings['pdf_keywords']['main'] = []

    project.settings['pdf_keywords']['main'] = keywords
    flag_modified(project, "settings")

    # commit this
    db.session.add(project)
    db.session.commit()

    return True, project


def sort_paper_rct_seq_in_project(project_id):
    '''
    Sort the paper's rct seq

    Based on 
    '''
    papers = get_papers(project_id)

    # get all nct
    ncts = {}

    n_papers = 0
    for paper in papers:
        if paper.meta['rct_id'] == '': continue

        # update the rct
        nct = paper.meta['rct_id']
        if nct not in ncts:
            ncts[nct] = {
                'rct_seq': {},
                'papers': []
            }

        ncts[nct]['papers'].append({
            'pid': paper.pid,
            'pub_date': get_year(paper.pub_date)
        })

        n_papers += 1

    print('* found %d papers of %d RCT_ID' % (
        n_papers, len(ncts)
    ))
    
    # sort the nct's paper
    for nct in ncts:
        ncts[nct]['papers'] = sorted(
            ncts[nct]['papers'],
            key=lambda p: p['pub_date']
        )
        for i, p in enumerate(ncts[nct]['papers']):
            ncts[nct]['rct_seq'][p['pid']] = i

    print('* sorted all nct and papers')

    # update the paper
    n_updates = 0
    for paper in papers:
        if paper.meta['rct_id'] == '':
            paper.meta['rct_seq'] = None
            paper.meta['study_type'] = None
            flag_modified(paper, 'meta')

        else:
            nct = paper.meta['rct_id']
            
            rct_seq = ncts[nct]['rct_seq'][paper.pid]
            if rct_seq == 0:
                study_type = settings.PAPER_STUDY_TYPE_ORIGINAL
            else:
                study_type = settings.PAPER_STUDY_TYPE_FOLLOWUP
            
            paper.meta['rct_seq'] = rct_seq
            paper.meta['study_type'] = study_type
            flag_modified(paper, 'meta')

            db.session.add(paper)
            n_updates += 1

    # commit!
    db.session.commit()
    print('* updated %s paper study_type' % (n_updates))

    return papers


def set_paper_rct_id(paper_id, rct_id):
    '''
    Set the main rct_id for study
    '''
    paper = get_paper_by_id(paper_id)

    paper.meta['rct_id'] = rct_id
    flag_modified(paper, "meta")

    # automatic update the date_updated
    paper.date_updated = datetime.datetime.now()
    
    db.session.add(paper)
    db.session.commit()

    return True, paper


def set_paper_pmid(paper_id, pmid):
    '''
    Set the PMID (pid) for a paper
    '''
    paper = get_paper_by_id(paper_id)
    project_id = paper.project_id

    existed_papers = get_papers_by_pmids(project_id, [pmid])
    if existed_papers == []:
        # which means it is not exists
        pass
    else:
        # this pmid exists!!!
        return None, existed_papers[0]

    # need to check if this pmid exists    
    paper.pid = pmid
    paper.pid_type = 'PubMed MEDLINE'

    # automatic update the date_updated
    paper.date_updated = datetime.datetime.now()
    
    db.session.add(paper)
    db.session.commit()

    return True, paper


def add_paper_tag(paper_id, tag):
    '''
    Add a tag to a paper
    '''
    paper = get_paper_by_id(paper_id)
    
    # add tags key if not exist
    if 'tags' not in paper.meta:
        paper.meta['tags'] = []

    # add tag
    if tag not in paper.meta['tags']:
        paper.meta['tags'].append(tag)
        flag_modified(paper, 'meta')
        db.session.add(paper)
        db.session.commit()
    else:
        pass

    return True, paper


def toggle_paper_tag(paper_id, tag):
    '''
    Toggle a tag on a paper.
    '''
    paper = get_paper_by_id(paper_id)
    
    # add tags key if not exist
    if 'tags' not in paper.meta:
        paper.meta['tags'] = []

    # toggle tag
    if tag not in paper.meta['tags']:
        paper.meta['tags'].append(tag)
    else:
        paper.meta['tags'].remove(tag)

    flag_modified(paper, 'meta')
    db.session.add(paper)
    db.session.commit()
    
    return True, paper


def is_existed_paper(project_id, pid):
    '''Check if a pid exists

    By default check the pmid
    '''
    paper = Paper.query.filter(and_(
        Paper.project_id == project_id,
        Paper.pid == pid
    )).first()

    if paper is None:
        return False, None
    else:
        return True, paper


def create_paper(project_id, pid, 
    pid_type='pmid', title=None, abstract=None,
    pub_date=None, authors=None, journal=None, meta=None,
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
    
    # the meta will contain more information
    all_rct_ids = get_nct_number(abstract)
    rct_id = '' if len(all_rct_ids) == 0 else all_rct_ids[0]
    _meta = {
        'tags': [],
        'pdfs': [],
        'rct_id': rct_id,
        'all_rct_ids': all_rct_ids
    }
    if meta is None:
        pass
    else:
        # copy the data in the meta to overwrite the default one
        for k in meta:
            _meta[k] = meta[k]

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
        meta = _meta,
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
    

def update_paper_rct_result_by_keystr_and_seq_num(keystr, seq_num):
    '''
    Update the RCT detection result
    '''
    paper = get_paper_by_keystr_and_seq(keystr, seq_num)
    paper = _update_paper_rct_result(paper)

    return paper


def update_paper_rct_result(project_id, pid):
    '''Update the RCT detection result
    '''
    paper = get_paper(project_id, pid)
    paper = _update_paper_rct_result(paper)

    return paper


def _update_paper_rct_result(paper):
    '''The internal function of updating RCT result
    '''
    # TODO catch exception
    pred = pred_rct(paper.title, paper.abstract)
    paper.meta['pred'] = pred['pred']
    flag_modified(paper, "meta")
    
    # commit this
    db.session.add(paper)
    db.session.commit()

    return paper


def set_paper_is_deleted_by_keystr_and_seq_num(keystr, seq_num, is_deleted):
    '''
    Update the is_deleted
    '''
    paper = get_paper_by_keystr_and_seq(keystr, seq_num)

    if is_deleted:
        paper.is_deleted = IS_DELETED_YES
    else:
        paper.is_deleted = IS_DELETED_NO

    db.session.add(paper)
    db.session.commit()

    return paper


def create_paper_if_not_exist(project_id, pid, 
    pid_type=None, title=None, abstract=None,
    pub_date=None, authors=None, journal=None, meta=None,
    ss_st=None, ss_pr=None, ss_rs=None, ss_ex=None, seq_num=None):
    '''A wrapper function for create_paper and is_existed_paper
    '''
    is_existed, paper = is_existed_paper(project_id, pid)
    if is_existed:
        return is_existed, paper
    else:
        p = create_paper(project_id, pid, 
            pid_type=pid_type, title=title, abstract=abstract,
            pub_date=pub_date, authors=authors, journal=journal, meta=meta,
            ss_st=ss_st, ss_pr=ss_pr, ss_rs=ss_rs, ss_ex=ss_ex, seq_num=seq_num)
        return is_existed, p


def create_paper_if_not_exist_and_predict_rct(project_id, pid, 
    pid_type=None, title=None, abstract=None,
    pub_date=None, authors=None, journal=None, meta=None,
    ss_st=None, ss_pr=None, ss_rs=None, ss_ex=None, seq_num=None):
    '''A wrapper function for create_paper and is_existed_paper
    '''
    is_existed, paper = create_paper_if_not_exist(project_id, pid,
            pid_type=pid_type, title=title, abstract=abstract,
            pub_date=pub_date, authors=authors, journal=journal, meta=meta,
            ss_st=ss_st, ss_pr=ss_pr, ss_rs=ss_rs, ss_ex=ss_ex, seq_num=seq_num)

    if is_existed:
        # nothing to do for a existing paper
        return is_existed, paper
    else:
        # update the RCT for this paper by the internal function
        paper = _update_paper_rct_result(paper)
        return is_existed, paper


def get_paper(project_id, pid):
    paper = Paper.query.filter(and_(
        Paper.project_id == project_id,
        Paper.pid == pid
    )).first()

    return paper


def get_paper_by_project_id_and_pid(project_id, pid):
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
    '''
    Get a paper by the project_id and its seq_num
    '''
    paper = Paper.query.filter(and_(
        Paper.project_id == project_id,
        Paper.seq_num == seq_num
    )).first()

    return paper


def get_paper_by_keystr_and_seq(keystr, seq_num):
    '''
    Get a paper detail by the keystr and its seq_num
    '''
    project = get_project_by_keystr(keystr)
    if project is None:
        return None
    paper = get_paper_by_seq(project.project_id, seq_num)

    return paper


def get_papers(project_id):
    papers = Paper.query.filter(and_(
        Paper.project_id == project_id
    )).order_by(Paper.date_created.desc()).all()

    return papers


def get_papers_by_keystr(keystr):
    '''
    Get papers by the project keystr
    '''
    project = get_project_by_keystr(keystr)
    papers = Paper.query.filter(and_(
        Paper.project_id == project.project_id
    )).order_by(Paper.date_created.desc()).all()

    return papers


def get_papers_by_seq_nums(project_id, seq_nums):
    '''
    Get papers by the seq_num list
    '''
    papers = Paper.query.filter(and_(
        Paper.project_id == project_id,
        Paper.seq_num.in_(seq_nums)
    )).all()
    return papers


def get_papers_by_pmids(project_id, pmids):
    '''
    Get all the papers according to pmid list
    '''
    papers = Paper.query.filter(and_(
        Paper.project_id == project_id,
        Paper.pid.in_(pmids)
    )).all()
    return papers


def get_papers_by_stage(project_id, stage):
    '''Get all papers of specified stage
    '''
    print('* get_papers_by_stage [%s]' % stage)
    if stage == ss_state.SS_STAGE_ALL_OF_THEM:
        papers = Paper.query.filter(and_(
            Paper.project_id == project_id,
            Paper.is_deleted == IS_DELETED_NO
        )).order_by(Paper.date_updated.desc()).all()

    elif stage == ss_state.SS_STAGE_UNSCREENED:
        papers = Paper.query.filter(and_(
            Paper.project_id == project_id,
            # 2020-12-10 how the study is imported doesn't matter for unscreened
            # Paper.ss_st.in_([
            #     ss_state.SS_ST_AUTO_EMAIL,
            #     ss_state.SS_ST_AUTO_SEARCH,
            #     ss_state.SS_ST_AUTO_OTHER,
            #     ss_state.SS_ST_IMPORT_ENDNOTE_XML,
            #     ss_state.SS_ST_IMPORT_OVID_XML,
            #     ss_state.SS_ST_IMPORT_SIMPLE_CSV
            # ]),
            Paper.ss_pr == ss_state.SS_PR_NA,
            Paper.ss_rs == ss_state.SS_RS_NA,
            Paper.is_deleted == IS_DELETED_NO
        )).order_by(Paper.date_updated.desc()).all()

    elif stage == ss_state.SS_STAGE_DECIDED:
        papers = Paper.query.filter(and_(
            Paper.project_id == project_id,
            Paper.ss_rs != ss_state.SS_RS_NA,
            Paper.is_deleted == IS_DELETED_NO
        )).order_by(Paper.date_updated.desc()).all()

    elif stage == ss_state.SS_STATE_PASSED_TITLE_NOT_FULLTEXT:
        papers = Paper.query.filter(and_(
            Paper.project_id == project_id,
            Paper.ss_pr == ss_state.SS_PR_PASSED_TITLE,
            Paper.ss_rs == ss_state.SS_RS_NA,
            Paper.is_deleted == IS_DELETED_NO
        )).order_by(Paper.date_updated.desc()).all()

    elif stage == ss_state.SS_STAGE_INCLUDED_SR:
        papers = Paper.query.filter(and_(
            Paper.project_id == project_id,
            Paper.ss_rs.in_([
                ss_state.SS_RS_INCLUDED_ONLY_SR,
                ss_state.SS_RS_INCLUDED_SRMA
            ]),
            Paper.is_deleted == IS_DELETED_NO
        )).order_by(Paper.date_updated.desc()).all()

    elif stage == ss_state.SS_STAGE_INCLUDED_SRMA:
        papers = Paper.query.filter(and_(
            Paper.project_id == project_id,
            Paper.ss_rs == ss_state.SS_RS_INCLUDED_SRMA,
            Paper.is_deleted == IS_DELETED_NO
        )).order_by(Paper.date_updated.desc()).all()

    elif stage == ss_state.SS_STAGE_EXCLUDED_BY_TITLE_ABSTRACT:
        papers = Paper.query.filter(and_(
            Paper.project_id == project_id,
            Paper.ss_rs.in_([
                ss_state.SS_RS_EXCLUDED_TITLE,
                ss_state.SS_RS_EXCLUDED_ABSTRACT
            ]),
            Paper.is_deleted == IS_DELETED_NO
        )).order_by(Paper.date_updated.desc()).all()

    elif stage == ss_state.SS_STAGE_EXCLUDED_BY_TITLE:
        papers = Paper.query.filter(and_(
            Paper.project_id == project_id,
            Paper.ss_rs == ss_state.SS_RS_EXCLUDED_TITLE,
            Paper.is_deleted == IS_DELETED_NO
        )).order_by(Paper.date_updated.desc()).all()

    elif stage == ss_state.SS_STAGE_EXCLUDED_BY_ABSTRACT:
        papers = Paper.query.filter(and_(
            Paper.project_id == project_id,
            Paper.ss_rs == ss_state.SS_RS_EXCLUDED_ABSTRACT,
            Paper.is_deleted == IS_DELETED_NO
        )).order_by(Paper.date_updated.desc()).all()

    elif stage == ss_state.SS_STAGE_EXCLUDED_BY_FULLTEXT:
        papers = Paper.query.filter(and_(
            Paper.project_id == project_id,
            Paper.ss_rs == ss_state.SS_RS_EXCLUDED_FULLTEXT,
            Paper.is_deleted == IS_DELETED_NO
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
    '''
    Set the pr and rs state with more detail

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


def add_pdfs_to_paper(paper_id, pdf_metas):
    '''
    Add PDF meta to a paper
    '''
    paper = get_paper_by_id(paper_id)
    if paper is None:
        raise Exception('no such paper???')

    if 'pdfs' not in paper.meta:
        paper.meta['pdfs'] = []

    paper.meta['pdfs'] += pdf_metas
    flag_modified(paper, "meta")

    db.session.add(paper)
    db.session.commit()
    
    return paper


def remove_pdfs_from_paper(paper_id, pdf_metas):
    '''
    Remove PDF meta from a paper
    '''
    paper = get_paper_by_id(paper_id)
    if paper is None:
        raise Exception('no such paper???')

    file_ids_to_remove = [ f['file_id'] for f in pdf_metas ]
    new_pdf_metas = []
    for pdf_meta in paper.meta['pdfs']:
        if pdf_meta['file_id'] not in file_ids_to_remove:
            new_pdf_metas.append(pdf_meta)

    paper.meta['pdfs'] = new_pdf_metas
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
        count(case when ss_pr = 'na' and ss_rs = 'na' then paper_id else null end) as unscreened,
        count(case when ss_pr = 'na' and ss_rs = 'na' and json_contains_path(ss_ex->'$.label', 'one', '$.CKL') then paper_id else null end) as unscreened_ckl,

        count(case when ss_pr = 'p20' and ss_rs = 'na' then paper_id else null end) as passed_title_not_fulltext,
        count(case when ss_pr = 'p20' and ss_rs = 'na' and json_contains_path(ss_ex->'$.label', 'one', '$.CKL') then paper_id else null end) as passed_title_not_fulltext_ckl,
        
        count(case when ss_rs = 'e2' then paper_id else null end) as excluded_by_title,
        count(case when ss_rs = 'e2' and json_contains_path(ss_ex->'$.label', 'one', '$.CKL') then paper_id else null end) as excluded_by_title_ckl,

        count(case when ss_rs = 'e22' then paper_id else null end) as excluded_by_abstract,
        count(case when ss_rs = 'e22' and json_contains_path(ss_ex->'$.label', 'one', '$.CKL') then paper_id else null end) as excluded_by_abstract_ckl,

        count(case when ss_rs in ('e2', 'e22') then paper_id else null end) as excluded_by_title_abstract,
        count(case when ss_rs = 'e21' then paper_id else null end) as excluded_by_rct_classifier,

        count(case when ss_rs = 'e3' then paper_id else null end) as excluded_by_fulltext,
        count(case when ss_rs = 'e3' and json_contains_path(ss_ex->'$.label', 'one', '$.CKL') then paper_id else null end) as excluded_by_fulltext_ckl,

        count(case when ss_rs = 'f1' then paper_id else null end) as included_only_sr,

        count(case when ss_rs in ('f1', 'f3') then paper_id else null end) as included_sr,
        count(case when ss_rs in ('f1', 'f3') and json_contains_path(ss_ex->'$.label', 'one', '$.CKL') then paper_id else null end) as included_sr_ckl,

        count(case when ss_rs = 'f3' then paper_id else null end) as included_srma,
        count(case when ss_rs = 'f3' and json_contains_path(ss_ex->'$.label', 'one', '$.CKL') then paper_id else null end) as included_srma_ckl,

        count(case when ss_rs != 'na' then paper_id else null end) as decided,
        count(case when ss_rs != 'na' and json_contains_path(ss_ex->'$.label', 'one', '$.CKL') then paper_id else null end) as decided_ckl
    
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
        'excluded_by_title_ckl',

        'excluded_by_abstract',
        'excluded_by_abstract_ckl',

        'excluded_by_title_abstract',
        'excluded_by_rct_classifier',

        'excluded_by_fulltext',
        'excluded_by_fulltext_ckl',

        'included_only_sr',

        'included_sr',
        'included_sr_ckl',

        'included_srma',
        'included_srma_ckl',

        'decided',
        'decided_ckl'
    ]
    result = {}
    for attr in attrs:
        try:
            result[attr] = r[attr]
        except Exception as err:
            
            result[attr] = 0

    return result


def get_screener_stat_only_unscreened_by_project_id(project_id):
    '''Get the statistics of the project for the screener
    '''
    sql = """
    select project_id,
        count(*) as all_of_them,
        count(case when ss_pr = 'na' and ss_rs = 'na' then paper_id else null end) as unscreened,
        count(case when ss_pr = 'na' and ss_rs = 'na' and json_contains_path(ss_ex->'$.label', 'one', '$.CKL') then paper_id else null end) as unscreened_ckl
    
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
        'unscreened_ckl'
    ]
    result = {}
    for attr in attrs:
        try:
            result[attr] = r[attr]
        except Exception as err:
            
            result[attr] = 0

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


###############################################################################
# Data Source Related Functions
###############################################################################

def create_datasource(
    ds_type, title, content
):
    '''
    Create a new data source record in db
    '''
    # create a datasource
    datasource_id = str(uuid.uuid1())
    date_created = datetime.datetime.now()

    datasource = DataSource(
        datasource_id = datasource_id,
        ds_type = ds_type,
        title = title,
        content = content,
        date_created = date_created,
    )
    
    db.session.add(datasource)
    db.session.commit()

    return datasource


###############################################################################
# Extract Related Functions
###############################################################################

def create_extract(project_id, oc_type, abbr, meta, data):
    '''
    Create a new extract for a project

    Args:

    oc_type: nma, pma, itable
    '''
    # create the id
    extract_id = str(uuid.uuid1())
    date_created = datetime.datetime.now()
    date_updated = datetime.datetime.now()

    extract = Extract(
        extract_id = extract_id,
        project_id = project_id,
        oc_type = oc_type,
        abbr = abbr,
        meta = meta,
        data = data,
        date_created = date_created,
        date_updated = date_updated
    )

    db.session.add(extract)
    db.session.commit()

    return extract


def delete_extract(project_id, oc_type, abbr):
    '''
    Delete an extract
    '''
    extract = Extract.query.filter(and_(
        Extract.project_id == project_id,
        Extract.oc_type == oc_type,
        Extract.abbr == abbr
    )).first()

    db.session.delete(extract)
    db.session.commit()

    return True


def update_extract_meta(project_id, oc_type, abbr, meta):
    '''
    Update the existing extract meta only
    '''
    extract = Extract.query.filter(and_(
        Extract.project_id == project_id,
        Extract.abbr == abbr
    )).first()

    # TODO check if not exists

    # update
    extract.meta = meta
    extract.date_updated = datetime.datetime.now()

    flag_modified(extract, "meta")

    # commit this
    db.session.add(extract)
    db.session.commit()

    return extract


def update_extract_meta_and_data(project_id, oc_type, abbr, meta, data):
    '''
    Update the existing extract
    '''
    extract = Extract.query.filter(and_(
        Extract.project_id == project_id,
        Extract.abbr == abbr
    )).first()

    # TODO check if not exists

    # update
    extract.meta = meta
    extract.data = data
    extract.date_updated = datetime.datetime.now()

    flag_modified(extract, "meta")
    flag_modified(extract, "data")

    # commit this
    db.session.add(extract)
    db.session.commit()

    return extract
    

def get_extracts_by_project_id(project_id):
    '''
    Get all of the extract detail of a project
    '''
    extracts = Extract.query.filter(
        Extract.project_id == project_id
    ).all()

    return extracts


def get_extract_by_project_id_and_abbr(project_id, abbr):
    '''
    Get an extract
    '''
    extract = Extract.query.filter(and_(
        Extract.project_id == project_id,
        Extract.abbr == abbr
    )).first()

    return extract


def get_extract_by_keystr_and_abbr(keystr, abbr):
    '''
    Get an extract by keystr and abbr
    '''
    project = get_project_by_keystr(keystr)

    if project is None:
        # what???
        return None

    extract = Extract.query.filter(and_(
        Extract.project_id == project.project_id,
        Extract.abbr == abbr
    )).first()

    return extract


def delete_all_extracts_by_keystr(keystr):
    '''
    Delete all extract by a given project keystr
    '''
    project = get_project_by_keystr(keystr)

    if project is None:
        # what???
        return None

    project_id = project.project_id

    # first, delete those extracts under this project
    Extract.query.filter_by(
        project_id=project_id
    ).delete()

    # commit
    db.session.commit()

    return True