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


def analyze(rs, cfg):
    subtype = 'rplt_%s_%s' % (cfg['prj'], cfg['analyzer_model'])
    if subtype not in RSCRIPT_TPL:
        return { 'success': False, 'msg': 'Incorrect analyzer'}
    # TODO check if data is valid

    # generate
    submission_id = hashlib.sha224(str(datetime.datetime.now()).encode('utf8')).hexdigest()[:12].upper()
    fn_rscript = TPL_FN['rscript'].format(submission_id=submission_id, subtype=subtype)

    params = {
        'submission_id': submission_id,
        'subtype': subtype,

        # file names
        'fn_rscript': fn_rscript
    }

    # put all the configs into param
    for key in cfg:
        params[key] = cfg[key]

    # generate an R script for producing the results
    gen_rscript(
        RSCRIPT_TPL_FOLDER, 
        RSCRIPT_TPL[subtype], 
        params['fn_rscript'], 
        params
    )

    # run the R script
    run_rscript(params['fn_rscript'])

    # return
    ret = {
        'submission_id': params['submission_id'],
        'params': params,
        'success': True
    }

    return ret 

