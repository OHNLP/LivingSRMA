#%% load packages
import json
from lnma.analyzer.rpadapter import _meta_trans_metabin, _meta_trans_metacum, _meta_trans_metaprop
from pprint import pprint
import pandas as pd

import rpy2.robjects as ro
from rpy2.robjects.packages import importr
from rpy2.robjects import pandas2ri
pandas2ri.activate()

#%% load R packages
meta = importr('meta')
jsonlite = importr('jsonlite')

#%% create dataframe
def demo():
    '''
    A demo case for showing how to use
    '''
    df = pd.DataFrame(
        [[0,339,3,309,'S1'],[0,343,3,309,'S2']], 
        columns=['Et','Nt','Ec','Nc','study']
    )

    #%% analyze!
    r_ret = meta.metabin(
        df.Et,df.Nt,df.Ec,df.Nc,
        comb_random=True,
        sm='OR'
    )
    r_jobj = jsonlite.toJSON(r_ret, force=True)

    # %% get the result in JSON
    j = json.loads(r_jobj[0])
    pprint(j)


#%% analyzer

def analyze(rs, cfg):
    '''
    Analyze the records as the parameters in cfg
    '''
    if cfg['analyzer_model'] == 'PWMA_PRCM':
        return analyze_pwma_prcm(rs, cfg)

    elif cfg['analyzer_model'] == 'PWMA_INCD':
        return analyze_pwma_incd(rs, cfg)

    else:
        return analyze_pwma_prcm(rs, cfg)


def analyze_pwma_prcm(rs, cfg):
    '''
    Analyze the primary and cumulative
    '''
    # create a dataframe first
    df = pd.DataFrame(rs)

    # get the primary
    r_prim = meta.metabin(
        df.Et, df.Nt, df.Ec, df.Nc,
        studlab=df.study,
        comb_random=True,
        sm=cfg['measure_of_effect'],
        hakn=True if cfg['is_hakn'] == 'YES' else False,
        method=cfg['pooling_method'],
        method_tau=cfg['tau_estimation_method']
    )

    # get the cumulative
    r_cumu = meta.metacum(
        r_prim,
        sortvar=df[cfg['sort_by']]
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

    # build the return
    ret = {
        'submission_id': 'rpy2',
        'params': cfg,
        'success': True,
        'data': {
            'primma': _meta_trans_metabin(j, cfg),
            'cumuma': _meta_trans_metacum(j, cfg),
        }
    }

    return ret


def analyze_pwma_incd(rs, cfg):
    '''
    Analyze the incidence
    '''
    # create a dataframe first
    df = pd.DataFrame(rs)

    # get the incidence
    r_incd = meta.metaprop(
        df.E, df.N,
        studlab=df.study,
        comb_random=True,
        sm=cfg['measure_of_effect'],
        hakn=True if cfg['is_hakn'] == 'YES' else False,
        method=cfg['pooling_method'],
        method_tau=cfg['tau_estimation_method']
    )

    # get the cumulative
    r_cumu = meta.metacum(
        r_incd,
        sortvar=df[cfg['sort_by']]
    )

    # convert to R json object
    r_j_incd = jsonlite.toJSON(r_incd, force=True)
    r_j_cumu = jsonlite.toJSON(r_cumu, force=True)

    # convert to Python JSON object
    j_incd = json.loads(r_j_incd[0])
    j_cumu = json.loads(r_j_cumu[0])

    # for compability
    j = {
        'primma': j_incd,
        'incdma': j_incd,
        'cumuma': j_cumu,
    }

    # build the return
    ret = {
        'submission_id': 'rpy2',
        'params': cfg,
        'success': True,
        'data': {
            'incdma': _meta_trans_metaprop(j, cfg),
            'cumuma': _meta_trans_metacum(j, cfg),
        }
    }

    return ret


