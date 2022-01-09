import time
from unicodedata import category

import numpy as np
from numpy.lib.function_base import extract
import pandas as pd
from tqdm import tqdm 

from sqlalchemy import and_, or_, not_
from sqlalchemy.orm.attributes import flag_modified

from lnma import settings
from lnma import util
from lnma import dora
from lnma import ss_state
from lnma.models import *

from lnma import db


def get_itable_by_keystr_and_cq_abbr(keystr, cq_abbr):
    '''
    Get the specific CQ itable in a project
    '''
    project = dora.get_project_by_keystr(keystr)

    if project is None:
        return None

    extract = Extract.query.filter(and_(
        Extract.project_id == project.project_id,
        Extract.meta['cq_abbr'] == cq_abbr,
        Extract.oc_type == 'itable'
    )).first()

    return extract


def get_itable_by_project_id_and_cq_abbr(project_id, cq_abbr):
    '''
    Get the specific CQ itable in a project
    '''
    extract = Extract.query.filter(and_(
        Extract.project_id == project_id,
        Extract.meta['cq_abbr'] == cq_abbr,
        Extract.oc_type == 'itable'
    )).first()

    return extract


def get_extracts_by_cate_and_name(keystr, cq_abbr, oc_type, group, category, full_name):
    '''
    Get extract by cate and name for detect duplicate purpose
    '''
    # first, get this paper
    project = dora.get_project_by_keystr(keystr)

    # second, check this
    sql = """
    select extract_id
    from extracts
    where project_id = '{project_id}'
        and oc_type = '{oc_type}'
        and JSON_EXTRACT(meta, '$.cq_abbr') = '{cq_abbr}'
        and JSON_EXTRACT(meta, '$.group') = '{group}'
        and JSON_EXTRACT(meta, '$.category') = '{category}'
        and JSON_EXTRACT(meta, '$.full_name') = '{full_name}'
    """.format(
        project_id=project.project_id,
        cq_abbr=cq_abbr,
        oc_type=oc_type,
        group=group,
        category=category,
        full_name=full_name
    )
    # print('* execute sql: %s' % sql)
    rs = db.session.execute(sql).fetchall()

    exts = []
    for r in rs:
        exts.append(
            dora.get_extract(r['extract_id'])
        )

    return exts
    

def create_empty_extract(keystr, cq_abbr, oc_type, group, category, full_name, other_meta={}):
    '''
    Create an extract with some infos
    '''

    # first, get this project
    project = dora.get_project_by_keystr(keystr)

    oc_abbr = util.mk_oc_abbr()
    default_meta = copy.deepcopy(settings.OC_TYPE_TPL[oc_type]['default'])

    # set some value to meta
    default_meta['abbr'] = oc_abbr
    default_meta['cq_abbr'] = cq_abbr
    default_meta['oc_type'] = oc_type
    default_meta['group'] = group
    default_meta['category'] = category
    default_meta['full_name'] = full_name

    # copy other values
    for key in other_meta:
        default_meta[key] = other_meta[key]

    # need to fix the cate
    default_meta['cate_attrs'] = copy.deepcopy(
        settings.INPUT_FORMAT_TPL[oc_type][default_meta['input_format']]
    )

    ext = dora.create_extract(
        project_id=project.project_id,
        oc_type=oc_type,
        abbr=oc_abbr,
        meta=default_meta,
        data={}
    )

    return ext


def update_extract_pwma_pre_data(extract, df, papers):
    '''
    Update extract data with a df of pre PWMA foramt

    study, year, TE, lowerci, upperci, treatment, control, survival in control, Ec, Et, pid

    The `TE, lowerci, upperci, survival in control, Ec, Et, pid` are required.
    '''
    # only one group when nma
    g_idx = 0

    # empty data
    data = {}

    # prepare the pids for detection
    pids = [ p.pid for p in papers ]
    pid2paper_id = {}
    for p in papers:
        pid2paper_id[p.pid] = p.paper_id
    missing_pids = []

    # check each row
    for idx, row in df.iterrows():
        pid = __get_pid(__get_val(row['pid']))

        # check this pid in pids or not
        if pid not in pids:
            print('* MISSING %s - pid: %s' % (
                extract.meta['full_name'],
                pid
            ))
            if pid not in missing_pids:
                missing_pids.append(pid)

            # now it is the difficult part
            # how to deal with this missing?
            # I think we need to skip these records first
            continue

        # next need to include this paper to this ext if not
        dora.update_paper_ss_cq_decision(
            pid2paper_id[pid],
            [{ 'abbr': extract.meta['cq_abbr'] }],
            'yes', 'Import'
        )
        
        # build the data object for this paper
        # the format is from the settings
        # this has to be a manually mapping
        arm = dict(
            TE = __get_val(row['TE']),
            lowerci = __get_val(row['lowerci']),
            upperci = __get_val(row['upperci']),

            survival_in_control = __get_val(row['survival in control']),
            Et = __get_val(row['Et']),
            Ec = __get_val(row['Ec']),
        )

        # ok, let's add this record
        if pid not in data:
            # nice! first time add
            data[pid] = copy.deepcopy(settings.DEFAULT_EXTRACT_DATA_PID_TPL)

            # add this to the main arm
            data[pid]['attrs']['main']['g0'] = arm

            # update the status
            data[pid]['is_selected'] = True
            data[pid]['is_checked'] = True

        else:
            # wow! it's multi arm study??
            data[pid]['attrs']['other'].append(
                {'g0': arm}
            )

            # and increase the n_arms
            data[pid]['n_arms'] += 1

    # update the extract
    ext = dora.update_extract_data(
        extract.project_id,
        extract.oc_type,
        extract.abbr,
        data
    )

    return ext, missing_pids


