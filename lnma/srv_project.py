import time
import datetime

from tqdm import tqdm 

from sqlalchemy import and_, or_, not_
from sqlalchemy.orm.attributes import flag_modified

from lnma import settings
from lnma import util
from lnma import dora
from lnma import ss_state

from . import db


def get_project_latest_stat_by_keystr(keystr):
    '''
    Get the latest statistics for a project by the keystr
    '''
    project = dora.get_project_by_keystr(keystr)

    if project is None:
        return None

    result = get_project_latest_stat(project.project_id)

    return result


def get_project_latest_stat(project_id):
    '''
    Get the latest statistics for a project
    '''
    sql = """
    select max(date_created) as last_created,
        max(date_updated) as last_updated
    from papers
    where project_id = '{project_id}'
    """.format(project_id = project_id)

    r = db.session.execute(sql).fetchone()

    print(r)

    if r is not None:
        result = {
            'last_created': r['last_created'].strftime('%Y-%m-%d'),
            'last_updated': r['last_updated'].strftime('%Y-%m-%d')
        }
    else:
        # Hmmm ... I don't think this would happen
        # 
        # 2021-05-12
        # Sorry, it happens
        result = None

    return result


def update_project_last_update_by_keystr(keystr):
    '''
    Update the project last_update by the keystr
    '''
    project = dora.get_project_by_keystr(keystr)

    if project is None:
        return None

    project.date_updated = datetime.datetime.now()

    db.session.add(project)
    db.session.commit()

    return project


def update_project_papers_ss_cq_by_keystr(keystr, decision):
    '''
    Update the ss_cq for all papers in this project

    Set the paper data model `ss_ex` to support cq-based data.
    ALL ss_rs==f1,f2,f3 papers are affected.
    '''
    project = dora.get_project_by_keystr(keystr)
    papers = dora.get_papers_by_keystr(keystr)

    print('* found %d papers for [%s] in current database' % (
        len(papers), keystr
    ))

    cnt = {
        'total': 0
    }

    for paper in tqdm(papers):
        if paper.is_ss_included_in_project():
            paper.update_ss_cq_by_cqs(
                project.settings['clinical_questions'],
                decision
            )

            flag_modified(paper, "ss_ex")
            cnt['total'] += 1

            db.session.add(paper)
            db.session.commit()

    print('* found and upgraded %s studies for the ss_cq' % (
        cnt['total']
    ))

    return project