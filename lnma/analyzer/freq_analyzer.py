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


def analyze(rs, cfg):
    # since frequentist NMA is done by netmeta only ... well, so as follows:
    cfg['freq_backend'] = 'netmeta'

    if cfg['input_format'] == INPUT_FORMATS_ET or \
        cfg['input_format'] == INPUT_FORMATS_FTET:
        cfg['freq_backend'] = 'pairwise_netmeta'
    
    # generate
    submission_id = hashlib.sha224(str(datetime.datetime.now()).encode('utf8')).hexdigest()[:12].upper()
    subtype = 'freq_' + cfg['freq_backend']
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

    # get result from other analyzer
    if cfg['freq_backend'] == 'netmeta':
        ret = analyze_by_netmeta(rs, params)

    elif cfg['freq_backend'] == 'pairwise_netmeta':
        ret = analyze_by_pairwise_netmeta(rs, params)

    else:
        ret = {

        }
    return ret


def analyze_by_netmeta(rs, params):
    '''
    Frequentist NMA
    
    The input `rs` must be in the following format:

        study, t1, t2, hr, lowerci, upperci

    Or:

        study, t1, t2, hr, seTE
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

    # output data
    df = pd.DataFrame(rs)
    
    # check the columns and convert to TE seTE format
    if 'TE' not in df.columns:
        if 'sm' in df.columns:
            df['TE'] = np.log(df['sm'])
        elif 'hr' in df.columns:
            df['TE'] = np.log(df['hr'])
        elif 'or' in df.columns:
            df['TE'] = np.log(df['or'])
        elif 'rr' in df.columns:
            df['TE'] = np.log(df['rr'])

        print('* fixed TE column with hr')

    if 'seTE' not in df.columns:
        f_ci2se = lambda r: (math.log(r['upperci']) - math.log(r['lowerci'])) / 3.92
        df['seTE'] = df.apply(lambda r: round(f_ci2se(r), 4), axis=1)
        print('* fixed seTE column with upper and lower ci')

    # first, output the data for netmeta
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
            'forest': _netmeta_trans_forest(jrst['myforest'], params),
            'league': _netmeta_trans_league_r(jrst['myleaguetb'], params),
            'psrank': _netmeta_trans_pscore(jrst, params)
        }
    }

    return ret


def analyze_by_pairwise_netmeta(rs, params):
    '''
    Frequentist NMA
    
    The input `rs` must be in the following format:

        study, treat, event, total

    Or:

        study, treat, event, total, follow-up time
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