def update_extract_pwma_raw_data(extract, df, papers):
    '''
    Update extract data with a df of raw PWMA foramt

    study, year, Et, Nt, Ec, Nc, treatment, control, pid

    The Et, Nt, Ec, Nc, pid are required.
    '''
    # only one group when nma
    g_idx = 0

    # empty data
    data = {}

    # prepare the pids for detection
    pids = [ p.pid for p in papers ]
    pid2paper_id = {}
    for p in papers:
        pid2paper_id[p.pid] = p.paper_id
    missing_pids = []

    # check each row
    for idx, row in df.iterrows():
        pid = __get_pid(__get_val(row['pid']))

        # check this pid in pids or not
        if pid not in pids:
            print('* MISSING %s - pid: %s' % (
                extract.meta['full_name'],
                pid
            ))
            if pid not in missing_pids:
                missing_pids.append(pid)

            # now it is the difficult part
            # how to deal with this missing?
            # I think we need to skip these records first
            continue

        # next need to include this paper to this ext if not
        dora.update_paper_ss_cq_decision(
            pid2paper_id[pid],
            [{ 'abbr': extract.meta['cq_abbr'] }],
            'yes', 'Import'
        )
        
        # build the data object for this paper
        # the format is from the settings
        # this has to be a manually mapping
        arm = dict(
            Et = __get_val(row['Et']),
            Nt = __get_val(row['Nt']),
            Ec = __get_val(row['Ec']),
            Nc = __get_val(row['Nc']),
        )

        # ok, let's add this record
        if pid not in data:
            # nice! first time add
            data[pid] = copy.deepcopy(settings.DEFAULT_EXTRACT_DATA_PID_TPL)

            # add this to the main arm
            data[pid]['attrs']['main']['g0'] = arm

            # update the status
            data[pid]['is_selected'] = True
            data[pid]['is_checked'] = True

        else:
            # wow! it's multi arm study??
            data[pid]['attrs']['other'].append(
                {'g0': arm}
            )

            # and increase the n_arms
            data[pid]['n_arms'] += 1

    # update the extract
    ext = dora.update_extract_data(
        extract.project_id,
        extract.oc_type,
        extract.abbr,
        data
    )

    return ext, missing_pids


def update_extract_nma_pre_data(extract, df, papers):
    '''
    Update extract data with a df of pre data format
    '''
    # only one group when nma
    g_idx = 0

    # empty data
    data = {}

    def __get_sm(row):
        if 'sm' in row: return row['sm']
        if 'hr' in row: return row['hr']
        return ''

    # prepare the pids for detection
    pids = [ p.pid for p in papers ]
    pid2paper_id = {}
    for p in papers:
        pid2paper_id[p.pid] = p.paper_id
    missing_pids = []

    # check each row
    for idx, row in df.iterrows():
        pid = __get_pid(__get_val(row['pid']))

        # check this pid in pids or not
        if pid not in pids:
            print('* MISSING %s - pid: %s' % (
                extract.meta['full_name'],
                pid
            ))
            if pid not in missing_pids:
                missing_pids.append(pid)

            # now it is the difficult part
            # how to deal with this missing?
            # I think we need to skip these records first
            continue

        # next need to include this paper to this ext if not
        dora.update_paper_ss_cq_decision(
            pid2paper_id[pid],
            [{ 'abbr': extract.meta['cq_abbr'] }],
            'yes', 'Import'
        )

        # build the data object for this paper
        # the format is from the settings
        # this has to be a manually mapping
        arm = dict(
            t1 = str(row['t1']),
            t2 = str(row['t2']),
            sm = str(__get_sm(row)),
            lowerci = str(row['lowerci']),
            upperci = str(row['upperci']),
            survival_t1 = str(__get_val(row['survival in t1'])),
            survival_t2 = str(__get_val(row['survival in t2'])),
            Ec_t1 = str(__get_val(row['Ec_t1'])),
            Et_t1 = str(__get_val(row['Et_t1'])),
            Ec_t2 = str(__get_val(row['Ec_t2'])),
            Et_t2 = str(__get_val(row['Et_t2'])),
        )

        # ok, let's add this record
        if pid not in data:
            # nice! first time add
            data[pid] = copy.deepcopy(settings.DEFAULT_EXTRACT_DATA_PID_TPL)

            # add this to the main arm
            data[pid]['attrs']['main']['g0'] = arm

            # update the status
            data[pid]['is_selected'] = True
            data[pid]['is_checked'] = True

        else:
            # wow! it's multi arm study??
            data[pid]['attrs']['other'].append(
                {'g0': arm}
            )

            # and increase the n_arms
            data[pid]['n_arms'] += 1
    
    # update the extract
    ext = dora.update_extract_data(
        extract.project_id,
        extract.oc_type,
        extract.abbr,
        data
    )

    return ext, missing_pids


