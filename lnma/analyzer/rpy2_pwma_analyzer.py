#%% load packages
import json
from pprint import pprint
import pandas as pd
import warnings

import numpy as np

import rpy2.robjects as ro
from rpy2.robjects.packages import importr

# remove the warnings for rpy2
from rpy2.rinterface import RRuntimeWarning
warnings.filterwarnings("ignore", category=RRuntimeWarning)

# remove the warnings for rpy2 version > 3
from rpy2.rinterface_lib.callbacks import logger as rpy2_logger
import logging
rpy2_logger.setLevel(logging.ERROR)

from rpy2.robjects import pandas2ri
pandas2ri.activate()

from lnma.analyzer.rpadapter import _meta_trans_metabin
from lnma.analyzer.rpadapter import _meta_trans_metagen
from lnma.analyzer.rpadapter import _meta_trans_metacum
from lnma.analyzer.rpadapter import _meta_trans_metaprop

#%% load R packages
meta = importr('meta')
jsonlite = importr('jsonlite')

def demo():
    '''
    A demo case for showing how to use
    '''
    df = pd.DataFrame(
        [
            [1,131,0,132,'S1',2021],
            [2,380,0,132,'S2',2021],
            [2,355,0,342,'S3',2021],
            [9,348,4,344,'S4',2021],
        ], 
        columns=['Et','Nt','Ec','Nc','study','year']
    )

    #%% analyze!
    r_prim = meta.metabin(
        df.Et,df.Nt,df.Ec,df.Nc,
        studlab=df.study,
        comb_random=True,
        sm='OR'
    )

    # get the cumulative
    r_cumu = meta.metacum(
        r_prim,
        pooled="random",
        sortvar=df['year']
    )

    # convert to R json object
    r_j_prim = jsonlite.toJSON(r_prim, force=True)
    r_j_cumu = jsonlite.toJSON(r_cumu, force=True)

    # convert to Python JSON object
    j_prim = json.loads(r_j_prim[0])
    j_cumu = json.loads(r_j_cumu[0])

    # for compability
    j = {
        'primma': j_prim,
        'cumuma': j_cumu,
    }
    pprint(j)
    print('primma: ', j['primma']['TE.random'])
    print('cumuma: ', j['cumuma']['TE'][-1])


def demo2():
    '''
    A demo case for showing how to use
    '''
    df = pd.DataFrame(
        [
            [1,131,0,132,'S1',2021],
            [2,380,0,132,'S2',2021],
            [2,355,0,342,'S3',2021],
            [9,348,4,344,'S4',2021],
        ], 
        columns=['Et','Nt','Ec','Nc','study','year']
    )

    #%% analyze!
    r_prim = meta.metabin(
        df.Et,df.Nt,df.Ec,df.Nc,
        studlab=df.study,
        comb_random=True,
        sm='OR'
    )

    # get the cumulative
    r_cumu = meta.metacum(
        r_prim,
        pooled="random",
        sortvar=df['year']
    )

    # convert to R json object
    r_j_prim = jsonlite.toJSON(r_prim, force=True)
    r_j_cumu = jsonlite.toJSON(r_cumu, force=True)

    # convert to Python JSON object
    j_prim = json.loads(r_j_prim[0])
    j_cumu = json.loads(r_j_cumu[0])

    # for compability
    j = {
        'primma': j_prim,
        'cumuma': j_cumu,
    }
    pprint(j)
    print('primma: ', j['primma']['TE.random'])
    print('cumuma: ', j['cumuma']['TE'][-1])


def analyze_pwma_cat_raw(rs, cfg):
    '''
    Analyze the primary of Categorical Raw Data

    The given rs should contains:

    study, Et, Nt, Ec, Nc
    '''
    # create a dataframe first
    df = pd.DataFrame(rs)

    # get the primary
    r_prim = meta.metabin(
        df.Et, df.Nt, df.Ec, df.Nc,
        studlab=df.study,
        comb_random=cfg['fixed_or_random']=='random',
        sm=cfg['measure_of_effect'],
        hakn=True if cfg['hakn_adjustment'] == 'TRUE' else False,
        method=cfg['pooling_method'],
        method_tau=cfg['tau_estimation_method']
    )

    # convert to R json object
    r_j_prim = jsonlite.toJSON(r_prim, force=True)

    # convert to Python JSON object
    j_prim = json.loads(r_j_prim[0])

    # for compability
    j = {
        'primma': j_prim
    }

    # build the return
    ret = {
        'submission_id': 'rpy2',
        'params': cfg,
        'success': True,
        'data': {
            'primma': _meta_trans_metabin(j, cfg)
        }
    }

    return ret


