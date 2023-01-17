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


def get_duplicated_papers(keystr):
    '''
    Get duplicated papers
    '''
    papers = dora.get_papers_by_keystr(keystr)
    print('* got %s papers for project [%s]' % (
        len(papers), keystr
    ))

    all_dups = {}
    dup_pids = []
    # for saving duplicates
    for p1_idx, p1 in enumerate(tqdm(papers)):
        p1_dups = [p1]

        if p1.pid in dup_pids:
            # this paper has been check and duplicated with any
            continue

        # check all other papers
        for p2 in papers[p1_idx+1:]:
            is_dup = is_paper_duplicated(p1, p2)
            if is_dup:
                p1_dups.append(p2)
                dup_pids.append(p2.pid)
            else:
                pass

        if len(p1_dups) == 1:
            # which means no dups found for this p1
            pass
        else:
            all_dups[p1.pid] = p1_dups
    
    print('* found %s papers have duplicates' % (
        len(all_dups)
    ))

    return all_dups

def is_paper_duplicated(p1, p2):
    '''
    Judge whether p1 and p2 are duplicated
    '''
    t1 = p1.title.lower()
    t2 = p2.title.lower()

    if t1 == t2:
        return True


    return False


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
        Paper.ss_ex['ss_cq'][cq_abbr]['d'] == settings.PAPER_SS_EX_SS_CQ_DECISION_YES
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


def set_paper_ss_st(paper_id, ss_st):
    '''
    Set the paper ss_st to a given value
    '''
    paper = dora.get_paper_by_id(paper_id)
    paper.ss_st = ss_st
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

    if ss_cq == settings.PAPER_SS_EX_SS_CQ_DECISION_YES:
        paper.ss_ex['ss_cq'][cq_abbr] = util.make_ss_cq_decision(
            settings.PAPER_SS_EX_SS_CQ_DECISION_YES,
            ss_cq_ex_reason,
            c
        )
    else:
        paper.ss_ex['ss_cq'][cq_abbr] = util.make_ss_cq_decision(
            settings.PAPER_SS_EX_SS_CQ_DECISION_NO,
            ss_cq_ex_reason,
            c
        )

    flag_modified(paper, 'ss_ex')
    db.session.add(paper)
    db.session.commit()

    return True, paper


def set_paper_ss_cq_ds(paper_id, cqs):
    '''
    Set the ss_cq data structure to a given paper
    '''
    paper = dora.get_paper_by_id(paper_id)

    # 2022-02-04: update the cq for this
    is_changed, reason = paper.update_ss_cq_ds(
        cqs,
    )
    if is_changed:
        flag_modified(paper, "ss_ex")

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
    

