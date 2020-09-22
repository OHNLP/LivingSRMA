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

from .rpadapter import _bugsnet_trans_netplt
from .rpadapter import _bugsnet_trans_league
from .rpadapter import _bugsnet_trans_rksucra


def analyze(rs, cfg):
    '''
    Analylze the rs according to cfg, which includes:

    - backend: freq, bayes
    - input_format: ET, FTET
    - data_type: CAT_RAW, CAT_PRE, CONTD_RAW, CONTD_PRE
    
    '''
    # generate
    submission_id = hashlib.sha224(str(datetime.datetime.now()).encode('utf8')).hexdigest()[:12].upper()
    subtype = 'nma_' + cfg['backend'] + '_' + cfg['data_type']
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
        if cfg['input_format'] == 'ET':
            ret = analyze_raw_by_bugsnet(rs, params)
        else:
            ret = {}

    elif cfg['backend'] == 'freq':
        if cfg['data_type'] == 'ET':
            ret = analyze_raw_by_freq(rs, params)
        elif cfg['data_type'] == 'CAT_RAW':
            ret = analyze_raw_by_freq(rs, params)
        elif cfg['data_type'] == 'CAT_PRE':
            ret = analyze_pre_by_freq(rs, params)
        else:
            ret = {}
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
            'tmrank': _bugsnet_trans_rksucra(jrst['sucraplot'], params)
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
    }
    r_params.update(params)

    # convert to dataframe
    df = pd.DataFrame(rs)

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
            'netplt': _netmeta_trans_netplt(jrst['mynetplt'], params),
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
        'small_values_are': 'bad' if params['which_is_better'] == 'big' else 'good',
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
            'netplt': _netmeta_trans_netplt(jrst['mynetplt'], params),
            'league': _netmeta_trans_league_r(jrst['myleaguetb'], params),
            'psrank': _netmeta_trans_pscore(jrst, params)
        }
    }

    return ret
