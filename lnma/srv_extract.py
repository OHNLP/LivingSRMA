import os
import time
import math

import numpy as np
from collections import OrderedDict
import pandas as pd
from tqdm import tqdm 

from sqlalchemy import and_, or_, not_
from sqlalchemy.orm.attributes import flag_modified

from lnma import settings
from lnma import util
from lnma import dora
from lnma import ss_state
from lnma import srv_paper
from lnma.models import *

from lnma import db


def copy_extracts(
    keystr_a,
    cq_abbr_a,
    group_a,

    keystr_b,
    cq_abbr_b,
    group_b,

    oc_type,
    skip_exists=True,
    skip_data=True
):
    '''
    Copy extracts from one group to another of same oc_type

    Please make sure the data
    '''
    project_a = dora.get_project_by_keystr(keystr_a)
    project_b = dora.get_project_by_keystr(keystr_b)

    if project_a is None:
        return None

    if project_b is None:
        return None

    # TODO, check the groups

    # Get all the extracts
    extracts_a = dora.get_extracts_by_keystr_and_cq_and_oc_type_and_group(
        keystr_a,
        cq_abbr_a,
        oc_type,
        group_a
    )

    # Copy to new projects
    extracts_b = []
    for ext_a in tqdm(extracts_a):
        # check if the abbr exists
        _ext_b = dora.get_extract_by_keystr_and_cq_and_abbr(
            keystr_b, 
            cq_abbr_b,
            ext_a.abbr
        )

        # update the meta
        new_meta = copy.deepcopy(ext_a.meta)
        new_meta['cq_abbr'] = cq_abbr_b
        new_meta['group'] = group_b

        if _ext_b is None:
            # great, there is no ext in this cq yet

            ext_b = dora.create_extract(
                project_b.project_id,
                oc_type,
                ext_a.abbr,
                new_meta,
                {} if skip_data else ext_a.data
            )
            extracts_b.append(ext_b)
            print('* copied extract %s' % ext_b.get_repr_str())

        else:
            # what??? this exists??
            if skip_exists:
                print('* skip duplicated extract %s' % ext_a.get_repr_str())

            else:
                # create a new abbr for this 
                new_abbr = util.mk_oc_abbr()
                new_meta['abbr'] = new_abbr
                ext_b = dora.create_extract(
                    project_b.project_id,
                    oc_type,
                    new_abbr,
                    new_meta,
                    {} if skip_data else ext_a.data
                )
                extracts_b.append(ext_b)
                print('* copied extract %s' % ext_b.get_repr_str())

    return extracts_b


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


