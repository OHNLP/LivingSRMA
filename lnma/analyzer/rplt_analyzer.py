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

from .rpadapter import _meta_trans_metabin
from .rpadapter import _meta_trans_metaprop
from .rpadapter import _meta_trans_metacum


def analyze(rs, cfg):
    subtype = 'rplt_%s_%s' % (cfg['analyzer_model'], cfg['input_format'])
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

        # for R script
        'smlab_text':  DIS_TEXT['MOE'][cfg['measure_of_effect']],
        
        # file names
        'fn_rscript': fn_rscript,
        'fn_csvfile': TPL_FN['csvfile'].format(**{
            'subtype': subtype, 'submission_id': submission_id
        }),
        'fn_outplt1':  TPL_FN['outplt1'].format(**{
            'subtype': subtype, 'submission_id': submission_id
        }),
        'fn_cumuplt':  TPL_FN['cumuplt'].format(**{
            'subtype': subtype, 'submission_id': submission_id
        }),
        'fn_jsonret': TPL_FN['jsonret'].format(**{
            'subtype': subtype, 'submission_id': submission_id
        }),
    }

    # put all the configs into param
    for key in cfg:
        params[key] = cfg[key]

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

    # if use FORESTDATA model, need to convert the results
    full_filename_jsonret = os.path.join(TMP_FOLDER, params['fn_jsonret'])
    jrst = json.load(open(full_filename_jsonret))
    if cfg['analyzer_model'] == 'PWMA_PRCM':
        ret = {
            'submission_id': params['submission_id'],
            'params': params,
            'success': True,
            'data': {
                'primma': _meta_trans_metabin(jrst, params),
                'cumuma': _meta_trans_metacum(jrst, params),
            }
        }

    elif cfg['analyzer_model'] == 'PWMA_PRIM':
        ret = {
            'submission_id': params['submission_id'],
            'params': params,
            'success': True,
            'data': {
                'primma': _meta_trans_metabin(jrst, params)
            }
        }

    elif cfg['analyzer_model'] == 'PWMA_INCD':
        ret = {
            'submission_id': params['submission_id'],
            'params': params,
            'success': True,
            'data': {
                'incdma': _meta_trans_metaprop(jrst, params),
                'cumuma': _meta_trans_metacum(jrst, params),
            }
        }

    else:
        ret = {
            'submission_id': params['submission_id'],
            'params': params,
            'success': True
        }

    return ret 

