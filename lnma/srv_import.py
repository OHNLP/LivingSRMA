import os
import time

from tqdm import tqdm 

from lnma import settings, srv_project
from lnma import util
from lnma import dora
from lnma import ss_state
from lnma import db


def import_ris(full_fn, keystr):
    '''
    Import the given RIS format record
    '''
    project = dora.get_project_by_keystr(keystr)

    # check the project 
    if project is None:
        print('* Not found project [%s]' % keystr)
        return False, None

    # check the file
    if not os.path.exists(full_fn):
        print('* Not found input file [%s]' % full_fn)
        return False, None

    print('* parsing the input ris file ...')
    papers, _ = util.parse_exported_ris(full_fn)
    if papers is None:
        print('* Not supported file format [%s]' % full_fn)
        return False, None

    # now create the paper in db
    cnt = {
        'total': len(papers),
        'existed': 0,
        'created': 0,
    }
    print('* importing the %s studies' % (
        len(papers)
    ))
    for p in tqdm(papers):
        is_exist, paper = dora.create_paper_if_not_exist_and_predict_rct(
            project.project_id, 
            p['pid'], 
            p['pid_type'],
            p['title'],
            p['abstract'],
            util.check_paper_pub_date(p['pub_date']),
            p['authors'],
            util.check_paper_journal(p['journal']),
            None,
            ss_state.SS_ST_IMPORT_MANUAL,
            ss_state.SS_PR_NA,
            ss_state.SS_RS_NA,
            None,
            None,
        )
        if is_exist:
            cnt['existed'] += 1
        else:
            cnt['created'] += 1
    
    print('* imported %s(c%s+e%s) papers' % (
        cnt['total'],
        cnt['created'],
        cnt['existed'],
    ))

    # update the timestamp
    _ = srv_project.update_project_last_update_by_keystr(keystr)

    return True, papers


def import_endnote_xml(full_fn, keystr):
    '''
    Import the given Endnote exported XML file to a project
    '''
    project = dora.get_project_by_keystr(keystr)

    if project is None:
        print('* Not found project [%s]' % keystr)
        return False, None

    if not os.path.exists(full_fn):
        print('* Not found input file [%s]' % full_fn)
        return False, None

    print('* parsing the input xml file ...')
    papers, _ = util.parse_endnote_exported_xml(full_fn)
    if papers is None:
        print('* Not supported file format [%s]' % full_fn)
        return False, None

    # now create the paper in db
    cnt = {
        'total': len(papers),
        'existed': 0,
        'created': 0,
    }
    print('* importing the %s studies' % (
        len(papers)
    ))
    for p in tqdm(papers):
        is_exist, paper = dora.create_paper_if_not_exist_and_predict_rct(
            project.project_id, 
            p['pid'], 
            p['pid_type'],
            p['title'],
            p['abstract'],
            util.check_paper_pub_date(p['pub_date']),
            p['authors'],
            util.check_paper_journal(p['journal']),
            None,
            ss_state.SS_ST_IMPORT_ENDNOTE_XML,
            ss_state.SS_PR_NA,
            ss_state.SS_RS_NA,
            None,
            None,
        )
        if is_exist:
            cnt['existed'] += 1
        else:
            cnt['created'] += 1
    
    print('* imported %s(c%s+e%s) papers' % (
        cnt['total'],
        cnt['created'],
        cnt['existed'],
    ))

    # update the timestamp
    _ = srv_project.update_project_last_update_by_keystr(keystr)

    return True, papers


def import_by_pmid(keystr, pmid, rct_id=None):
    '''
    Import a study by its pmid
    '''
    project = dora.get_project_by_keystr(keystr)

    if project is None:
        return False, None
    
    # try to search this pmid
    data = util.e_fetch([pmid])

    if pmid not in data['result']:
        # not found this pmid
        # just skip not matter what next
        return False, None

    # ok, since this information is correct
    # we could try to update the data
    paper = dora.get_paper_by_project_id_and_pid(
        project.project_id, pmid
    )

    if paper is None:
        # this is a new paper
        meta_rct = None if rct_id is None else { 'rct_id': rct_id }
        paper = dora.create_paper(
            project.project_id, pmid, 'PMID', 
            '', '', '', '', '', 
            meta_rct, # meta
            ss_state.SS_ST_IMPORT_SIMPLE_CSV,
            None, None, None, 
            None, # seq_num
        )
    else:
        # this is not a new paper
        pass

    # update the paper information
    paper.from_pubmed_record(data['result'][pmid])

    # update the prediction
    paper = dora.update_paper_rct_result(paper)

    db.session.add(paper)
    db.session.commit()

    return True, paper