def update_extract_nma_raw_data(extract, df, papers):
    '''
    Update extract data with a df of raw data format

    The df format looks like the following:

    study	treat	event	total	pid
    name_x	LenPem	244	355	33616314
    name_x	Suni	122	357	33616314
    name_y	LenPem	244	355	33616312
    name_y	Suni	122	357	33616312

    there should be 5 columns and each study will have two rows.

    '''
    # only one group when nma
    g_idx = 0

    # empty data
    data = {}

    pids = [ p.pid for p in papers ]
    pid2paper_id = {}
    for p in papers:
        pid2paper_id[p.pid] = p.paper_id
    missing_pids = []

    # check records two by two
    for i in range(len(df)//2):
        # get the first and second row of current idx 
        idx = i * 2
        rows = [
            df.iloc[idx],
            df.iloc[idx+1]
        ]

        # first, need to check these two pids
        pid1 = __get_pid(__get_val(rows[0]['pid']))
        pid2 = __get_pid(__get_val(rows[0]['pid']))

        if pid1 != pid2:
            # what????
            # this must be some kind of mismatch error
            print('* MISMATCH row %s: %s - %s' % (
                idx, pid1, pid2
            ))
            continue

        # ok, now just use one pid
        pid = pid1

        # check this pid in pids or not
        # due to the 2-row format design
        if pid not in pids:
            print('* MISSING %s - pid: %s' % (
                extract.meta['full_name'],
                pid
            ))
            if pid not in missing_pids:
                missing_pids.append(pid)
            
            # now it is the difficult part
            # how to deal with this missing?
            # I think we need to skip these records first
            continue

        # next need to include this paper to this ext if not
        dora.update_paper_ss_cq_decision(
            pid2paper_id[pid],
            [{ 'abbr': extract.meta['cq_abbr'] }],
            'yes', 'Import'
        )

        # build the arm
        arm = dict(
            t1 = __get_val(rows[0]['treat']),
            t2 = __get_val(rows[1]['treat']),

            event_t1 = __get_val(rows[0]['event']),
            total_t1 = __get_val(rows[0]['total']),

            event_t2 = __get_val(rows[1]['event']),
            total_t2 = __get_val(rows[1]['total']),
        )

        # check this data
        if pid not in data:
            # ok, create this record
            # nice! first time add
            data[pid] = copy.deepcopy(settings.DEFAULT_EXTRACT_DATA_PID_TPL)

            # add this to the main arm
            # it's the first row here, so the t2 is empty
            data[pid]['attrs']['main']['g0'] = arm

            # update the status
            data[pid]['is_selected'] = True
            data[pid]['is_checked'] = True

        else:
            # ok, it's a multi arm study!
            # wow! it's multi arm study??
            data[pid]['attrs']['other'].append(
                {'g0': arm}
            )

            # and increase the n_arms
            data[pid]['n_arms'] += 1

    # update the extract
    ext = dora.update_extract_data(
        extract.project_id,
        extract.oc_type,
        extract.abbr,
        data
    )

    return ext, missing_pids


def import_extracts_from_xls(full_path, keystr, cq_abbr, oc_type):
    '''
    Import extracts to database
    '''
    project = dora.get_project_by_keystr(keystr)

    # load data
    xls = pd.ExcelFile(full_path)

    # build AE Category data
    first_sheet_name = xls.sheet_names[0]
    dft = xls.parse(first_sheet_name)
    dft = dft[~dft['full_name'].isna()]
    
    print(dft.head())

    # get all included papers for decision
    papers = dora.get_papers_of_included_sr(
        project.project_id
    )

    missing_pids = []
    # columns we could use 
    for idx, row in dft.iterrows():
        tab_name = row['name'].strip()
        data_type = row['data_type'].strip()
        print('*'*40, keystr, cq_abbr, oc_type, '[%s]' % tab_name, '|', data_type)
        
        # the general meta information for an outcome
        meta = dict(
            cq_abbr = cq_abbr,
            oc_type = oc_type,
            group = row['analysis_title'].strip(),
            category = row['category'].strip(),
            full_name = row['full_name'].strip(),
            which_is_better = row['which_is_better'].strip(),
            fixed_or_random = row['fixed_or_random'].strip(),
            measure_of_effect = row['measure'].strip(),
            included_in_plots = row['included_in_plots'].strip(),
            included_in_sof = row['included_in_sof'].strip()
        )

        # special rule for NMA
        if oc_type == 'nma':
            # include this extract in evidence map or not
            meta['included_in_em'] = row['included_in_em'].strip()

            # for NMA, freq or bayes?
            meta['analysis_method'] = row['method'].strip()

            # the current data type
            meta['input_format'] = {
                'pre':'NMA_PRE_SMLU', 
                'raw':'NMA_RAW_ET'
            }[data_type]

        # special rule for PWMA
        if oc_type == 'pwma':
            # the certainty for this outcome
            meta['certainty'] = {
                'cie': '0',
                'risk_of_bias': row['risk_of_bias'],
                'inconsistency': row['inconsistency'],
                'indirectness': row['indirectness'],
                'imprecision': row['imprecision'],
                'publication_bias': row['publication_bias'],
                'importance': row['importance'],
            }

            # the treatment and control
            meta['treatments'] = [
                row['treatment'],
                row['control']
            ]

            # the data type
            meta['input_format'] = {
                'pre': 'PRIM_CAT_PRE', 
                'raw': 'PRIM_CAT_RAW'
            }[data_type]

        # check exist
        exts = get_extracts_by_cate_and_name(
            keystr, 
            cq_abbr,
            oc_type,
            meta['group'],
            meta['category'],
            meta['full_name']
        )

        if len(exts) != 0:
            # remove these
            for ext in exts:
                dora.delete_extract(
                    ext.project_id,
                    ext.oc_type,
                    ext.abbr
                )
                print('* removed ext %s' % ext.abbr)
        
        ext = create_empty_extract(
            keystr, 
            cq_abbr,
            oc_type,
            meta['group'],
            meta['category'],
            meta['full_name'],
            meta
        )
        print('* created ext %s' % ext.abbr)

        # now let's update data
        df_oc = xls.parse(tab_name)

        # need to exclude those with empty study name
        df_oc = df_oc[~df_oc['study'].isna()]

        if oc_type == 'nma':
            if data_type == 'pre':
                ext, ms_pids = update_extract_nma_pre_data(ext, df_oc, papers)
                missing_pids = list(set(missing_pids + ms_pids))

                print('* updated ext pre data %s' % ext.abbr)

            elif data_type == 'raw':
                ext, ms_pids = update_extract_nma_raw_data(ext, df_oc, papers)
                missing_pids = list(set(missing_pids + ms_pids))
                print('* updated ext raw data %s' % ext.abbr)

        elif oc_type == 'pwma':
            if data_type == 'pre':
                pass

            elif data_type == 'raw': 
                ext, ms_pids = update_extract_pwma_raw_data(ext, df_oc, papers)
                missing_pids = list(set(missing_pids + ms_pids))
                print('* updated ext raw data %s' % ext.abbr)
    
    print('\n\n\n* MISSING pids:')
    for pid in missing_pids:
        print(pid)

    return dft


###########################################################
# Utils for management
###########################################################

def reset_extracts_includes(keystr, cq_abbr, include_in, yes_or_no):
    '''
    Reset all extracts' include in 
    '''
    extracts = dora.get_extracts_by_keystr_and_cq(keystr, cq_abbr)

    for ext in tqdm(extracts):
        if include_in == 'plots':
            ext.meta['included_in_plots'] = yes_or_no            
            flag_modified(ext, 'meta')
            db.session.add(ext)
            db.session.commit()

        elif include_in == 'sof':
            ext.meta['included_in_sof'] = yes_or_no
            flag_modified(ext, 'meta')
            db.session.add(ext)
            db.session.commit()

        else:
            pass

    print('* done reset')


def __get_val(v):
    '''
    Helper function for getting values from df cell
    '''
    if pd.isna(v): 
        return ''
    return str(v).strip()


def __get_pid(v):
    '''
    Helper function for pid
    '''
    try:
        pid = str(int(float(v)))
        return pid
    except:
        return v