import os
import json
import math
import hashlib
import pathlib
import datetime
from collections import OrderedDict

import numpy as np
import pandas as pd

from .data_helper import gen_rscript
from .data_helper import run_rscript

from lnma.settings import *

from .rpadapter import _netmeta_trans_netcha
from .rpadapter import _netmeta_trans_netplt
from .rpadapter import _netmeta_trans_league_r
from .rpadapter import _netmeta_trans_forest
from .rpadapter import _netmeta_trans_pscore

from .rpadapter import _bugsnet_trans_netcha
from .rpadapter import _bugsnet_trans_netplt
from .rpadapter import _bugsnet_trans_league
from .rpadapter import _bugsnet_trans_forest
from .rpadapter import _bugsnet_trans_scrplt
from .rpadapter import _bugsnet_trans_rksucra

from .rpadapter import _gemtc_trans_forest
from .rpadapter import _gemtc_trans_league
from .rpadapter import _gemtc_trans_netcha
from .rpadapter import _gemtc_trans_netplt

from .rpadapter import _dmetar_trans_scrplt
from .rpadapter import _dmetar_trans_rksucra

def analyze(rs, cfg):
    '''
    Analylze the rs according to cfg, which includes:

    - backend: freq, bayes
    - input_format: ET, HRLU

    The HRLU format could be processed by the gemtc or dmetar.
    The ET format could be processed by the Bugsnet
    '''
    # generate
    submission_id = hashlib.sha224(str(datetime.datetime.now()).encode('utf8')).hexdigest()[:12].upper()
    subtype = 'nma_' + cfg['backend'] + '_' + cfg['input_format']
    fn_rscript = TPL_FN['rscript'].format(submission_id=submission_id, subtype=subtype)

    params = {
        'submission_id': submission_id,
        'subtype': subtype,

        'fn_rscript': fn_rscript,
        'fn_csvfile': TPL_FN['csvfile'].format(**{
            'subtype': subtype, 'submission_id': submission_id
        }),
        'fn_jsonret': TPL_FN['jsonret'].format(**{
            'subtype': subtype, 'submission_id': submission_id
        }),
    }

    # put all the configs into param
    for key in cfg:
        params[key] = cfg[key]

    print(params)

    # get result from other analyzer
    if cfg['backend'] == 'bayes':
        if cfg['input_format'] == INPUT_FORMATS_ET or \
           cfg['input_format'] == INPUT_FORMAT_NMA_RAW_ET:
            ret = analyze_raw_by_bugsnet(rs, params)

        elif cfg['input_format'] == INPUT_FORMATS_FTET:
            ret = analyze_raw_by_bugsnet(rs, params)

        elif cfg['input_format'] == INPUT_FORMATS_HRLU or \
             cfg['input_format'] == INPUT_FORMAT_NMA_PRE_SMLU:
            ret = analyze_pre_by_gemtc(rs, params)

        else:
            ret = analyze_raw_by_bugsnet(rs, params)

    elif cfg['backend'] == 'freq':
        if cfg['input_format'] == INPUT_FORMATS_ET or \
           cfg['input_format'] == INPUT_FORMAT_NMA_RAW_ET:
            ret = analyze_raw_by_freq(rs, params)

        elif cfg['input_format'] == INPUT_FORMATS_FTET:
            ret = analyze_raw_by_freq(rs, params)

        elif cfg['input_format'] == INPUT_FORMATS_HRLU or \
             cfg['input_format'] == INPUT_FORMAT_NMA_PRE_SMLU:
            ret = analyze_pre_by_freq(rs, params)

        else:
            ret = analyze_pre_by_freq(rs, params)
    else:
        ret = {}

    return ret


