import os
import pandas as pd

from flask import current_app

from lnma import dora
from lnma import util
from lnma import ss_state
from lnma import settings
from lnma import db

'''
Services of PRISMA for publication site
'''

def get_prisma_by_cq(project_id, cq_abbr="default", do_include_papers=False):
    '''
    Get the PRISMA numbers from database
    '''
    project = dora.get_project(project_id)
    # project_id = project.project_id

    # get the living prisma from database
    stat = get_stat_aef(project_id)

    # get the paper information from database
    # the paper dict is PMID based
    paper_dict = {}

    # the study dict is NCT based
    study_dict = {}

    # update the e3 reasons
    papers = dora.get_papers_by_stage(
        project_id, 
        ss_state.SS_STAGE_EXCLUDED_BY_FULLTEXT
    )
    stat['e3_by_reason'] = {}
    for paper in papers:
        reason = paper.ss_ex['reason']
        if reason not in stat['e3_by_reason']:
            stat['e3_by_reason'][reason] = {
                'count': 0
            }
        stat['e3_by_reason'][reason]['count'] += 1

    # update the f1 decisions
    papers = dora.get_papers_by_stage(
        project_id,
        ss_state.SS_STAGE_INCLUDED_SR
    )
    # using this to check whether a study is used in MA
    f1_pids = []
    for paper in papers:
        rct_id = paper.get_rct_id()

        # decide the cq level decision
        if paper.ss_ex['ss_cq'][cq_abbr]['d'] == 'yes':
            # nothing 
            stat['f1']['pids'].append(paper.pid)
            f1_pids.append(paper.pid)
        else:
            # this study is not included in this cq
            stat['f1']['count'] -= 1
            stat['e3']['count'] += 1

            # update the reason
            reason = paper.ss_ex['ss_cq'][cq_abbr]['r']
            if reason in stat['e3_by_reason']:
                stat['e3_by_reason'][reason]['count'] += 1
            else:
                # this reason is NOT in existing reasons
                if ss_state.SS_REASON_OTHER not in stat['e3_by_reason']:
                    stat['e3_by_reason'][ss_state.SS_REASON_OTHER] = {
                        'count': 0
                    }
                stat['e3_by_reason'][ss_state.SS_REASON_OTHER]['count'] += 1

        # add this paper to the paper dict
        if do_include_papers:
            paper_dict[paper.pid] = {
                "authors": paper.authors,
                "ctid": rct_id,
                "date": paper.pub_date,
                "journal": paper.journal,
                "pid": paper.pid,
                "pid_type": paper.pid_type,
                "title": paper.title,
            }

            # add this RCT to the study dict
            if rct_id not in study_dict:
                study_dict[rct_id] = {
                    "authors": paper.authors,
                    "ctid": rct_id,
                    "date": paper.pub_date,
                    "journal": paper.journal,
                    "pid": paper.pid,
                    "title": paper.title,

                    # the followings are for RCT
                    "study_id": rct_id,
                    "latest_pid": '',
                    "pids": [],
                }
        
            # then add this paper to the study list
            study_dict[rct_id]['latest_pid'] = paper.pid
            study_dict[rct_id]['pids'].append(paper.pid)

    # update the f3 decisions
    ocs = dora.get_extracts_by_keystr_and_cq(
        project.keystr,
        cq_abbr
    )
    # check each outcome
    for oc in ocs:
        # check papaer extracted in this outcome
        for pid in oc.data:
            p = oc.data[pid]

            if p['is_selected']:
                if pid in stat['f3']['pids']:
                    # this pid has been counted
                    pass
                else:
                    stat['f3']['count'] += 1
                    stat['f3']['pids'].append(pid)
            else:
                # this paper is extracted but not selected yet.
                pass

    # finally, we present this object
    ret = {
        "stat": stat,
        "paper_dict": paper_dict,
        "study_dict": study_dict,
    }

    return ret


