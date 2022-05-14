from genericpath import exists
import os
import json
from matplotlib.pyplot import flag

from tqdm import tqdm

from flask import current_app

# from lnma.analyzer import rpy2_pwma_analyzer as pwma_analyzer
# from lnma.analyzer import nma_analyzer
# use python analyzer instead of the R
from lnma.analyzer import rpy2_nma_analyzer as nma_analyzer
from lnma import dora, srv_analyzer
from lnma import util
from lnma import ss_state
from lnma import settings
from lnma import db

from lnma import srv_paper


def get_graph_nma_data_from_db(keystr, cq_abbr):
    '''
    Get the NMA graph data
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
        'nma'
    )
    print('* found %s extracts defined in %s-%s' % (
        len(extracts), keystr, cq_abbr
    ))

    # OK, let's check each outcome
    oc_dict = {}
    graph_dict = {}
    failed_extracts = []
    
    for extract in tqdm(extracts):

        # check if included in sof
        if extract.meta['included_in_plots'] != 'yes':
            # this oc is NOT included
            print('* skip extract %s due to NOT_INCLUDED_IN_SOF' % (extract.abbr))
            continue

        print('* analyzing %s' % (
            extract.get_repr_str()
        ))

        # create an oc object for ... what?
        # treat_list = extract.meta['treatments']

        # but the treat_list may not be available
        treat_list = extract._get_nma_treat_list()

        # build rs and cfg
        # cfg = {
        #     # for init analyzer
        #     "backend": extract.meta['analysis_method'],
        #     "input_format": input_format,
        #     "reference_treatment": treat_list[0],
        #     "measure_of_effect": extract.meta['measure_of_effect'],
        #     "fixed_or_random": extract.meta['fixed_or_random'],
        #     "which_is_better": 'small' if extract.meta['which_is_better'] == 'lower' else 'big',

        #     # a special rule for database format
        #     'format_converted': 'yes'
        # }
    
        # get the rs for this oc
        # rscfg = extract.get_raw_rs_cfg(
        #     paper_dict, 
        #     is_skip_unselected=True
        # )
        # rs = rscfg['rs']
        # cfg = rscfg['cfg']

        # update the config for R script
        # cfg['backend'] = extract.meta['analysis_method']
        # cfg['reference_treatment'] = treat_list[0]
        # cfg['input_format'] = input_format

        # the R script use different param
        # cfg["which_is_better"] = 'small' if extract.meta['which_is_better'] == 'lower' else 'big',

        # 2022-02-20: no need to change this,
        # since all the format convert has been done in the model level.
        # in the Extract._get_rs_nma(), the format will be changed automatically.
        # cfg['format_converted'] = 'yes'

        # calc!
        # ret_nma = nma_analyzer.analyze(
        #     rs, 
        #     cfg
        # )
        try:
            results = srv_analyzer.get_nma(
                extract, 
                paper_dict,
                True
            )
        except Exception as err:
            results = None
            rstmsg = str(err)

            failed_extracts.append([
                extract,
                rstmsg
            ])

            print('*'*60)
            print('*'*20 + 'NMA RUNTIME EXCEPTION')
            print('*'*60)
            print(err)

        if results is None:
            continue
        
        else:
            ret_nma = results[0]['rst']

        # put in result
        graph_dict[extract.abbr] = ret_nma


        # put the oc_dict
        # get the input format for selecting template
        oc_datatype = settings.INPUT_FORMATS_HRLU
        if extract.meta['input_format'] == 'NMA_RAW_ET':
            oc_datatype = settings.INPUT_FORMATS_ET

        oc = {
            "oc_method": extract.meta['analysis_method'],
            "oc_abbr": extract.abbr,
            "oc_name": extract.abbr,
            "oc_fullname": extract.meta['full_name'],
            "oc_measures": [extract.meta['measure_of_effect']],
            "oc_datatype": oc_datatype,
            "param": {
                "analysis_method": extract.meta['analysis_method'],
                "fixed_or_random": extract.meta['fixed_or_random'],
                "which_is_better": extract.meta['which_is_better']
            },
            "treat_list": treat_list,
            # just give all information to frontend
            "meta": extract.meta
        }
        oc_dict[extract.abbr] = oc

    ret = {
        'oc_dict': oc_dict,
        'graph_dict': graph_dict
    }

    if len(failed_extracts) == 0:
        print('\n\n\n* GREAT! NO issues during NMA calculation!')

    else:
        print('*'*60)
        print('\n\n\n* TOO BAD! %s issues during NMA calculation!' % (
            len(failed_extracts)
        ))
        for idx, err_ext in enumerate(failed_extracts):
            ext = err_ext[0]
            err = err_ext[1]

            print('* %d Error when analyzing %s' % (idx, ext.get_repr_str()))
            print('* %s' % err)
            print('')

    return ret


def get_sof_nma_data_from_db(keystr, cq_abbr):
    '''
    Get the SoF table data for NMA
    '''

    # for most cases:
    return get_nma_by_cq(keystr, cq_abbr, 'sof')


def get_nma_by_cq(keystr, cq_abbr="default", included_in='sof'):
    '''
    Get the NMA result for SoF table
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
        'nma'
    )
    print('* found %s extracts defined in %s-%s' % (
        len(extracts), keystr, cq_abbr
    ))     

    # then create oc_dict
    oc_dict = {}
    treat_list = []
    failed_extracts = []

    for extract in tqdm(extracts):
        abbr = extract.abbr

        # check if included in sof
        if extract.meta['included_in_sof'] != 'yes':
            # this oc is NOT included
            print('* skip extract %s due to NOT_INCLUDED_IN_SOF' % (abbr))
            continue

        # treatments = extract.get_treatments_in_data()

        print('* analyzing %s' % (
            extract.get_repr_str()
        ))

        try:
            results = srv_analyzer.get_nma(
                extract, 
                paper_dict,
                True
            )
        except Exception as err:
            results = None
            rstmsg = str(err)

            failed_extracts.append([
                extract,
                rstmsg
            ])
            print('*'*60)
            print('*'*20 + 'NMA RUNTIME EXCEPTION')
            print('*'*60)
            print(err)

        if results is None or len(results)<1:
            print('* NO NMA results for extract[%s]' % (
                extract.get_repr_str()
            ))
            continue

        # for league table, we just need the first NMA result
        rst = results[0]['rst']

        # convert the league table to lgtable format
        lgtable = _conv_nmarst_league_to_lgtable(rst)

        # convert the ranks to rktable format
        # flag_reverse = extract.meta['which_is_better'] == 'higher' or \
        #             extract.meta['which_is_better'] == 'bigger' or \
        #             extract.meta['which_is_better'] == 'big'
        # in fact, the rank table should always be like this
        flag_reverse = True
        rktable = _conv_nmarst_rank_to_rktable(
            rst,
            reverse=flag_reverse
        )

        # get the cetable?
        cetable = {}

        # get the trttable
        trtable = extract.get_nma_trtable()

        # update the SoF-level treat list
        for treat_name in trtable:
            if treat_name not in treat_list:
                treat_list.append(treat_name)

        # OK, bind the result
        oc_dict[abbr] = {
            'extract': extract.as_very_simple_dict(),
            
            # the league table
            'lgtable': lgtable,

            # the rank table
            'rktable': rktable,

            # the cie table
            'cetable': cetable,

            # the treat table 
            'trtable': trtable
        }

    # before returning, sort the treat_list
    treat_list.sort()

    # last, add CIE patch
    oc_dict = _add_cie_patch(keystr, cq_abbr, oc_dict)

    ret = {
        'treat_list': treat_list,
        'oc_dict': oc_dict
    }

    if len(failed_extracts) == 0:
        print('\n\n\n* GREAT! NO issues during NMA calculation!')

    else:
        print('*'*60)
        print('\n\n\n* TOO BAD! Some issues during NMA calculation!')
        for err_ext in failed_extracts:
            ext = err_ext[0]
            err = err_ext[1]

            print('* Error when analyzing %s' % ext.get_repr_str())
            print('* %s' % err)
            print('')

    return ret


