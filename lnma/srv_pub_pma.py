import os
import pandas as pd

from tqdm import tqdm
import numpy as np

from flask import current_app

from lnma.analyzer import rpy2_pwma_analyzer as pwma_analyzer
from lnma import dora, srv_analyzer
from lnma import util
from lnma import ss_state
from lnma import settings
from lnma import db

from lnma import srv_paper


def get_graph_pma_data_from_db(keystr, cq_abbr):
    '''
    Get the graph data for PWMA
    '''
    if keystr == 'IO' and cq_abbr == 'default': 
        # for the IO project, the calculation is different
        return get_sof_pma_data_from_db_IO(cq_abbr, False)

    return get_pma_by_cq(keystr, cq_abbr, 'plots')


def get_sof_pma_data_from_db(keystr, cq_abbr, is_calc_pma=True):
    '''
    Get the SoF table data for PWMA
    '''
    if keystr == 'IO' and cq_abbr == 'default': 
        # for the IO project, the calculation is different
        return get_sof_pma_data_from_db_IO(cq_abbr, is_calc_pma)

    # for most cases:
    return get_pma_by_cq(keystr, cq_abbr, 'sof')


def get_pma_by_cq(keystr, cq_abbr="default", included_in='sof'):
    '''
    Get the pma results

    included_in: sof or plots
    '''
    # get basic information
    project = dora.get_project_by_keystr(keystr)

    if project is None:
        return None

    papers = srv_paper.get_included_papers_by_cq(
        project.project_id, cq_abbr
    )
    print('* found %s papers included in %s-%s' % (
        len(papers), keystr, cq_abbr
    ))

    # make a dictionary for lookup
    paper_dict = {}
    rs = []
    for paper in papers:
        paper_dict[paper.pid] = paper
        rs.append(paper.as_quite_simple_dict())

    # Then, we need to build the oc_list for the navigation
    extracts = dora.get_extracts_by_keystr_and_cq_and_oc_type(
        keystr, 
        cq_abbr, 
        'pwma'
    )
    print('* found %s extracts defined in %s-%s' % (
        len(extracts), keystr, cq_abbr
    ))

    # then create oc_dict
    oc_dict = {}
    for extract in tqdm(extracts):
        abbr = extract.abbr

        # skip not included in sof or plots
        cond = 'included_in_%s' % included_in
        if cond in extract.meta:
            if extract.meta[cond] == 'yes':
                pass
            else:
                continue
        else:
            continue

        print('* analyzing %s' % (
            extract.get_repr_str()
        ))

        # put the oc into dict
        results = srv_analyzer.get_pma(
            extract, 
            paper_dict, 
            is_skip_unselected=True
        )

        # 2022-03-12: update the extract
        # update the extract cie
        if 'certainty' not in extract.meta:
            # need to fix this for this outcome
            extract.meta['certainty'] = extract.get_certainty()

            # update this extract with n
            extract = dora.update_extract_meta(
                extract.project_id,
                extract.oc_type,
                extract.abbr,
                extract.meta
            )
            
            print('* fixed missing certainty in extract: %s' % (
                extract.get_repr_str()
            ))

        # 2022-02-19: fix the missing CIE
        extract.meta['certainty']['cie'] = util.calc_pma_cie(
            extract.meta['certainty'],
            settings.CIE_PWMA_COLUMNS
        )

        # the return obj for this oc
        oc_dict[abbr] = {
            'extract': extract.as_very_simple_dict(),
            
            # use the sm as the key, since there may be more results
            # for example, HR, RR, OR, INCD
            'results': results,
        }
    
    ret = {
        'rs': rs,
        'oc_dict': oc_dict
    }

    return ret