def set_paper_ss_decision(
    project, 
    cq_abbr, 
    pid, 
    ss_pr, 
    ss_rs, 
    reason, 
    stage
):
    '''
    Set paper screening decision

    The input parameters must be decided in advance
    '''
    paper = dora.get_paper_by_keystr_and_pid(
        project.keystr, pid
    )

    # what??? 
    if paper is None:
        return False, None

    # create a dict for the details
    detail_dict = util.get_decision_detail_dict(
        reason, 
        stage
    )

    if ss_rs == ss_state.SS_RS_INCLUDED_ONLY_SR:
        # the situation is complex, need to check the cq
        if 'ss_cq' in paper.ss_ex:
            # may need to update a cq
            paper.ss_ex['ss_cq'][cq_abbr] = util.make_ss_cq_decision(
                settings.PAPER_SS_EX_SS_CQ_DECISION_YES,
                reason,
                settings.PAPER_SS_EX_SS_CQ_CONFIRMED_YES
            )
        
        else:
            # ok, it's a new one, create all 
            paper.ss_ex['ss_cq'] = util.make_ss_cq_dict(
                project
            )

            # and then update this cq
            paper.ss_ex['ss_cq'][cq_abbr] = util.make_ss_cq_decision(
                settings.PAPER_SS_EX_SS_CQ_DECISION_YES,
                reason,
                settings.PAPER_SS_EX_SS_CQ_CONFIRMED_YES
        )

        # append the detail_dict
        for key in detail_dict:
            paper.ss_ex[key] = detail_dict[key]

    # update the ss for this paper
    p = dora.set_paper_pr_rs_with_details(
        paper.paper_id, 
        pr=ss_pr,
        rs=ss_rs,
        detail_dict=paper.ss_ex
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


def check_existed_paper_by_file(keystr, data_type, full_path):
    '''
    Check existed papers by a given file
    '''
    # has this project?
    project = dora.get_project_by_keystr(keystr)

    if project is None:
        print('* no such project %s' % keystr)
        return

    # read the content from that file
    raw_text = open(full_path, encoding='utf-8').read()

    if data_type == 'ovid':
        # remove illegal chars in the text, usually the \x00 or others
        xml_text = util.escape_illegal_xml_characters(raw_text)

        # get the json papers
        jsonpapers = util.parse_ovid_exported_xml_text(xml_text)

        # check
        ret = check_existed_paper_by_jsonpapers(
            project.project_id, 
            jsonpapers
        )

    else:
        ret = None

    return ret


def check_existed_paper_by_jsonpapers(project_id, jsonpapers):
    '''
    Check existed papers by a given json papers
    '''
    ret = {
        "cnt": {
            'total': len(jsonpapers),
            'existed': 0,
            'new': 0
        },
        "papers": {
            'existed': [],
            'new': []
        }
    }

    # check each one
    for p in tqdm(jsonpapers):
        pid = p['pid']
        title = p['title']

        # check this paper in database
        is_existed, paper = dora.is_existed_paper(
            project_id,
            pid,
            title
        )

        if is_existed:
            ret['cnt']['existed'] += 1
            _p = {
                'result': 'existed',
                'seq': paper.seq_num,
                'p': p,
            }
            ret['papers']['existed'].append(_p)
        else:
            ret['cnt']['new'] += 1
            _p = {
                'result': 'new',
                'seq': 0,
                'p': p,
            }
            ret['papers']['new'].append(_p)

    return ret


def save_paper_by_file(keystr, data_type, full_path):
    '''
    Save papers by a given file
    '''
    # has this project?
    project = dora.get_project_by_keystr(keystr)

    if project is None:
        print('* no such project %s' % keystr)
        return

    # read the content from that file
    raw_text = open(full_path, encoding='utf-8').read()

    if data_type == 'ovid':
        # remove illegal chars in the text, usually the \x00 or others
        xml_text = util.escape_illegal_xml_characters(raw_text)

        # get the json papers
        jsonpapers = util.parse_ovid_exported_xml_text(xml_text)

        # check
        ret = save_paper_by_jsonpapers(
            project.project_id, 
            jsonpapers
        )

    else:
        ret = None

    return ret


def save_paper_by_jsonpapers(project_id, jsonpapers, stage=ss_state.SS_STAGE_UNSCREENED):
    '''
    Save paper object by a JSON object parsed by OVID
    '''
    # get the screening stage information
    # convert stage to pr and rs
    ss_pr, ss_rs = ss_state.SS_STAGE_TO_PR_AND_RS[stage]
    ss_ex = util.create_pr_rs_details('User specified', stage)

    # for the results
    ret = {
        "success": True,
        "cnt": {
            'total': len(jsonpapers),
            'existed': 0,
            'created': 0,
        },
        "papers": {
            'existed': [],
            'created': []
        }
    }

    for p in jsonpapers:
        # create the `meta` object for a paper
        # meta
        meta = {}
        if 'raw_type' in p:
            if p['raw_type'] in ['pubmed_xml', 'endnote_xml', 'ovid_xml']:
                meta['raw_type'] = p['raw_type']
                meta['xml'] = p['xml']
        else:
            meta['raw_type'] = None

        # add the DOI when uploading a new study
        if 'doi' in p:
            meta['doi'] = p['doi']
        else:
            meta['doi'] = ''
        # create
        try:
            is_exist, paper = dora.create_paper_if_not_exist_and_predict_rct(
                project_id, 
                p['pid'], 
                p['pid_type'],
                p['title'],
                p['abstract'],
                util.check_paper_pub_date(p['pub_date']),
                util.check_paper_authors(p['authors']),
                util.check_paper_journal(p['journal']),
                meta,
                ss_state.SS_ST_IMPORT_ENDNOTE_XML,
                ss_pr,
                ss_rs,
                ss_ex,
                None,
                False
            )
        except Exception as err:
            # give some feedback to frontend
            ret['papers'].append({
                'result': 'error',
                'success': False,
                'seq': p['seq']
            })
            continue
        
        # save the result
        _p = {
            'result': '',
            'success': None,
            'seq': p['seq']
        }
        if is_exist:
            ret['cnt']['existed'] += 1
            _p = {
                'result': 'existed',
                'success': False,
                'seq': paper.seq_num
            }
            ret['papers']['existed'].append(_p)
        else:
            ret['cnt']['created'] += 1
            _p = {
                'result': 'created',
                'success': False,
                'seq': p['seq']
            }
            ret['papers']['created'].append(_p)

    return ret

    
# if __name__ == '__main__':
#     # for debug purpose
#     from lnma import db, create_app
#     app = create_app()
#     db.init_app(app)
#     app.app_context().push()

#     update_all_srma_paper_pub_date('IO')