def parse_evmap_data_from_json(j):
    '''
    Parse the Evidence Map data from the calculation result

    The `j` is the return of get_sof_nma_by_cq()

    The evmap data focus on the evidence visualization,
    So it summarizes the results of all treatments for visualization.
    The selection is a treatment-based effect

    The effects are defined as follows:
    effects = {
        3: 'significant benefit',
        2: 'no significant effect',
        1: 'significant harm',
        0: 'na'
    }
    '''
    # the final result is a bout treatment
    treat_dict = {}

    # get all information for this treat in each result
    for abbr in j['oc_dict']:
        oc = j['oc_dict'][abbr]
        # check all par
        for cmprt in oc['lgtable']:
            for treat in oc['lgtable'][cmprt]:
                # skip the same, no need to compare
                if treat == cmprt: continue

                # try to locate this cmprt first
                if cmprt not in oc['cetable']: continue

                # try to get the treat
                if treat not in oc['cetable'][cmprt]: continue

                # get the certainty
                cie = oc['cetable'][cmprt][treat]['cie']

                # get the values for effect
                sm = oc['lgtable'][cmprt][treat]['sm']
                lw = oc['lgtable'][cmprt][treat]['lw']
                up = oc['lgtable'][cmprt][treat]['up']
                which_is_better = oc['extract']['meta']['which_is_better']

                # get the effect
                effect = _get_effect(
                    sm,
                    lw,
                    up,
                    which_is_better
                )

                # create a record if not exists yet
                if treat not in treat_dict:
                    treat_dict[treat] = {
                        'rs': []
                    }

                # save this record
                treat_dict[treat]['rs'].append({
                    'cie': cie,
                    'effect': effect,
                    'comparator': cmprt,
                    'treatment': treat,
                    'oc_abbr': abbr
                })

    # bind the treat_dict to j
    j['treat_dict'] = treat_dict

    return j