def analyze_pwma_cat_raw_incd(rs, cfg):
    '''
    Analyze the incidence rate of Categorical Raw Data

    The given rs should contains:

    study, Et, Nt
    '''
    # create a dataframe first
    df = pd.DataFrame(rs)

    # set the sm if not correct
    if cfg['measure_of_effect'] not in ['PLOGIT', 'PAS', "PFT", "PLN", "PRAW"]:
        cfg['measure_of_effect'] = 'PLOGIT'

    # get the incd
    r_incd = meta.metaprop(
        df.Et, df.Nt,
        studlab=df.study,
        comb_random=cfg['fixed_or_random']=='random',
        sm=cfg['measure_of_effect'],
        hakn=True if cfg['hakn_adjustment'] == 'TRUE' else False,
        method=cfg['pooling_method'],
        method_tau=cfg['tau_estimation_method']
    )
    # convert to R json object
    r_j_incd = jsonlite.toJSON(r_incd, force=True)

    # convert to Python JSON object
    j_incd = json.loads(r_j_incd[0])

    # for compability
    j = {
        'incdma': j_incd
    }

    # build the return
    ret = {
        'submission_id': 'rpy2',
        'params': cfg,
        'success': True,
        'data': {
            'incdma': _meta_trans_metaprop(j, cfg)
        }
    }

    return ret


def analyze_pwma_cat_pre(rs, cfg):
    '''
    Analyze the primary of Categorical pre-calculated

    The given rs should contains:

    study, TE, upperci, lowerci
    '''
    # create a dataframe first
    df = pd.DataFrame(rs)

    # convert the TE
    df['TE'] = np.log(df['TE'])

    # usually the SE is not in the data
    if 'SE' not in df.columns:
        # need to convert the SE
        df['SE'] = (np.log(df['upperci']) - np.log(df['lowerci'])) / 3.92

    # get the primary
    r_prim = meta.metagen(
        df.TE, df.SE,
        studlab=df.study,
        sm=cfg['measure_of_effect'],
        comb_random=cfg['fixed_or_random']=='random',
        method_tau=cfg['tau_estimation_method'],
        hakn=True if cfg['hakn_adjustment'] == 'TRUE' else False
    )

    # convert to R json object
    r_j_prim = jsonlite.toJSON(r_prim, force=True)

    # convert to Python JSON object
    j_prim = json.loads(r_j_prim[0])

    # for compability
    j = {
        'primma': j_prim,
    }

    # build the return
    ret = {
        'submission_id': 'rpy2',
        'params': cfg,
        'success': True,
        'data': {
            'primma': _meta_trans_metagen(j, cfg)
        }
    }

    return ret


def analyze_subg_cat_pre(rs, cfg):
    '''
    Analyze the subgroup of Categorical pre-calculated

    The given rs should contains:

    study, TE, upperci, lowerci, subgroup
    '''
    # create a dataframe first
    df = pd.DataFrame(rs)

    # convert the TE
    df['TE'] = np.log(df['TE'])

    # usually the SE is not in the data
    if 'SE' not in df.columns:
        # need to convert the SE
        df['SE'] = (np.log(df['upperci']) - np.log(df['lowerci'])) / 3.92

    # get the primary
    r_prim = meta.metagen(
        df.TE, 
        df.SE,
        studlab=df.study,
        byvar=df.subgroup,
        sm=cfg['measure_of_effect'],
        comb_random=cfg['fixed_or_random']=='random',
        method_tau=cfg['tau_estimation_method'],
        hakn=True if cfg['hakn_adjustment'] == 'TRUE' else False
    )

    # convert to R json object
    r_j_prim = jsonlite.toJSON(r_prim, force=True)
    print(r_j_prim)

    # convert to Python JSON object
    j_prim = json.loads(r_j_prim[0])

    # for compability
    j = {
        'primma': j_prim,
    }

    # build the return
    ret = {
        'submission_id': 'rpy2',
        'params': cfg,
        'success': True,
        'data': {
            'primma': _meta_trans_metagen(j, cfg)
        }
    }

    return ret

###########################################################
# Analyzer for the IO project API usage
###########################################################

def analyze(rs, cfg):
    '''
    Analyze the records as the parameters in cfg
    '''
    # for IO API
    if 'analyzer_model' in cfg:
        if cfg['analyzer_model'] == 'PWMA_PRCM':
            return analyze_pwma_prcm(rs, cfg)

        elif cfg['analyzer_model'] == 'PWMA_PRBN':
            return analyze_pwma_prcm(rs, cfg, has_cumu=False)

        elif cfg['analyzer_model'] == 'PWMA_INCD':
            return analyze_pwma_incd(rs, cfg, has_cumu=True)

        else:
            return analyze_pwma_prcm(rs, cfg)

    # for general analyze
    ret = None
    if 'input_format' in cfg:
        if cfg['input_format'] == 'PRIM_CAT_PRE':
            ret = analyze_pwma_cat_pre(rs, cfg)

        elif cfg['input_format'] == 'PRIM_CAT_RAW':
            ret = analyze_pwma_cat_raw(rs, cfg)

    return ret