def get_prisma_from_db(prj, cq_abbr="default"):
    '''
    Get PRISMA JSON data from database
    '''
    project = dora.get_project_by_keystr(prj)
    project_id = project.project_id

    # get the fixed number from project settings
    # this depends on whether this project 
    past_prisma = {}

    # get the living prisma from database
    prisma, stat = get_prisma_bef(project_id)

    # get the paper information from database
    # the paper dict is PMID based
    paper_dict = {}

    # the study dict is NCT based
    study_dict = {}

    # fill the pmid
    papers = dora.get_papers_by_stage(
        project.project_id,
        ss_state.SS_STAGE_INCLUDED_SR
    )
    for paper in papers:
        rct_id = paper.get_rct_id()

        # add this paper to the paper dict
        paper_dict[paper.pid] = {
            "authors": paper.authors,
            "ctid": rct_id,
            "date": paper.pub_date,
            "journal": paper.journal,
            "pmid": paper.pid,
            "pid_type": paper.pid_type,
            "title": paper.title,
        }

        # add this RCT to the study dict
        if rct_id not in study_dict:
            study_dict[rct_id] = {
                "authors": paper.authors,
                "ctid": rct_id,
                "date": paper.pub_date,
                "journal": paper.journal,
                "pmid": paper.pid,
                "title": paper.title,

                # the followings are for RCT
                "study_id": rct_id,
                "latest_pmid": '',
                "pmids": [],
            }
        
        # then add this paper to the study list
        study_dict[rct_id]['latest_pmid'] = paper.pid
        study_dict[rct_id]['pmids'].append(paper.pid)

    # finally, we present this object
    ret = {
        "prisma": prisma,
        "stat": stat,
        "paper_dict": paper_dict,
        "study_dict": study_dict,
    }

    return ret


def get_prisma_from_xls(prj):
    '''
    Get PRISMA JSON data from Excel file
    '''
    import numpy as np

    fn = 'PRISMA_DATA.xlsx'
    full_fn = os.path.join(current_app.instance_path, settings.PUBLIC_PATH_PUBDATA, prj, fn)

    # hold all the outcomes
    fn_json = 'PRISMA.json'
    full_fn_json = os.path.join(current_app.instance_path, settings.PUBLIC_PATH_PUBDATA, prj, fn_json)
    
    # there are two tables for this 
    tab_name_prisma = 'PRISMA'
    tab_name_studies = 'studies'

    # load the xls
    xls = pd.ExcelFile(full_fn)

    # read the prisma, we need to read this tab two times
    dft = xls.parse(tab_name_prisma, nrows=4)

    # first, get the basic info
    prisma = {}
    stage_list = dft.columns.tolist()
    for col in dft.columns:
        # col should be b1, b2, b3 ... f1, f2
        stage = col.strip()
        text = dft.loc[0, col]
        n_pmids = dft.loc[1, col]
        if np.isnan(n_pmids):
            n_pmids = None
        detail = dft.loc[2, col]
        if type(detail) != str:
            detail = None
        
        # create the basic 
        prisma[stage] = {
            'stage': stage,
            'n_pmids': n_pmids,
            'n_ctids': 0,
            'text': text,
            'detail': detail,
            'study_list': [],
            'paper_list': []
        }

    # the study dict is NCT based
    study_dict = {}
    # the paper dict is PMID based
    paper_dict = {}
    # then, get the nct and pmids, skip the text, number and detail rows
    dft = xls.parse(tab_name_prisma, skiprows=[1,2,3])
    for col in dft.columns:
        stage = col
        study_ids = dft[col][~dft[col].isna()].tolist()
            
        # update the studies
        for study_id in study_ids:
            # the pmid is a number, but we need it as a string
            study_id = str(study_id)
            # tmp is ctid,PMID format, e.g., NCT12345678,321908734
            tmp = study_id.split(',')

            if len(tmp) == 1:
                # only pmid ???
                ctid = tmp[0]
                pmid = tmp[0]
            elif len(tmp) == 2:
                ctid = tmp[0].strip()
                pmid = tmp[1].strip()
            else:
                continue

            try:
                # some pid are saved as a float number????
                # like 27918762.0???
                pmid = '%s' % int(float(pmid))
            except:
                pass
                
            # append this ctid to this stage
            if ctid not in prisma[stage]['study_list']:
                prisma[stage]['study_list'].append(ctid)

            # create a new in the study_dict for this nct
            if ctid not in study_dict:
                study_dict[ctid] = {
                    'ctid': ctid, 'latest_pmid': None, 'pmids': [],
                }

            # append this pmid to this stage
            if pmid not in prisma[stage]['paper_list']:
                prisma[stage]['paper_list'].append(pmid)
            
            # update the pmid information of this clinical trial
            study_dict[ctid]['latest_pmid'] = pmid
            study_dict[ctid]['pmids'].append(pmid)
            
            # create a new item in paper_dict for this pmid
            if pmid not in paper_dict:
                paper_dict[pmid] = {
                    'ctid': ctid, 'pmid': pmid
                }
            else:
                # what???
                pass
        
        if prisma[stage]['n_pmids'] is None:
            prisma[stage]['n_pmids'] = len(prisma[stage]['paper_list'])

        # update the number of ncts
        prisma[stage]['n_ctids'] = len(prisma[stage]['study_list'])


    # second, read more studies from second tab
    try:
        # the second tab is optional
        cols = ['study_id', 'title', 'date', 'journal', 'authors']
        dft = xls.parse(tab_name_studies, usecols='A:E', names=cols)
        for idx, row in dft.iterrows():
            study_id = ('%s'%row['study_id']).strip()
            is_ctid = False
            if study_id.startswith('NCT'):
                is_ctid = True
            else:
                # sometimes the value is weird ...
                try:
                    study_id = '%s' % int(float(study_id))
                except:
                    pass

            # update the study info
            if is_ctid:
                if study_id in study_dict:
                    for col in cols:
                        study_dict[study_id][col] = str(row[col])
                else:
                    pass
            else:
                if study_id in paper_dict:
                    for col in cols:
                        paper_dict[study_id][col] = str(row[col])
                else:
                    pass
    except Exception as err:
        # nothing, just ignore this error
        print(err)

    # reat the studies
    ret = {
        "prisma": prisma,
        "study_dict": study_dict,
        "paper_dict": paper_dict
    }

    return ret