def update_extract_pwma_pre_data(extract, df, papers, is_subg=False):
    '''
    Update extract data with a df of pre PWMA foramt

    study, year, TE, lowerci, upperci, treatment, control, survival in control, Ec, Et, pid

    The `TE, lowerci, upperci, survival in control, Ec, Et, pid` are required.

    But the `survival in control`, `Ec`, `Et` may not be available.

    If this extract is about subgroup analysis, there should be an `subgroup` column
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

    # special for subg analysis
    subgroup_dict = {}

    # need to update the extract meta
    new_meta = copy.deepcopy(extract.meta)

    # check each row
    for idx, row in df.iterrows():
        # no matter what, get the pid first
        pid = __get_pid(__get_val(row['pid']))

        if idx == 0:
            # use the first record to update the treatment
            treatment = __get_val(row['treatment'])
            control = __get_val(row['control'])
            new_meta['treatments'] = [
                treatment, control
            ]

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
            'yes', 
            'Import'
        )
        
        # build the data object for this paper
        # the format is from the settings
        # this has to be a manually mapping
        arm = dict(
            TE = __get_val(row['TE']),
            lowerci = __get_val(row['lowerci']),
            upperci = __get_val(row['upperci']),

            survival_in_control = __get_val(__get_col(row, 'survival in control')),
            Et = __get_val(__get_col(row, 'Et')),
            Ec = __get_val(__get_col(row, 'Ec')),
        )

        # now, need to check if this is a subg analysis
        # by default, the subg_code is always g0
        # which means there is only one group for this analysis
        subg_code = 'g0'
        if is_subg:
            subg = row['subgroup']

            # if this a new subgroup?
            if subg not in subgroup_dict:
                # this is a new subgroup, assign a group id for this
                subgroup_dict[subg] = 'g%s' % (len(subgroup_dict))

            # get the subg_code for this subgroup
            subg_code = subgroup_dict[subg]

        # ok, let's add this record
        if pid not in data:
            # nice! first time add
            data[pid] = copy.deepcopy(settings.DEFAULT_EXTRACT_DATA_PID_TPL)

            # add this to the main arm
            data[pid]['attrs']['main'][subg_code] = arm

            # update the status
            data[pid]['is_selected'] = True
            data[pid]['is_checked'] = True

        else:
            # then need to check subg
            if is_subg:
                # as long as this paper has been added
                # we just need to add this subgroup
                data[pid]['attrs']['main'][subg_code] = arm

            else:
                # so this is not for subgroup analysis
                # the duplicated pid means 
                # wow! it's multi arm study??
                data[pid]['attrs']['other'].append(
                    {subg_code: arm}
                )

                # and increase the n_arms
                data[pid]['n_arms'] += 1

    # update the subg settings if is subgroup analysis
    if is_subg:
        # get the sub_groups
        sub_groups = []

        # create a dict for reverse search
        g2subg_dict = {}
        for k in subgroup_dict:
            v = subgroup_dict[k]
            g2subg_dict[v] = k

        # loop on the values and convert to the ordered list
        for i in range(len(g2subg_dict)):
            sub_groups.append(
                g2subg_dict['g%s'%i]
            )

        # set the subgs
        new_meta['sub_groups'] = sub_groups
        print("* updated subgroups: %s" % (
            sub_groups
        ))

    # # update meta
    # ext = dora.update_extract_meta(
    #     extract.project_id,
    #     extract.oc_type,
    #     extract.abbr,
    #     new_meta
    # )

    # # update the extract
    # ext = dora.update_extract_data(
    #     extract.project_id,
    #     extract.oc_type,
    #     extract.abbr,
    #     data
    # )

    ext = dora.update_extract_meta_and_data(
        extract.project_id,
        extract.oc_type,
        extract.abbr,
        new_meta,
        data
    )

    return ext, missing_pids


def update_extract_pwma_raw_data(extract, df, papers, is_subg=False):
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

    # special for subg analysis
    subgroup_dict = {}

    # need to update the extract meta accordingly
    new_meta = copy.deepcopy(extract.meta)

    # check each row
    for idx, row in df.iterrows():
        pid = __get_pid(__get_val(row['pid']))

        if idx == 0:
            # use the first record to update the treatment
            treatment = __get_val(row['treatment'])
            control = __get_val(row['control'])
            new_meta['treatments'] = [
                treatment, control
            ]

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
            'yes', 
            'Import'
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

        # now, need to check if this is a subg analysis
        # by default, the subg_code is always g0
        # which means there is only one group for this analysis
        subg_code = 'g0'
        if is_subg:
            subg = row['subgroup']

            # if this a new subgroup?
            if subg not in subgroup_dict:
                # this is a new subgroup, assign a group id for this
                subgroup_dict[subg] = 'g%s' % (len(subgroup_dict))

            # get the subg_code for this subgroup
            subg_code = subgroup_dict[subg]

        # ok, let's add this record
        if pid not in data:
            # nice! first time add
            data[pid] = copy.deepcopy(settings.DEFAULT_EXTRACT_DATA_PID_TPL)

            # add this to the main arm
            data[pid]['attrs']['main'][subg_code] = arm

            # update the status
            data[pid]['is_selected'] = True
            data[pid]['is_checked'] = True

        else:
            # then need to check subg
            if is_subg:
                # as long as this paper has been added
                # we just need to add this subgroup
                data[pid]['attrs']['main'][subg_code] = arm

            else:
                # so this is not for subgroup analysis
                # the duplicated pid means 
                # wow! it's multi arm study??
                data[pid]['attrs']['other'].append(
                    {subg_code: arm}
                )

                # and increase the n_arms
                data[pid]['n_arms'] += 1

    # update the subg settings if is subgroup analysis
    if is_subg:
        # get the sub_groups
        sub_groups = []

        # create a dict for reverse search
        g2subg_dict = {}
        for k in subgroup_dict:
            v = subgroup_dict[k]
            g2subg_dict[v] = k

        # loop on the values and convert to the ordered list
        for i in range(len(g2subg_dict)):
            sub_groups.append(
                g2subg_dict['g%s'%i]
            )

        # set the subgs
        new_meta['sub_groups'] = sub_groups
        print("* updated subgroups: %s" % (
            sub_groups
        ))

    # # update meta
    # ext = dora.update_extract_meta(
    #     extract.project_id,
    #     extract.oc_type,
    #     extract.abbr,
    #     new_meta
    # )

    # # update the extract
    # ext = dora.update_extract_data(
    #     extract.project_id,
    #     extract.oc_type,
    #     extract.abbr,
    #     data
    # )

    ext = dora.update_extract_meta_and_data(
        extract.project_id,
        extract.oc_type,
        extract.abbr,
        new_meta,
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
            'yes', 
            'Import'
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
            survival_t1 = str(__get_val(__get_col(row, 'survival in t1'))),
            survival_t2 = str(__get_val(__get_col(row, 'survival in t2'))),
            Ec_t1 = __get_int_val(row['Ec_t1']),
            Et_t1 = __get_int_val(row['Et_t1']),
            Ec_t2 = __get_int_val(row['Ec_t2']),
            Et_t2 = __get_int_val(row['Et_t2']),
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
    name_x	LenPem	244  	355	    33616314
    name_x	Suni	122	    357	    33616314
    name_y	LenPem	244	    355	    33616312
    name_y	Suni	122	    357	    33616312

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
            'yes', 
            'Import'
        )

        # build the arm
        arm = dict(
            t1 = __get_int_val(rows[0]['treat']),
            t2 = __get_int_val(rows[1]['treat']),

            event_t1 = __get_int_val(rows[0]['event']),
            total_t1 = __get_int_val(rows[0]['total']),

            event_t2 = __get_int_val(rows[1]['event']),
            total_t2 = __get_int_val(rows[1]['total']),
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
    missing_tabs = []
    pid2tabs = {}

    # columns we could use 
    for idx, row in dft.iterrows():
        tab_name = row['name'].strip()
        data_type = row['data_type'].strip()
        analysis_group = row['analysis_title'].strip()
        print('*'*40, keystr, cq_abbr, oc_type, analysis_group, '[%s]' % tab_name, '|', data_type)
        
        # search this tab first
        if tab_name not in xls.sheet_names:
            print('* NOT FOUND SHEET [%s]' % tab_name)
            missing_tabs.append(tab_name)
            continue

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
            included_in_sof = row['included_in_sof'].strip(),
            is_subg_analysis = 'no',
            sub_groups = ['A']
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
            # the values could be NaN, so need to check
            meta['certainty'] = {
                'cie': '0',
                'risk_of_bias': "%s"%__get_int_val(__get_col(row, 'risk_of_bias'), '0'),
                'inconsistency': "%s"%__get_int_val(__get_col(row, 'inconsistency'), '0'),
                'indirectness': "%s"%__get_int_val(__get_col(row, 'indirectness'), '0'),
                'imprecision': "%s"%__get_int_val(__get_col(row, 'imprecision'), '0'),
                'publication_bias': "%s"%__get_int_val(__get_col(row, 'publication_bias'), '0'),
                'importance': __cie_imp2val(__get_val(__get_col(row, 'importance'), '0')),
            }

            # the treatment and control
            # but the value can be empty
            # need to double check in the data sheet
            val_t = __get_val(row['treatment'])
            val_c = __get_val(row['control'])
            meta['treatments'] = [
                val_t,
                val_c
            ]

            # the data type
            meta['input_format'] = {
                'pre': 'PRIM_CAT_PRE', 
                'raw': 'PRIM_CAT_RAW'
            }[data_type]

            # now need to check subg analysis
            if meta['group'] == 'subgroup':
                meta['is_subg_analysis'] = 'yes'

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
        print('* found %s records for this oc' % (
            len(df_oc)
        ))
        
        # update the pid used by oc
        pids = list(set(df_oc[~df_oc['pid'].isna()]['pid'].tolist()))
        for _pid in pids:
            _pid = __get_pid(__get_val(_pid))
            if _pid not in pid2tabs: pid2tabs[_pid] = []
            pid2tabs[_pid].append(tab_name)

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
            # one more thing for pwma is that is this a subg analysis
            is_subg = meta['is_subg_analysis'] == 'yes'
            if data_type == 'pre':
                ext, ms_pids = update_extract_pwma_pre_data(ext, df_oc, papers, is_subg)
                missing_pids = list(set(missing_pids + ms_pids))
                print('* updated ext pre data %s' % ext.abbr)

            elif data_type == 'raw': 
                ext, ms_pids = update_extract_pwma_raw_data(ext, df_oc, papers, is_subg)
                missing_pids = list(set(missing_pids + ms_pids))
                print('* updated ext raw data %s' % ext.abbr)
    
    print('\n\n\n* MISSING pids:')
    for pid in missing_pids:
        print(pid, ':', pid2tabs[pid])
    print('\n\n\n* MISSING tabs:')
    for tab in missing_tabs:
        print(tab)
    
    if len(missing_pids) == 0 and \
       len(missing_tabs) == 0:
        print('\n\n\n* GREAT! It seems NO issue found!\n')

    else:
        print('\n\n\n* TOO BAD! Something is missing!\n')


    return dft


###############################################################################
# Utils for the itable
###############################################################################

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


def import_itable_from_xls(
    keystr, 
    cq_abbr, 
    full_fn_itable, 
    full_fn_filter
):
    '''
    Import itable all data from xls file

    Including:

    1. meta data for attributes
    2. data of extraction
    3. filters

    the itable file name is 'ITABLE_ATTR_DATA.xlsx' or other
    the filters name is ITABLE_FILTERS.xlsx or other
    '''
    project = dora.get_project_by_keystr(keystr)

    # if project is None:
    #     project_id = request.cookies.get('project_id')
    #     project = dora.get_project(project_id)

    if project is None:
        return None
    
    project_id = project.project_id
    oc_type = 'itable'

    # in fact, due to the update the cq, this is also needed to be updated
    # cq_abbr = 'default'

    # get the exisiting extracts
    # extract = dora.get_extract_by_project_id_and_abbr(
    #     project.project_id, abbr
    # )
    extract = dora.get_itable_by_project_id_and_cq(
        project_id, 
        cq_abbr
    )

    # if not exist, create a new one which is empty
    if extract is None:
        abbr = util.mk_abbr()
        meta = copy.deepcopy(settings.OC_TYPE_TPL['itable']['default'])
        meta['cq_abbr'] = cq_abbr
        extract = dora.create_extract(
            project_id, oc_type, abbr, 
            settings.OC_TYPE_TPL['itable']['default'],
            {}
        )

    # 2022-02-19: fix the order
    abbr = extract.abbr

    # get the itable data
    cad, cate_attrs, i2a, data, not_found_pids = get_itable_from_itable_data_xls(
        project.keystr, 
        cq_abbr,
        full_fn_itable
    )
    if cate_attrs is None:
        # something wrong???
        return None

    print('* not found pid %s' % (
        len(not_found_pids)
    ))
    for _ in not_found_pids:
        print('* - %s' % (_))

    # update the meta
    meta = extract.meta
    meta['cate_attrs'] = cate_attrs

    # get the filters
    filters = get_itable_filters_from_xls(
        project.keystr, 
        full_fn_filter
    )
    if filters == []:
        print('* not found filters')

    meta['filters'] = filters

    # update the extract
    # pprint(filters)
    itable = dora.update_extract_meta_and_data(
        project_id, oc_type, abbr, meta, data
    )

    return itable


def get_itable_from_itable_data_xls(
    keystr, 
    cq_abbr,
    full_fn
    ):
    '''
    Get the itable extract from ITABLE_ATTR_DATA.xlsx
    '''
    if not os.path.exists(full_fn):
        # try the xls file
        # full_fn = full_fn[:-1]
        # what's wrong???
        return None, None, None, None, None

    # get this project
    project = dora.get_project_by_keystr(keystr)
    if project is None:
        return None, None, None, None, None

    # get the ca list first
    ca_dict, ca_list, i2a = get_cate_attr_subs_from_itable_data_xls(
        full_fn
    )

    # read the first sheet, but skip the first row
    xls = pd.ExcelFile(full_fn)
    first_sheet_name = xls.sheet_names[0]
    df = xls.parse(first_sheet_name, skiprows=1)

    # 2021-06-27: weird bug, read so many NaN columns
    df = df.dropna(axis=1, how='all')

    cols = df.columns
    n_cols = len(df.columns)
    cols_lower = [ _.lower() for _ in cols ]

    # a pmid/pid based dictionary
    data = {}

    # use this to locate those not found pid
    not_found_pids = []

    # begin loop 
    for _, row in df.iterrows():
        # find the pmid first
        if 'PMID' in row:
            pmid = row['PMID']
        else:
            pmid = row['PubMed ID']

        # try to make sure it's NOT something like 12345678.0
        if pd.isna(pmid):
            # this is a NaN value for pmid
            # can not parse this kind of value
            print('* error when parsing NaN pmid at Row[%s]' % ( _ ))
            continue

        try:
            pmid = int(pmid)

            # must make sure the pmid is a string
            pmid = '%s' % pmid

            # the pmid may contain blank
            pmid = pmid.strip()
            pmid = '%s' % int(pmid)
        except:
            print('* error when parsing pmid[%s]' % ( pmid ))
            # 2022-02-04: now we support DOI as pid
            # just remove the blanks
            # last try, just
            pmid = pmid.strip()

        # get the NCT
        if 'Trial registration #' in row:
            nct8 = row['Trial registration #'].strip()
        else:
            nct8 = ''

        # 2022-02-04: sometimes the nct is from Col NCT
        if 'NCT' in row:
            nct8 = row['NCT']

        # get the decision
        if 'Included in MA' in row:
            included_in_ma = ('%s'%row['Included in MA']).strip().upper()
        else:
            included_in_ma = 'NO'

        # check if this pmid exists
        is_main = False
        if pmid in data:
            # which means this row is an multi arm
            # add a new object in `other`
            # that's all we need to do
            data[pmid]['n_arms'] += 1
            data[pmid]['attrs']['other'].append({'g0':{}}) # subg 0 (in fact no subg)

        else:
            # ok, this is a new study
            # by default not selected and not checked
            # 
            # `main` is for the main records
            # `other` is for other arms, by default, other is empty
            data[pmid] = {
                'is_selected': True,
                'is_checked': True,
                'n_arms': 2,
                'attrs': {
                    'main': {'g0': {}}, # follow the pattern shared by subg
                    'other': []
                }
            }
            is_main = True

            # it's better to update the nct information
            is_success, p = srv_paper.set_paper_rct_id(
                keystr, pmid, nct8
            )

            if is_success:
                # ok, updated the nct for this paper
                pass
            else:
                print('* warning when setting rct_id [%s] to %s, skipped' % (
                    nct8, pmid
                ))

            # next, if a study is in itable.xls,
            # it must be included sr at least
            p = dora.get_paper_by_project_id_and_pid(
                project.project_id, pmid
            )

            if p is None:
                # BUT, it is possible that this pmid is not found
                print('* NOT found pid[%s]' % (
                    pmid
                ))
                not_found_pids.append(
                    pmid
                )

            else:
                # OK, we found this paper!
                sss = p.get_ss_stages()
                # if ss_state.SS_STAGE_INCLUDED_SR in sss:
                #     # OK, this study is included in SR at least
                #     pass

                # else:

                # set the stage for this paper
                # change stage!
                _, p = srv_paper.set_paper_ss_decision(
                    project, 
                    cq_abbr,
                    pmid, 
                    ss_state.SS_PR_CHECKED_BY_ADMIN,
                    ss_state.SS_RS_INCLUDED_ONLY_SR,
                    ss_state.SS_REASON_CHECKED_BY_ADMIN,
                    ss_state.SS_STAGE_INCLUDED_ONLY_SR
                )

                # OK, updated
                print('* updated %s from %s to %s' % (
                    pmid, sss, p.get_ss_stages()
                ))
                    

        # now check each column for this study
        for idx in range(n_cols):
            col = cols[idx]

            # skip the pmid column
            # since we already use this column as the key
            if col.upper() in settings.EXTRACTOR_ITABLE_IMPORT_SKIP_COLUMNS:
                continue

            # get the value in this column
            val = row[col]

            # try to clear the blanks
            try: val = val.strip()
            except: pass
            
            # for NaN value
            if pd.isna(val): val = None

            abbr = i2a[idx]

            if is_main:
                data[pmid]['attrs']['main']['g0'][abbr] = val
            else:
                # check if this value is same in the main track
                if val == data[pmid]['attrs']['main']['g0'][abbr]: 
                    # for the same value, also set ...
                    data[pmid]['attrs']['other'][-1]['g0'][abbr] = val
                else:
                    # just save the different values
                    data[pmid]['attrs']['other'][-1]['g0'][abbr] = val
            
            # print('* added col[%s] as abbr[%s] val[%s]' % (col, abbr, val))

        print('* added %s %s arms with [%s]' % (
            pmid, data[pmid]['n_arms'], nct8
        ))

    return ca_dict, ca_list, i2a, data, not_found_pids


def get_cate_attr_subs_from_itable_data_xls(full_fn):
    '''
    Get the cate, attr, and subs from the given file
    '''
    if not os.path.exists(full_fn):
        # try the xls file ? wh
        # full_fn = full_fn[:-1]

        # 2022-02-04: no matter what it is, return None
        return None, None, None

    # read the first sheet
    xls = pd.ExcelFile(full_fn)
    first_sheet_name = xls.sheet_names[0]
    df = xls.parse(first_sheet_name, header=None, nrows=2)

    # 2021-06-27: weird bug, read so many NaN columns
    # df = pd.read_excel(full_fn)
    df = df.dropna(axis=1, how='all')

    # convert to other shape
    dft = df.T
    df_attrs = dft.rename(columns={0: 'cate', 1: 'attr'})

    # not conver to tree format
    cate_attr_dict = OrderedDict()
    idx2abbr = {}

    # check each attr
    for idx, row in df_attrs.iterrows():
        vtype = 'text'

        if type(row['cate']) != str:
            if math.isnan(row['cate']) \
                or math.isnan(row['attr']):
                print('* skip nan cate or attr idx %s' % idx)
                continue


        print("* found %s | %s" % (
            row['cate'], row['attr']
        ))

        # found cate and attr
        cate = row['cate'].strip()
        attr = row['attr'].strip()

        # skip some attrs
        if attr.upper() in settings.EXTRACTOR_ITABLE_IMPORT_SKIP_COLUMNS:
            continue
        
        # put this cate if not exists
        if cate not in cate_attr_dict:
            cate_attr_dict[cate] = {
                'abbr': util.mk_abbr_12(),
                'name': cate,
                'attrs': {}
            }

        # split the name into different parts
        attr_subs = attr.split('|')
        if len(attr_subs) > 1:
            attr = attr_subs[0].strip()
            sub = attr_subs[1].strip()
        else:
            attr = attr
            sub = None

        # put this attr if not exists
        if attr not in cate_attr_dict[cate]['attrs']:
            cate_attr_dict[cate]['attrs'][attr] = {
                'abbr': util.mk_abbr_12(),
                'name': attr,
                'subs': None
            }
        
        # put this sub
        if sub is not None:
            if cate_attr_dict[cate]['attrs'][attr]['subs'] is None:
                cate_attr_dict[cate]['attrs'][attr]['subs'] = [{
                    'abbr': util.mk_abbr_12(),
                    'name': sub
                }]
            else:
                cate_attr_dict[cate]['attrs'][attr]['subs'].append({
                    'abbr': util.mk_abbr_12(),
                    'name': sub
                })
            # point the idx to the last sub in current attr
            idx2abbr[idx] = cate_attr_dict[cate]['attrs'][attr]['subs'][-1]['abbr']
        else:
            # point the idx to the attr
            idx2abbr[idx] = cate_attr_dict[cate]['attrs'][attr]['abbr']
    
    # convert the dict to list
    cate_attr_list = []
    for _i in cate_attr_dict:
        cate = cate_attr_dict[_i]
        # put this cate
        _cate = {
            'abbr': cate['abbr'],
            'name': cate['name'],
            'attrs': []
        }

        for _j in cate['attrs']:
            attr = cate['attrs'][_j]
            # put this attr
            _attr = {
                'abbr': attr['abbr'],
                'name': attr['name'],
                'subs': attr['subs']
            }
            _cate['attrs'].append(_attr)

        cate_attr_list.append(_cate)

    return cate_attr_dict, cate_attr_list, idx2abbr


def get_itable_filters_from_xls(keystr, full_fn):
    '''
    Get the filters from ITABLE_FILTER.xlsx
    '''
    # full_fn = os.path.join(
    #     current_app.instance_path, 
    #     settings.PATH_PUBDATA, 
    #     keystr, fn
    # )
    if not os.path.exists(full_fn):
        # try the xls file
        return []

    # load the data file
    import pandas as pd
    xls = pd.ExcelFile(full_fn)
    # load the Filters tab
    sheet_name = 'Filters'
    dft = xls.parse(sheet_name)

    # build Filters data
    ft_list = []
    for col in dft.columns[1:]:
        display_name = col
        tmp = dft[col].tolist()
        # the first line of dft is the column name / attribute name
        ft_attr = '%s' % tmp[0]

        if ft_attr == 'nan': continue

        # the second line of dft is the filter type: radio or select
        ft_type = ("%s" % tmp[1]).strip().lower()
        # get those rows not NaN, which means containing option
        ft_opts = dft[col][~dft[col].isna()].tolist()[3:]
        # get the default label
        ft_def_opt_label = ("%s" % tmp[2]).strip()

        # set the default option
        ft_item = {
            'display_name': display_name,
            'type': ft_type,
            'attr': ft_attr,
            'value': 0,
            'values': [{
                "display_name": ft_def_opt_label,
                "value": 0,
                "sql_cond": "{$col} is not NULL",
                "default": True
            }]
        }
        # build ae_name dict
        for i, ft_opt in enumerate(ft_opts):
            ft_opt = str(ft_opt)
            # remove the white space
            ft_opt = ft_opt.strip()
            ft_item['values'].append({
                "display_name": ft_opt,
                "value": i+1,
                "sql_cond": "{$col} like '%%%s%%'" % ft_opt,
                "default": False
            })

        ft_list.append(ft_item)
            
        print('* parsed ft_attr %s with %s options' % (ft_attr, len(ft_opts)))
    print('* created ft_list %s filters' % (len(ft_list)))

    return ft_list


def get_studies_included_in_ma(keystr, cq_abbr, paper_dict=None):
    '''
    Get the studies which are included in MA
    '''
    project = dora.get_project_by_keystr(keystr)
    if project is None:
        return None

    if paper_dict is None:
        # create a paper_dict
        papers = dora.get_papers_of_included_sr(project.project_id)
        paper_dict = {}
        for p in papers:
            paper_dict[p.pid] = p

    # get all oc of this project
    ocs = dora.get_extracts_by_keystr_and_cq(
        keystr,
        cq_abbr
    )

    # check each outcome
    # to fill this stat object
    stat = {
        'f3': {
            'pids': [],
            'rcts': [],
            'n': 0
        }
    }
    for oc in ocs:
        # 2022-01-19: fix the number issue
        # the itable should be excluded from the counting
        if oc.oc_type == 'itable':
            continue

        # check papaer extracted in this outcome
        for pid in oc.data:
            # 2022-01-17 fix the MA>SR issue
            # need to check whether this pid exists in papers
            if pid not in paper_dict:
                # which means this extraction is not linked with a paper,
                # maybe due to import issue or pid update.
                # so, just skip this
                continue

            # get the data
            p = oc.data[pid]

            if p['is_selected']:
                if pid in stat['f3']['pids']:
                    # this pid has been counted
                    pass
                else:
                    stat['f3']['n'] += 1
                    stat['f3']['pids'].append(pid)

                    # check the ctid
                    if pid in paper_dict:
                        # rct_id = paper_dict[pid]['ctid']
                        rct_id = paper_dict[pid].get_rct_id()
                        if rct_id not in stat['f3']['rcts']:
                            stat['f3']['rcts'].append(rct_id)
                    else:
                        # what???
                        # if this pid not in paper_dict
                        # which means the rct info is missing
                        print('* ERROR missing %s in paper_dict' % (
                            pid
                        ))
                        pass

            else:
                # this paper is extracted but not selected yet.
                pass
    try:
        print("* generated stat_f3 %s/%s included in MA" % (
            stat['f3']['n'],
            len(paper_dict)
        ))
    except:
        pass

    return stat


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


def __get_val(v, default_value=''):
    '''
    Helper function for getting values from df cell
    '''
    if pd.isna(v): 
        return default_value
    return str(v).strip()


def __get_int_val(v, default_value=''):
    '''
    Helper function for getting the int value
    '''
    if pd.isna(v): 
        return default_value
    try:
        val = str(int(float(v)))
        return val
    except:
        return v


def __get_col(row, col):
    '''
    Helper function for getting values from df row by column name
    '''
    if col not in row.keys():
        return None
    
    else:
        return row[col]


def __get_pid(v):
    '''
    Helper function for pid
    '''
    try:
        pid = str(int(float(v)))
        return pid
    except:
        return v


def __cie_imp2val(v):
    '''
    Helper function for the cie importance
    '''
    if v is None: return '0'
    _v = '%s' % v
    _v = _v.lower().strip()

    if _v == 'critical': 
        return '2'

    elif _v == 'important':
        return '1'

    else:
        return v