def analyze_pwma_prcm(rs, cfg, has_cumu=True):
    '''
    Analyze the primary and cumulative
    '''
    # create a dataframe first
    df = pd.DataFrame(rs)

    # get the primary
    r_prim = meta.metabin(
        df.Et, df.Nt, df.Ec, df.Nc,
        studlab=df.study,
        comb_random=cfg['fixed_or_random']=='random',
        sm=cfg['measure_of_effect'],
        hakn=True if cfg['is_hakn'] == 'TRUE' else False,
        method=cfg['pooling_method'],
        method_tau=cfg['tau_estimation_method']
    )

    # convert to R json object
    r_j_prim = jsonlite.toJSON(r_prim, force=True)

    # convert to Python JSON object
    j_prim = json.loads(r_j_prim[0])

    # for compability
    j = {
        'primma': j_prim,
    }
    
    # get the cumulative
    if has_cumu:
        r_cumu = meta.metacum(
            r_prim,
            pooled=cfg['fixed_or_random'],
            sortvar=df[cfg['sort_by']]
        )
        r_j_cumu = jsonlite.toJSON(r_cumu, force=True)
        j_cumu = json.loads(r_j_cumu[0])
        j['cumuma'] = j_cumu

    # build the return
    ret = {
        'submission_id': 'rpy2',
        'params': cfg,
        'success': True,
        'data': {
            'primma': _meta_trans_metabin(j, cfg)
        }
    }
    if has_cumu:
        ret['data']['cumuma'] = _meta_trans_metacum(j, cfg)

    return ret


def analyze_pwma_incd(rs, cfg, has_cumu=True):
    '''
    Analyze the incidence
    '''
    # create a dataframe first
    df = pd.DataFrame(rs)

    # get the incidence
    r_incd = meta.metaprop(
        df.E, df.N,
        studlab=df.study,
        comb_random=cfg['fixed_or_random']=='random',
        sm=cfg['measure_of_effect'],
        hakn=True if cfg['is_hakn'] == 'TRUE' else False,
        method=cfg['pooling_method'],
        method_tau=cfg['tau_estimation_method']
    )

    # convert to R json object
    r_j_incd = jsonlite.toJSON(r_incd, force=True)

    # convert to Python JSON object
    j_incd = json.loads(r_j_incd[0])

    # for compability
    j = {
        'primma': j_incd,
        'incdma': j_incd,
    }
    
    # get the cumulative
    if has_cumu:
        r_cumu = meta.metacum(
            r_incd,
            pooled=cfg['fixed_or_random'],
            sortvar=df[cfg['sort_by']]
        )
        r_j_cumu = jsonlite.toJSON(r_cumu, force=True)
        j_cumu = json.loads(r_j_cumu[0])
        j['cumuma'] = j_cumu

    # build the return
    ret = {
        'submission_id': 'rpy2',
        'params': cfg,
        'success': True,
        'data': {
            'incdma': _meta_trans_metaprop(j, cfg)
        }
    }
    if has_cumu:
        ret['data']['cumuma'] = _meta_trans_metacum(j, cfg)

    return ret


###########################################################
# A wrapper for compatibility with py_pwma_analyzer
###########################################################

def get_pma(dataset, datatype='CAT_RAW', 
    sm='RR', method='MH', fixed_or_random='random'):
    '''
    Get the pma result in a simple way
    '''
    df = pd.DataFrame(
        dataset,
        columns=['Et', 'Nt', 'Ec', 'Nc', 'study']
    )
    cfg = {
        'measure_of_effect': sm,
        'is_hakn': 'FALSE',
        'pooling_method': method,
        'fixed_or_random': fixed_or_random,
        'tau_estimation_method': 'DL'
    }
    # get the result
    full_result = analyze_pwma_prcm(df, cfg, False)

    r = full_result['data']['primma']['model'][fixed_or_random]

    # h is for heterogeneity
    h = full_result['data']['primma']['heterogeneity']

    # the results used here is the backtraced values
    ret = {
        "model": {
            "measure": sm,
            "sm": r['bt_TE'],
            "lower": r['bt_lower'],
            "upper": r['bt_upper'],
            "total": r['Nt'],
            "i2": h['i2'],
            "tau2": h['tau2'],
            "q_pval": h['p'],
            "q_tval": None,
            "z_pval": None,
            "z_tval": None,
        },
        "stus": full_result['data']['primma']['stus']
    }

    # result for each stu
    for i in range(len(ret['stus'])):
        ret['stus'][i]['sm'] = ret['stus'][i]['bt_TE']
        ret['stus'][i]['total'] = ret['stus'][i]['Nt']
        ret['stus'][i]['w'] = ret['stus'][i]['w_'+fixed_or_random]

        # backup original value
        ret['stus'][i]['og_lower'] = ret['stus'][i]['lower']
        ret['stus'][i]['og_upper'] = ret['stus'][i]['upper']
        # set to backtraced value
        ret['stus'][i]['lower'] = ret['stus'][i]['bt_lower']
        ret['stus'][i]['upper'] = ret['stus'][i]['bt_upper']

    return ret


if __name__ == '__main__':
    demo()