def get_prisma_bef(project_id):
    '''
    Get the statistics for the PRISMA
    Including:

    - b: batch number
    - e: excluded
    - f: final number

    '''
    # get the basic stats
    stat = dora.get_screener_stat_by_project_id(project_id)

    # get the NCT number states
    papers = dora.get_papers(project_id)
    b1_study_list = []
    b4_study_list = []
    b5_study_list = []
    e1_study_list = []
    e2_study_list = []
    e3_study_list = []
    f1_study_list = []
    f2_study_list = []
    
    f1_paper_list = []
    f2_paper_list = []

    for paper in papers:
        rct_id = ''
        if 'rct_id' in paper.meta:
            rct_id = paper.meta['rct_id']
        
        # use the pid as rct id if it is missing
        if rct_id == '':
            rct_id = paper.pid

        stages = paper.get_ss_stages()
        # print(paper.ss_rs, stages)

        if ss_state.SS_STAGE_INCLUDED_SR in stages:
            f1_study_list.append(rct_id)
            f1_paper_list.append(paper.pid)

        if ss_state.SS_STAGE_INCLUDED_SRMA in stages:
            f2_study_list.append(rct_id)
            f2_paper_list.append(paper.pid)

    prisma = {
        'b1': {
            "n_ctids": len(b1_study_list),
            "n_pmids": stat[ss_state.SS_STAGE_ALL_OF_THEM],
        },
        'b2': {
            "n_ctids": 0,
            "n_pmids": 0,
        },
        'b3': {
            "n_ctids": 0,
            "n_pmids": 0,
        },
        'b4': {
            "n_ctids": len(b4_study_list),
            "n_pmids": stat[ss_state.SS_STAGE_DECIDED]
                - stat[ss_state.SS_STAGE_EXCLUDED_BY_FULLTEXT],
        },
        'b5': {
            "n_ctids": len(b5_study_list),
            "n_pmids": stat[ss_state.SS_STAGE_INCLUDED_SR]
                + stat[ss_state.SS_STAGE_EXCLUDED_BY_ABSTRACT]
        },

        'e1': {
            "n_ctids": len(e1_study_list),
            "n_pmids": stat[ss_state.SS_STAGE_EXCLUDED_BY_TITLE],
        },
        'e2': {
            "n_ctids": len(e2_study_list),
            "n_pmids": stat[ss_state.SS_STAGE_EXCLUDED_BY_ABSTRACT],
        },
        'e3': {
            "n_ctids": len(e3_study_list),
            "n_pmids": stat[ss_state.SS_STAGE_EXCLUDED_BY_FULLTEXT],
        },

        'f1': {
            "n_ctids": len(f1_study_list),
            "n_pmids": stat[ss_state.SS_STAGE_INCLUDED_SR],
            "study_list": f1_study_list,
            "paper_list": f1_paper_list
        },
        'f2': {
            "n_ctids": len(f2_study_list),
            "n_pmids": stat[ss_state.SS_STAGE_INCLUDED_SRMA],
            "study_list": f2_study_list,
            "paper_list": f2_paper_list
        }
    }

    return prisma, stat


