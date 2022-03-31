import time
import datetime

from tqdm import tqdm 

from sqlalchemy import and_, or_, not_
from sqlalchemy.orm.attributes import flag_modified

from lnma import settings
from lnma import util
from lnma import dora
from lnma import ss_state
from lnma.models import *

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
            'last_updated': r['last_updated'].strftime('%Y-%m-%d'),
            'last_queried': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    else:
        # Hmmm ... I don't think this would happen
        # 
        # 2021-05-12
        # Sorry, it happens
        result = None

    return result


def get_project_timeline_by_keystr(keystr):
    '''
    Get the timeline of the given project
    '''
    # project = dora.get_project_by_keystr(keystr)
    papers = dora.get_papers_by_keystr(keystr)

    # timeline is a date-based dictionary for sorting events
    # by looping on each paper in a project
    # to generate a statistics on the paper process.
    # It looks like:
    #
    # {
    #    date: {
    #        category: {
    #            event: {
    #                pids: int, # which paper related to this event
    #            }
    #        }
    #    }, ...     
    # }
    # 
    # According to the event define, one paper may show in 
    # several events (create, update, and decision, etc)
    timeline = {}

    for paper in tqdm(papers):
        # get the pid of this paper for shortcut
        pid = paper.pid

        # get all dates related to this paper
        # date_updated = paper.get_date_updated_in_date()
        date_created = paper.get_date_created_in_date()
        date_decided = paper.ss_ex['date_decided'] if 'date_decided' in paper.ss_ex else None

        # add this date and default category
        # dates = [date_created, date_updated]
        dates = [date_created]
        if date_decided is not None:
            dates.append(date_decided)

        for _d in dates:
            if _d not in timeline:
                timeline[_d] = {
                    'created': {},
                    'decision': {}
                }

        # add event of this paper
        # event, import
        if paper.ss_st not in timeline[date_created]['created']:
            timeline[date_created]['created'][paper.ss_st] = []
        timeline[date_created]['created'][paper.ss_st].append(pid)

        # event, decision
        if date_decided is not None and paper.ss_rs != ss_state.SS_RS_NA:
            if paper.ss_rs not in timeline[date_decided]['decision']:
                timeline[date_decided]['decision'][paper.ss_rs] = []
            timeline[date_decided]['decision'][paper.ss_rs].append(pid)

    return timeline


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
        'n_changed': 0,
        'n_all': 0
    }

    for paper in tqdm(papers):
        if paper.is_ss_included_in_project():
            # ok, this paper is select
            is_changed, reason = paper.update_ss_cq_ds(
                project.settings['clinical_questions'],
            )
            if is_changed:
                flag_modified(paper, "ss_ex")
                cnt['n_changed'] += 1

                db.session.add(paper)
                db.session.commit()
            else:
                # ok, since we didn't change anything, no need to update
                pass
            
            cnt['n_all'] += 1

    print('* found %s and upgraded %s studies for the ss_cq' % (
        cnt['n_all'],
        cnt['n_changed']
    ))

    return project


def delete_all_extracts_by_keystr(keystr, cq_abbr='default', oc_type='all'):
    '''
    Delete all extract by a given project keystr
    '''
    project = dora.get_project_by_keystr(keystr)

    if project is None:
        # what???
        return None

    project_id = project.project_id

    # first, delete those extracts under this project
    if oc_type == 'all':
        # Extract.query.filter(and_(
        #     Extract.project_id == project_id,
        #     Extract.meta['cq_abbr'] == cq_abbr
        # )).delete()

        Extract.query.filter(
            Extract.project_id == project_id,
            Extract.meta['cq_abbr'] == cq_abbr
        ).delete(synchronize_session=False)

    else:
        # Extract.query.filter(and_(
        #     Extract.project_id == project.project_id,
        #     Extract.oc_type == oc_type,
        #     Extract.meta['cq_abbr'] == cq_abbr
        # )).delete()
        Extract.query.filter(
            Extract.project_id == project_id,
            Extract.meta['cq_abbr'] == cq_abbr,
            Extract.oc_type == oc_type
        ).delete(synchronize_session=False)

    # commit
    db.session.commit()

    return True


def set_project_title_by_keystr(keystr, title):
    '''
    Set the title for a given project
    '''
    project = dora.get_project_by_keystr(keystr)
    return set_project_title(
        project.project_id,
        title
    )


def set_project_title(project_id, title):
    '''
    Set the title for a given project
    '''
    project = dora.get_project(project_id)
    if project is None:
        return False, None

    project.title = title

    db.session.add(project)
    db.session.commit()

    return True, project


def set_project_keystr(project_id, keystr):
    '''
    Set the keystr
    '''
    project = dora.get_project(project_id)
    if project is None:
        return False, None

    project.keystr = keystr

    db.session.add(project)
    db.session.commit()

    return True, project


def set_project_keystr_by_keystr(keystr, new_keystr):
    '''
    Set the new_keystr for a given project
    '''
    project = dora.get_project_by_keystr(keystr)
    return set_project_keystr(
        project.project_id,
        new_keystr
    )


def delete_all_papers_by_keystr(keystr):
    '''
    Delete all papers in a project
    '''
    project = dora.get_project_by_keystr(keystr)

    if project is None:
        # what???
        return None

    project_id = project.project_id

    # first, delete those paper under this project
    Paper.query.filter_by(
        project_id=project_id
    ).delete()

    # commit
    db.session.commit()

    return True