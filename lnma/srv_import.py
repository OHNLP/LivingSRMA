import os
import time

from tqdm import tqdm 

from lnma import settings, srv_project
from lnma import util
from lnma import dora
from lnma import ss_state


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