def _get_effect(sm, lw, up, which_is_better='lower'):
    '''
    Get the effect value
    effects = {
        3: 'significant benefit',
        2: 'no significant effect',
        1: 'significant harm',
        0: 'na'
    }
    '''
    if sm == 1:
        return 2

    elif lw < 1 and up > 1:
        return 2

    elif sm > 1:
        if which_is_better == 'higher':
            return 3
        else:
            return 1

    elif sm < 1:
        if which_is_better == 'higher':
            return 1
        else:
            return 3
    
    else:
        return 0    


def _add_cie_patch(keystr, cq_abbr, oc_dict):
    '''
    Add patch to NMA result
    '''
    # try to read the file
    fn = 'CIE.csv'
    full_fn = os.path.join(
        current_app.instance_path, 
        settings.PUBLIC_PATH_PUBDATA, 
        keystr,
        cq_abbr,
        fn
    )

    if not os.path.exists(full_fn):
        # ok, no such file
        print('* No CIE patch for %s-%s')
        return oc_dict

    # try to build a dict from full name to abbr
    ocfn2abbr = {}
    for abbr in oc_dict:
        ocfn = oc_dict[abbr]['extract']['meta']['full_name']
        ocfn2abbr[ocfn] = abbr

    # load csv
    import csv

    def _int_cie(v):
        '''
        A helper for cie int value, default is 0
        '''
        try:
            return int(v)
        except:
            return 0

    with open(full_fn, 'r', encoding='utf-8-sig') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=',')
        for row in csv_reader:
            c = row['comparator']
            t = row['treatment']
            ocfn = row['name']

            if ocfn not in ocfn2abbr:
                # which means this oc not defined yet?
                continue
            
            oc_abbr = ocfn2abbr[ocfn]

            # check comparator
            if c not in oc_dict[oc_abbr]['cetable']:
                oc_dict[oc_abbr]['cetable'][c] = {}

            # check treatment
            if t not in oc_dict[oc_abbr]['cetable'][c]:
                oc_dict[oc_abbr]['cetable'][c][t] = {}

            # put the values
            for k in row:
                if k in ['category', 'name', 'comparator', 'treatment']:
                    continue
                # make sure the value type is int
                oc_dict[oc_abbr]['cetable'][c][t][k] = _int_cie('%s'%row[k])

            # no matter cie is there or not
            # update cie
            # then get the final cie
            oc_dict[oc_abbr]['cetable'][c][t]['cie'] = util.calc_nma_cie(
                oc_dict[oc_abbr]['cetable'][c][t],
                settings.CIE_NMA_COLUMNS
            )

    return oc_dict
    

def _conv_nmarst_league_to_lgtable(nmarst):
    '''
    Convert NMA result league to lgtable format
    '''
    # get the league table data
    league_table = nmarst['data']['league']

    # get all cols
    lgt_cols = league_table['cols']
    lgtable = {}
    for lgt_rs in league_table['tabledata']:
        lgt_r = lgt_rs['row']
        # create a new comparator row
        lgtable[lgt_r] = {}

        for j, lgt_c in enumerate(lgt_cols):
            lgt_cell = {
                "sm": lgt_rs['stat'][j],
                'lw': lgt_rs['lci'][j],
                'up': lgt_rs['uci'][j]
            }
            # create a new treat col
            lgtable[lgt_r][lgt_c] = lgt_cell

    return lgtable


def _conv_nmarst_rank_to_rktable(nmarst, reverse=True):
    '''
    Convert NMA result to rktable format
    '''
    rank_name = 'psrank'
    if rank_name not in nmarst['data']:
        rank_name = 'tmrank'

    rank_data = nmarst['data'][rank_name]

    # sort the ranks
    ranks = sorted(rank_data['rs'], 
        key=lambda v: v['value'],
        reverse=reverse)

    rktable = {}
    for i, r in enumerate(ranks):
        # put the ranks in the sm
        rktable[r['treat']] = {
            'rank': i + 1,
            'score': r['value']
        }

    return rktable

