import time
import datetime
from numpy.lib.function_base import delete

from sqlalchemy import and_, or_, not_
from sqlalchemy.orm.attributes import flag_modified

from tqdm import tqdm

from flask_login import current_user

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
    else:
        paper.ss_ex['label'][label]['user'] = {
            'uid': current_user.uid,
            'abbr': current_user.get_abbr()
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
        Paper.ss_ex['ss_cq'][cq_abbr]['d'] == settings.PAPER_SS_EX_SS_CQ_YES
    )).order_by(Paper.date_updated.desc()).all()

    return papers


def set_paper_label_dis(paper_id, dis, cq_abbr=''):
    '''
    Set the DIS label for paper
    '''

    if cq_abbr is None or cq_abbr == '':
        # which means just set project level
        if dis == 'yes':
            paper = set_paper_ss_label(paper_id, 'DIS')
        else:
            paper = unset_paper_ss_label(paper_id, 'DIS')

        return True, paper

    else:
        paper = dora.get_paper_by_id(paper_id)
        
        paper.ss_ex['ss_cq'][cq_abbr]['c'] = dis

        flag_modified(paper, 'ss_ex')
        db.session.add(paper)
        db.session.commit()

        return True, paper


def set_paper_label_rfc(paper_id, rfc, cq_abbr=''):
    '''
    Set the RFC label for 
    '''

    if cq_abbr is None or cq_abbr == '':
        # which means just set project level
        if rfc == 'yes':
            paper = set_paper_ss_label(paper_id, 'RFC')
        else:
            paper = unset_paper_ss_label(paper_id, 'RFC')

        return True, paper

    else:
        paper = dora.get_paper_by_id(paper_id)
        
        paper.ss_ex['ss_cq'][cq_abbr]['c'] = rfc

        flag_modified(paper, 'ss_ex')
        db.session.add(paper)
        db.session.commit()

        return True, paper


def set_paper_ss_cq(paper_id, cq_abbr, ss_cq, ss_cq_ex_reason=''):
    '''
    Set the ss_cq for a paper
    '''
    paper = dora.get_paper_by_id(paper_id)

    if paper is None:
        return False, None

    if 'ss_cq' not in paper.ss_ex:
        paper.ss_ex['ss_cq'] = {}

    if cq_abbr in paper.ss_ex['ss_cq']:
        c = paper.ss_ex['ss_cq'][cq_abbr]['c']
    else:
        c = 'no'

    if ss_cq == settings.PAPER_SS_EX_SS_CQ_YES:
        paper.ss_ex['ss_cq'][cq_abbr] = util.make_ss_cq_decision(
            settings.PAPER_SS_EX_SS_CQ_YES,
            ss_cq_ex_reason,
            c
        )
    else:
        paper.ss_ex['ss_cq'][cq_abbr] = util.make_ss_cq_decision(
            settings.PAPER_SS_EX_SS_CQ_NO,
            ss_cq_ex_reason,
            c
        )

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
    

def check_usage_in_extracts(keystr, seq_num):
    '''
    Check the usage of a paper in extractions
    '''
    paper = dora.get_paper_by_keystr_and_seq(keystr, seq_num)

    if paper is None:
        return None

    # get the pid for later use
    pid = paper.pid

    # ok, need to check if this paper exists in extraction
    extracts = dora.get_extracts_by_keystr(keystr)

    has_used_in_extracts = []

    for ext in extracts:
        if pid in ext.data:
            has_used_in_extracts.append(ext)
        else:
            pass

    if len(has_used_in_extracts)>0:
        print('* found %s#%s used in %s extracts' % (
            keystr, seq_num, len(has_used_in_extracts)
        ))
        for ext in has_used_in_extracts:
            print('* - %s in %s|%s|%s - %s|%s' % (
                ext.data[pid]['is_selected'],
                ext.meta['cq_abbr'],
                ext.meta['oc_type'],
                ext.meta['group'],
                ext.meta['category'],
                ext.meta['full_name'],
            ))

    return has_used_in_extracts


def delete_paper_from_db_by_seq_num(keystr, seq_num, is_stop_when_used=True):
    '''
    Delete a paper from DB
    '''
    project = dora.get_project_by_keystr(keystr)

    if project is None:
        return False

    paper = dora.get_paper_by_keystr_and_seq(keystr, seq_num)

    if paper is None:
        return False
    
    # get the pid for later use
    pid = paper.pid

    # ok, need to check if this paper exists in extraction
    extracts = dora.get_extracts_by_keystr(keystr)

    has_used_in_extracts = []

    for ext in extracts:
        if pid in ext.data:
            has_used_in_extracts.append(ext)
        else:
            pass

    if len(has_used_in_extracts)>0:
        print('* found %s#%s used in %s extracts' % (
            keystr, seq_num, len(has_used_in_extracts)
        ))
        for ext in has_used_in_extracts:
            print('* - %s in %s|%s|%s - %s|%s' % (
                ext.data[pid]['is_selected'],
                ext.meta['cq_abbr'],
                ext.meta['oc_type'],
                ext.meta['group'],
                ext.meta['category'],
                ext.meta['full_name'],
            ))
        if is_stop_when_used:
            return False

    # checked, delete this paper
    ret = dora.delete_paper(paper.paper_id)

    return ret


# if __name__ == '__main__':
#     # for debug purpose
#     from lnma import db, create_app
#     app = create_app()
#     db.init_app(app)
#     app.app_context().push()

#     update_all_srma_paper_pub_date('IO')