def analyze_raw_by_bugsnet(rs, params):
    '''
    Bayesian NMA
    
    The input `rs` must be in the following format:

        study, treat, event, total

    Or:

        study, treat, event, total, follow-up time

    The input params must include:

        measure_of_effect
        reference_treatment
        which_is_better
    '''
    # prepare the r script
    subtype = params['subtype']

    full_filename_rscript = os.path.join(TMP_FOLDER, params['fn_rscript'])
    full_filename_csvfile = os.path.join(TMP_FOLDER, params['fn_csvfile'])
    full_filename_jsonret = os.path.join(TMP_FOLDER, params['fn_jsonret'])
    
    r_params = {
        # these three are for netmeta (netrank)
        'is_fixed': 'TRUE' if params['fixed_or_random'] == 'fixed' else 'FALSE',
        'is_random': 'TRUE' if params['fixed_or_random'] == 'random' else 'FALSE',

        # the followings are for BUGSnet
        'measure_of_effect_to_link': R_BUGSNET_MEASURE2LINK[params['measure_of_effect']],
        'model_param_time_column': 'time = "time",' if params['measure_of_effect'] == 'hr' else '',
        'sucra_largerbetter': 'TRUE' if params['which_is_better'] == 'big' else 'FALSE',
    }
    r_params.update(params)

    # output data
    df = pd.DataFrame(rs)
    df.to_csv(full_filename_csvfile, index=False)

    # generate an R script for producing the results
    gen_rscript(
        RSCRIPT_TPL_FOLDER, 
        RSCRIPT_TPL[subtype], 
        params['fn_rscript'], 
        r_params
    )

    # run the R script
    run_rscript(params['fn_rscript'])

    # transform the output json to front end format
    jrst = json.load(open(full_filename_jsonret))
    ret = {
        'submission_id': params['submission_id'],
        'params': params,
        'success': True,
        'data': {
            'netplt': _bugsnet_trans_netplt(jrst['network_char']['comparison'], params),
            'league': _bugsnet_trans_league(jrst['league'], params),
            'tmrank': _bugsnet_trans_rksucra(jrst['sucraplot'], params),

            'scrplt': _bugsnet_trans_scrplt(jrst['sucraplot'], params),
            'netcha': _bugsnet_trans_netcha(jrst['network_char']['network'], params),
            'forest': _bugsnet_trans_forest(jrst['league'], params),
        }
    }

    return ret


def analyze_pre_by_gemtc(rs, params):
    '''
    Bayesian NMA for pre data
    
    The input `rs` must be:

        'study', 't1', 't2', 'hr', 'upperci', 'lowerci'

    The `hr` could be `TE` or `sm`

    The input params must include:

        measure_of_effect
        reference_treatment
        which_is_better
        fixed_or_random
    
    optional param:

        mtc_model_n_chain
    '''
    # prepare the r script
    subtype = params['subtype']

    # prepare the file names
    full_filename_rscript = os.path.join(TMP_FOLDER, params['fn_rscript'])
    full_filename_csvfile = os.path.join(TMP_FOLDER, params['fn_csvfile'])
    full_filename_jsonret = os.path.join(TMP_FOLDER, params['fn_jsonret'])

    # prepare the other parameters used in R script
    r_params = {
        'mtc_model_n_chain': params['mtc_model_n_chain'] if 'mtc_model_n_chain' in params else 4,
        'sucra_lower_is_better': 'TRUE' if params['which_is_better'] == 'big' else 'FALSE',
    }
    r_params.update(params)

    # convert data into dataframe
    df = pd.DataFrame(rs)

    # check the columns
    if 'TE' not in df.columns and 'hr' in df.columns:
        df['TE'] = np.log(df['hr'])
        print('* fixed TE column with hr')

    if 'TE' not in df.columns and 'sm' in df.columns:
        df['TE'] = np.log(df['sm'])
        print('* fixed TE column with sm')

    if 'seTE' not in df.columns:
        f_ci2se = lambda r: (math.log(r['upperci']) - math.log(r['lowerci'])) / 3.92
        df['seTE'] = df.apply(lambda r: round(f_ci2se(r), 4), axis=1)
        print('* fixed seTE column with upper and lower ci')

    # transform the dataset
    rs2 = []
    for idx, row in df.iterrows():
        # add the treatment 1
        rs2.append({
            'diff': row['TE'],
            'std.err': row['seTE'],
            'treatment': row['t1'],
            'study': row['study']
        })
        # add the treatment 2
        rs2.append({
            'diff': None,
            'std.err': None,
            'treatment': row['t2'],
            'study': row['study']
        })

    # output the rs2 as csv
    df2 = pd.DataFrame(rs2)
    df2.to_csv(full_filename_csvfile, index=False)

    # generate an R script for producing the results
    gen_rscript(
        RSCRIPT_TPL_FOLDER, 
        RSCRIPT_TPL[subtype], 
        params['fn_rscript'], 
        r_params
    )

    # run the R script
    run_rscript(params['fn_rscript'])

    # transform the output json to front end format
    jrst = json.load(open(full_filename_jsonret))
    rs_sucra = []

    ret = {
        'submission_id': params['submission_id'],
        'params': params,
        'success': True,
        'data': {
            'netcha': _gemtc_trans_netcha(jrst['model'], params),
            'netplt': _gemtc_trans_netplt(jrst['model'], params),
            'forest': _gemtc_trans_forest(jrst['expleague'], params),
            'league': _gemtc_trans_league(jrst['expleague'], params),
            'scrplt': _dmetar_trans_scrplt(jrst, params),
            'tmrank': _dmetar_trans_rksucra(jrst, params)
        }
    }

    return ret


