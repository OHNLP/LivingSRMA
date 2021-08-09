import os
import pandas as pd

from flask import current_app

from lnma import dora
from lnma import srv_extract
from lnma import srv_paper
from lnma import util
from lnma import ss_state
from lnma import settings

'''
Services of PRISMA for publication site
'''
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
    prisma, stat = srv_paper.get_prisma_bef(project_id)

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
