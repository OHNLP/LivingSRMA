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

from .rpadapter import _meta_trans_metabin
from .rpadapter import _meta_trans_metacum

from lnma.settings import *


def analyze(rs, cfg):
    # generate
    submission_id = hashlib.sha224(str(datetime.datetime.now()).encode('utf8')).hexdigest()[:12].upper()
    subtype = 'pwma_' + cfg['input_format']
    fn_rscript = TPL_FN['rscript'].format(submission_id=submission_id, subtype=subtype)

    # generate parameters from the configs
    params = {
        'submission_id': submission_id,
        'subtype': subtype,

        # for R script
        'is_fixed': 'TRUE' if cfg['fixed_or_random'] == 'fixed' else 'FALSE',
        'is_random': 'TRUE' if cfg['fixed_or_random'] == 'random' else 'FALSE',
        'is_hakn': cfg['hakn_adjustment'],
        'is_prediction': cfg['prediction_interval'],
        'smlab_text':  DIS_TEXT['MOE'][cfg['measure_of_effect']],

        # for output
        'fn_rscript': fn_rscript,
        'fn_csvfile': TPL_FN['csvfile'].format(**{
            'subtype': subtype, 'submission_id': submission_id
        }),
        'fn_jsonret': TPL_FN['jsonret'].format(**{
            'subtype': subtype, 'submission_id': submission_id
        }),
        'fn_outplt1':  TPL_FN['outplt1'].format(**{
            'subtype': subtype, 'submission_id': submission_id
        }),
        'result_plots': ['fn_outplt1']
    }

    # put all the configs into param
    for key in cfg:
        params[key] = cfg[key]

    # update some configs for R script, make sure these are in upper case
    params['measure_of_effect'] = params['measure_of_effect'].upper()
    params['tau_estimation_method'] = params['tau_estimation_method'].upper()

    # update some configs for sensitivity analysis and cumulative analysis
    if params['pairwise_analysis'] == 'PRIM':
        params['fn_fnnlplt'] = TPL_FN['fnnlplt'].format(**{
            'subtype': subtype, 'submission_id': submission_id
        })
        params['result_plots'].append('fn_fnnlplt')

    # the configs for sensitivity analysis
    if params['pairwise_analysis'] == 'PRIM' and \
       params['sensitivity_analysis'] == 'yes':
        if len(params['sensitivity_analysis_excluded_study_list']) == 0:
            params['sensitivity_analysis'] == 'no'
        else:
            params['sensitivity_analysis_exsubset'] = \
                ",".join([ '"%s"' % s for s in params['sensitivity_analysis_excluded_study_list'] ])
            params['fn_sensplt'] = TPL_FN['sensplt'].format(**{
                'subtype': subtype, 'submission_id': submission_id
            })
            params['result_plots'].append('fn_sensplt')

    if params['pairwise_analysis'] == 'PRIM' and \
       params['cumulative_meta_analysis'] == 'yes':
        params['fn_cumuplt'] = TPL_FN['cumuplt'].format(**{
            'subtype': subtype, 'submission_id': submission_id
        })
        params['result_plots'].append('fn_cumuplt')

    # prepare the file names
    full_filename_csvfile = os.path.join(TMP_FOLDER, params['fn_csvfile'])
    full_filename_jsonret = os.path.join(TMP_FOLDER, params['fn_jsonret'])

    # convert to dataframe and to csv data file for R script to load
    df = pd.DataFrame(rs)
    df.to_csv(full_filename_csvfile, index=False)

    # generate an R script for producing the results
    gen_rscript(
        RSCRIPT_TPL_FOLDER, 
        RSCRIPT_TPL[subtype], 
        params['fn_rscript'], 
        params
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
            'primma': _meta_trans_metabin(jrst, params)
        }
    }

    return ret