def get_sof_pma_data_from_db_IO(cq_abbr="default", is_calc_pma=True):
    '''
    The SoF Table of PWMA DATA for IO project
    '''
    # First, get all extracts of pwma
    # But for other projects, need to double check the input type
    keystr = 'IO'
    project = dora.get_project_by_keystr(keystr)
    # papers = dora.get_papers_by_stage(
    #     project.project_id, 
    #     ss_state.SS_STAGE_INCLUDED_SR,
    #     cq_abbr
    # )
    papers = srv_paper.get_included_papers_by_cq(
        project.project_id, cq_abbr
    )
    print('* found %s papers included in %s-%s' % (
        len(papers), 'IO', cq_abbr
    ))
    
    # make a dictionary for lookup
    paper_dict = {}
    for paper in papers:
        paper_dict[paper.pid] = paper

    # Then, we need to build the oc_list for the navigation
    extracts = dora.get_extracts_by_keystr_and_cq_and_oc_type(
        keystr, 
        cq_abbr, 
        'pwma'
    )
    print('* found %s extracts defined in %s-%s' % (
        len(extracts), 'IO', cq_abbr
    ))

    oc_dict = {}
    for extract in extracts:
        abbr = extract.abbr
        # put the oc into dict
        oc_dict[abbr] = {
            'extract': extract.as_very_simple_dict()
        }

    # the measures
    sms = ['OR', 'RR', 'INCD']
    # the grades for AEs
    grades = ['GA', 'G3H', 'G5N']
    # columns for int type
    int_cols = [
        'GA_Et', 'GA_Nt', 'GA_Ec', 'GA_Nc',
        'G34_Et', 'G34_Ec',
        'G3H_Et', 'G3H_Ec',
        'G5N_Et', 'G5N_Ec'
    ]

    # a helper function
    def __notna(v):
        if v is None:
            return False
        # convert to a temp 
        t = '%s' % v
        t = t.strip().lower()
        # just use exception to judge if it
        try:
            int(t)
            return True
        except:
            return False

    # a helper function
    def __notzero(v):
        return v != 0

    # a helper function to make sure the value is int if possible
    def __int(v):
        try: return int(v)
        except: return v

    # a helper function to make sure the value is good for pwma
    def __is_pwmable(r, gr):
        # the first condition is all numbers are not null
        f1 = __notna(r['%s_Et'%gr]) and __notna(r['GA_Nt']) and \
             __notna(r['%s_Ec'%gr]) and __notna(r['GA_Nc'])
            
        # the second condition is not both zero
        f2 = (__notna(r['%s_Et'%gr]) and __notzero(r['%s_Et'%gr])) or \
             (__notna(r['%s_Ec'%gr]) and __notzero(r['%s_Ec'%gr]))

        # final combine two
        return f1 and f2

    # Second, build the oc_dict
    rs = []
    for extract in tqdm(extracts):

        # check if this extract is excluded from graph / sof
        if is_calc_pma:
            # for sof
            if extract.meta['included_in_sof'] == 'no':
                # which means not to be display in softable
                continue
        else:
            # for graph
            if extract.meta['included_in_plots'] == 'no':
                # which means we don't display this on the website in graph
                continue

        # get short name for the group, cate, oc
        oc_abbr = extract.abbr
        oc_group = extract.meta['group']
        oc_cate = extract.meta['category']
        oc_name = extract.meta['full_name']

        # build the dataframe for this outcome / extract
        oc_rs = []

        # the extract['data'] con
        for pid in extract.data:
            # get the extraction 
            ext_pp_data = extract.data[pid]

            # if this paper is not selected, just skip
            if not ext_pp_data['is_selected']: continue

            # get the paper
            if pid in paper_dict:
                paper = paper_dict[pid]
            else:
                # which means this study is not included in SR
                # or was included in SR but has been removed?
                continue

            # OK, this study is selected, put the extracted result
            # shallow copy is good enough for this case
            # we could make a list to contain all the records
            # the second item is the author name suffix
            # for each paper, there must be one main record
            # sometimes, there is also multi-arm
            ext_pp_rs = [
                [ext_pp_data['attrs']['main']['g0'].copy(), '']
            ]
            for arm_idx in range(ext_pp_data['n_arms'] - 2):
                ext_pp_rs.append(
                    [ext_pp_data['attrs']['other'][arm_idx]['g0'].copy(), ' Comp %s' % (arm_idx + 2)]
                )
            
            # then, we just need to run the calculation once
            for item in ext_pp_rs:
                r = item[0]
                
                # make sure the data type is int
                for col in int_cols:
                    if col in r:
                        r[col] = __int(r[col])
                    else:
                        r[col] = ''
                
                # add more attributes
                # r['has_GA']  = __notna(r['GA_Et'])
                # r['has_G34'] = __notna(r['G34_Et'])
                # r['has_G3H'] = __notna(r['G3H_Et'])
                # r['has_G5N'] = __notna(r['G5N_Et'])

                # first, the has_XX is defined as whether could use this record for basic
                # we use a strict condition, as same as the prim analysis
                r['has_GA']  = __is_pwmable(r, 'GA')
                r['has_G34'] = __is_pwmable(r, 'G34')
                r['has_G3H'] = __is_pwmable(r, 'G3H')
                r['has_G5N'] = __is_pwmable(r, 'G5N')

                # add flag for incidence analysis
                # to conduct incidence analysis, 2 columns are required
                # E, N
                # so the has_XX_incd is a little different from the pwmable
                r['has_GA_incd']  = __notna(r['GA_Et']) and __notna(r['GA_Nt'])
                r['has_G34_incd'] = __notna(r['G34_Et']) and __notna(r['GA_Nt'])
                r['has_G3H_incd'] = __notna(r['G3H_Et']) and __notna(r['GA_Nt'])
                r['has_G5N_incd'] = __notna(r['G5N_Et']) and __notna(r['GA_Nt'])

                # add flag for prim+cumu analysis
                # to conduct prim+cumu analysis, 4 columns are required
                # Et, Nt, Ec, Nc
                r['has_GA_prim']  = __is_pwmable(r, 'GA')
                r['has_G34_prim'] = __is_pwmable(r, 'G34')
                r['has_G3H_prim'] = __is_pwmable(r, 'G3H')
                r['has_G5N_prim'] = __is_pwmable(r, 'G5N')

                # the author name is the combination of paper short name and suffix
                r['author'] = paper.get_short_name() + item[1]
                r['year'] = paper.get_year()
                r['pid'] = paper.pid
                r['oc_abbr'] = oc_abbr
                r['oc_cate'] = oc_cate
                r['oc_name'] = oc_name
                r['oc_group'] = oc_group

                rs.append(r)
                oc_rs.append(r)

        # now do the PWMA
        if not is_calc_pma: continue

        # create a new oc
        oc_dict[oc_abbr]['results'] = {}

        # create a temp dataframe for this outcome
        dft = pd.DataFrame(oc_rs)

        if dft.empty:
            # which means no study here
            # just go to check next
            continue

        for grade in grades:
            dftt = dft[dft['has_%s' % grade]==True]

            oc_dict[oc_abbr]['results'][grade] = {
                'grade': grade,
                'stus': dftt['author'].values.tolist(),
                'Et': int(dftt['%s_Et' % grade].sum()),
                'Nt': int(dftt['GA_Nt'].sum()),
                'Ec': int(dftt['%s_Ec' % grade].sum()),
                'Nc': int(dftt['GA_Nc'].sum()),
                'result': {}
            }

            # prepare the dataset for PWMA
            # the `ds` will looks like a matrix:
            # [
            #    [ Et, Nt, Ec, Nc, author1 ],
            #    [ Et, Nt, Ec, Nc, author2 ],
            #    ...
            # ]
            # this `ds` is prepared the pymeta package
            # the GA_Nt and GA_Nc are shared in all grades
            ds = []
            for idx, r in dftt.iterrows():
                Et = r['%s_Et' % grade]
                Nt = r['GA_Nt']
                Ec = r['%s_Ec' % grade]
                Nc = r['GA_Nc']
                author = r['author']

                if not util.is_pwmable(Et, Nt, Ec, Nc):
                    # this record is not good for pwma
                    continue

                # if Et == 0: 
                #     Et = 0.4
                #     Nt += Et
                # if Ec == 0: 
                #     Ec = 0.4
                #     Nc += Ec

                # convert data to PythonMeta Format
                ds.append([
                    Et,
                    Nt,
                    Ec, 
                    Nc,
                    author
                ])

            # for each sm, get the PMA result
            for sm in sms:
                if len(ds) == 0:
                    # this is no records, no need to continue
                    pma_r = None
                    pma_f = None
                
                else:
                    # get the pma result

                    # for INCD incidence
                    if sm == 'INCD':
                        # default 
                        pma_f = None
                        pma_r = None

                        # need to convert the format for this
                        ds_2 = []
                        for v in ds:
                            ds_2.append({
                                'Et': v[0],
                                'Nt': v[1],
                                'Ec': v[2],
                                'Nc': v[3],
                                'study': v[4],
                            })
                        cfg = {
                            "external_val": 0, 
                            "fixed_or_random": "random", 
                            "hakn_adjustment": "FALSE", 
                            "incd_measure_of_effect": "PLOGIT", 
                            "input_format": "PRIM_CAT_RAW", 
                            "internal_val_ec": 0, 
                            "internal_val_et": 0, 
                            "measure_of_effect": "PLOGIT", 
                            "pooling_method": "Inverse", 
                            "prediction_interval": "FALSE", 
                            "sensitivity_analysis": "no", 
                            "smd_estimation_method": "Hedges", 
                            "survival_in_control": 0, 
                            "tau_estimation_method": "DL", 
                            "which_is_better": "lower"
                        }
                        rst_incd = pwma_analyzer.analyze_pwma_cat_raw_incd(
                            ds_2,
                            cfg
                        )

                        if rst_incd is not None:
                            pma_r = {
                                'model': rst_incd['data']['incdma']['model']['random']
                            }

                            pma_r['model'].update(
                                rst_incd['data']['incdma']['heterogeneity']
                            )

                    else:
                            
                        # for OR and RR
                        try:
                            # use Python package to calculate the OR/RR
                            pma_r = pwma_analyzer.get_pma(
                                ds, 
                                datatype="CAT_RAW", 
                                sm=sm, 
                                fixed_or_random='random'
                            )
                            # validate the result, if isNaN, just set None
                            if np.isnan(pma_r['model']['sm']): pma_r = None

                            # pma_f = pwma_analyzer.get_pma(
                            #     ds, datatype="CAT_RAW", 
                            #     sm=sm, fixed_or_random='fixed'
                            # )
                            # if np.isnan(pma_f['model']['sm']): pma_f = None
                            # no enough space, just set to None
                            pma_f = None

                            # use R package to calculate the OR/RR
                            # pma_r = get_pma_by_rplt(ds, datetype="CAT_RAW", sm=sm, fixed_or_random='random')
                            # pma_f = get_pma_by_rplt(ds, datetype="CAT_RAW", sm=sm, fixed_or_random='fixed')
                            
                        except Exception as err:
                            print('* %s: [%s] [%s] [%s]' % (
                                'ISSUE Data cause error'.ljust(25, ' '),
                                oc_name.rjust(35, ' '), 
                                grade.rjust(3, ' '),
                                ds
                            ), err)
                            pma_r = None
                            pma_f = None

                oc_dict[oc_abbr]['results'][grade]['result'][sm] = {
                    'random': pma_r,
                    'fixed': pma_f
                }


    # OK, get the final dictionary
    ret = {
        'rs': rs
    }

    # put the oc_dict if for SoF table
    if is_calc_pma:
        ret['oc_dict'] = oc_dict

    return ret