def get_stat_aef(project_id):
    '''
    Get the statistics of the project for the PRISMA
    Including:

    - a auto + import
    - e excluded
    - f final

    '''
    stages = [
        { "stage": "a1",  "text": "Records identified through automatic update" },
        { "stage": "a2",  "text": "Records identified through batch import" },

        { "stage": "ax_na_na",  "text": "Unscreened records" },
        { "stage": "ax_p2_na",  "text": "Full-text reviewing" },

        { "stage": "e2",  "text": "Excluded by title" },
        { "stage": "e22", "text": "Excluded by abstract review" },
        { "stage": "e3",  "text": "Excluded by full-text review" },

        { "stage": "f1", "text": "Final number in qualitative synthesis (systematic review)" },
        { "stage": "f3", "text": "Final number in quantitative synthesis (meta-analysis)" }
    ]
    sql = """
    select project_id,
        
        count(case when ss_st in ('a10', 'a11', 'a12') then paper_id else null end) as a1,
        count(case when ss_st in ('a21', 'a22', 'a23') then paper_id else null end) as a2,

        count(case when ss_pr = 'na' and ss_rs = 'na' then paper_id else null end) as ax_na_na,
        count(case when ss_pr = 'p20' and ss_rs = 'na' then paper_id else null end) as ax_p2_na,
        
        count(case when ss_rs = 'e2' then paper_id else null end) as e2,
        count(case when ss_rs = 'e22' then paper_id else null end) as e22,
        count(case when ss_rs = 'e3' then paper_id else null end) as e3,
        
        count(case when ss_rs in ('f1', 'f3') then paper_id else null end) as f1,
        0 as f3
        

    from papers
    where project_id = '{project_id}'
        and is_deleted = 'no'
    group by project_id
    """.format(project_id=project_id)
    r = db.session.execute(sql).fetchone()

    if r is None:
        stat = {
            'stages': stages
        }
        for k in stages:
            stat[k['stage']] = {
                'count': 0,
                'pids': []
            }

        return stat

    # put the values in prisma dict
    stat = {
        'stages': stages
    }
    # for k in r.keys():
    #     stat[k] = {
    #         'count': r[k]
    #     }
    for k in stages:
        stat[k['stage']] = {
            'count': r[k['stage']],
            'pids': []
        }

    return stat
    

#####################################################################
# Deprecated functions
#####################################################################

def get_prisma_abeuf(project_id):
    '''
    Deprecated
    Get the statistics of the project for the PRISMA
    Including:

    - a auto update
    - b batch number
    - e excluded
    - u updated
    - f final

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
    