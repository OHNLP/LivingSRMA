import time

from tqdm import tqdm 

from lnma import util
from lnma import dora
from lnma import ss_state


def set_paper_pred(keystr, pid, model_id, rs):
    '''
    Set the paper prediction
    '''
    paper = dora.get_paper_by_keystr_and_pid(
        keystr, pid
    )

    # hmmm ... why?
    if paper is None:
        return False, None

    # set the 

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
    

if __name__ == '__main__':
    # for debug purpose
    from lnma import db, create_app
    app = create_app()
    db.init_app(app)
    app.app_context().push()

    update_all_srma_paper_pub_date('IO')