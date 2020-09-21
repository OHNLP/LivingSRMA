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

from .rpadapter import _meta_trans_metagen


def analyze(rs, cfg):
    subtype = 'pwma_v2_%s' % (cfg['analyzer_model'])
    if subtype not in RSCRIPT_TPL:
        return { 'success': False, 'msg': 'Incorrect analyzer'}
    # TODO check if data is valid

    # generate
    submission_id = hashlib.sha224(str(datetime.datetime.now()).encode('utf8')).hexdigest()[:12].upper()
    fn_rscript = TPL_FN['rscript'].format(submission_id=submission_id, subtype=subtype)

    # prepare 
    params = {
        'submission_id': submission_id,
        'subtype': subtype,

        # r params
        'is_fixed': 'TRUE' if cfg['fixed_or_random'] == 'fixed' else 'FALSE',
        'is_random': 'TRUE' if cfg['fixed_or_random'] == 'random' else 'FALSE',
        
        # file names
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

    # create the CSV file for analysis
    full_filename_csvfile = os.path.join(TMP_FOLDER, params['fn_csvfile'])

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

    # if use PRIM_CAT_PRE model
    if cfg['analyzer_model'] == 'PRIM_CAT_PRE':
        full_filename_jsonret = os.path.join(TMP_FOLDER, params['fn_jsonret'])
        jrst = json.load(open(full_filename_jsonret))
        ret = {
            'submission_id': params['submission_id'],
            'params': params,
            'success': True,
            'data': {
                'primma': _meta_trans_metagen(jrst, params)
            }
        }

    else:
        ret = {
            'submission_id': params['submission_id'],
            'params': params,
            'success': True
        }

    return ret 