def analyze_raw_by_freq(rs, params):
    '''
    Frequentist NMA
    
    The input `rs` must be in the following format:

        study, treat, event, total

    Or:

        study, treat, event, total, follow-up time

    The input params must include:

        measure_of_effect
        reference_treatment
        which_is_better
        format_converted
    '''
    
    # prepare the r script
    subtype = params['subtype']

    # prepare the file names
    full_filename_rscript = os.path.join(TMP_FOLDER, params['fn_rscript'])
    full_filename_csvfile = os.path.join(TMP_FOLDER, params['fn_csvfile'])
    full_filename_jsonret = os.path.join(TMP_FOLDER, params['fn_jsonret'])

    # prepare the other parameters used in R script
    r_params = {
        'is_fixed': 'TRUE' if params['fixed_or_random'] == 'fixed' else 'FALSE',
        'is_random': 'TRUE' if params['fixed_or_random'] == 'random' else 'FALSE',
        'small_values_are': 'good' if params['which_is_better'] == 'small' else 'bad'
    }
    r_params.update(params)

    # convert to dataframe
    df = pd.DataFrame(rs)

    if 'format_converted' in params:
        # output data for netmeta pairwise
        # this means this rs has been converted to t1e1n1 - t2e2n2 format
        df.to_csv(full_filename_csvfile, index=False)

    else:
        # output data for netmeta pairwise
        rs2 = OrderedDict()
        for idx, row in df.iterrows():
            # add the treatment 1
            study = row['study']
            
            if study not in rs2: rs2[study] = { 'study': study }
            if 'treat1' not in rs2[study]:
                rs2[study]['treat1'] = row['treat']
                rs2[study]['event1'] = row['event']
                rs2[study]['n1'] = row['total']
            elif 'treat2' not in rs2[study]:
                rs2[study]['treat2'] = row['treat']
                rs2[study]['event2'] = row['event']
                rs2[study]['n2'] = row['total']
            else:
                pass
        
        rs2 = list(rs2.values())

        # output the rs2 as csv
        df2 = pd.DataFrame(rs2)
        df2.to_csv(full_filename_csvfile, index=False)


    # generate an R script for producing the results
    gen_rscript(
        RSCRIPT_TPL_FOLDER, 
        RSCRIPT_TPL[subtype], 
        params['fn_rscript'], 
        r_params
    )

    # run the R script
    run_rscript(params['fn_rscript'])

    # transform the output json to front end format
    jrst = json.load(open(full_filename_jsonret))
    rs_sucra = []

    ret = {
        'submission_id': params['submission_id'],
        'params': params,
        'success': True,
        'data': {
            'netcha': _netmeta_trans_netcha(jrst['nma'], params),
            'netplt': _netmeta_trans_netplt(jrst['mynetplt'], params),
            'forest': _netmeta_trans_forest(jrst['myforest'], params),
            'league': _netmeta_trans_league_r(jrst['myleaguetb'], params),
            'psrank': _netmeta_trans_pscore(jrst, params)
        }
    }

    return ret


def analyze_pre_by_freq(rs, params):
    '''
    Frequentist NMA for pre-calculated data
    
    The input `rs` must be in the following format:

        study, t1, t2, sm, lowerci, upperci

    The input params must include:

        measure_of_effect
        reference_treatment
        which_is_better
    '''

    # prepare the r script
    subtype = params['subtype']

    # prepare the file names
    full_filename_rscript = os.path.join(TMP_FOLDER, params['fn_rscript'])
    full_filename_csvfile = os.path.join(TMP_FOLDER, params['fn_csvfile'])
    full_filename_jsonret = os.path.join(TMP_FOLDER, params['fn_jsonret'])

    # prepare the other parameters used in R script
    r_params = {
        'is_fixed': 'TRUE' if params['fixed_or_random'] == 'fixed' else 'FALSE',
        'is_random': 'TRUE' if params['fixed_or_random'] == 'random' else 'FALSE',
        'small_values_are': 'good' if params['which_is_better'] == 'small' else 'bad'
    }
    r_params.update(params)

    # convert to dataframe
    df = pd.DataFrame(rs)
    df.to_csv(full_filename_csvfile, index=False)

    # generate an R script for producing the results
    gen_rscript(
        RSCRIPT_TPL_FOLDER, 
        RSCRIPT_TPL[subtype], 
        params['fn_rscript'], 
        r_params
    )

    # run the R script
    run_rscript(params['fn_rscript'])

    # transform the output json to front end format
    jrst = json.load(open(full_filename_jsonret))
    rs_sucra = []

    ret = {
        'submission_id': params['submission_id'],
        'params': params,
        'success': True,
        'data': {
            'netcha': _netmeta_trans_netcha(jrst['nma'], params),
            'netplt': _netmeta_trans_netplt(jrst['mynetplt'], params),
            'league': _netmeta_trans_league_r(jrst['myleaguetb'], params),
            'forest': _netmeta_trans_forest(jrst['myforest'], params),
            'psrank': _netmeta_trans_pscore(jrst, params)
        }
    }

    return ret
