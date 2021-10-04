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

from lnma.analyzer.rpadapter import _netmeta_trans_netcha
from lnma.analyzer.rpadapter import _netmeta_trans_netplt
from lnma.analyzer.rpadapter import _netmeta_trans_forest
from lnma.analyzer.rpadapter import _netmeta_trans_league_r
from lnma.analyzer.rpadapter import _netmeta_trans_pscore

#%% load R packages
meta = importr('meta')
netmeta = importr('netmeta')
jsonlite = importr('jsonlite')

def demo():
    '''
    A demo case for showing how to use
    '''
    cfg = {
        'which_is_better': 'lower'
    }
    df = pd.DataFrame(
        [
            ['Pembro', 'Placebo', 0.68, 0.53, 0.87, 'S1', 2021],
            ['Suni', 'Placebo', 0.76, 0.59, 0.98, 'S2', 2016],
            ['Sora', 'Placebo', 0.97, 0.80, 1.17, 'S3', 2016],
            ['Pazo', 'Placebo', 0.84, 0.71, 0.99, 'S4', 2017],
            ['Axi', 'Placebo', 0.87, 0.66, 1.15, 'S5', 2018]
        ], 
        columns=['t1', 't2', 'sm','lowerci', 'upperci','study','year']
    )

    # convert the TE
    df['TE'] = np.log(df['sm'])

    # usually the SE is not in the data
    if 'seTE' not in df.columns:
        # need to convert the SE
        df['seTE'] = (np.log(df['upperci']) - np.log(df['lowerci'])) / 3.92

    # get the primary
    r_nma = netmeta.netmeta(
        TE = df.TE,
        seTE = df.seTE,
        treat1 = df.t1,
        treat2 = df.t2,
        studlab = df.study,
        sm = 'HR',
        comb_random = False,
        reference_group = 'Placebo'
    )
    r_j_nma = jsonlite.toJSON(r_nma, force=True)
    j_nma = json.loads(r_j_nma[0])

    # the network plot
    r_netplt = netmeta.netgraph(r_nma)
    r_j_netplt = jsonlite.toJSON(r_netplt, force=True)
    j_netplt = json.loads(r_j_netplt[0])

    # the league table
    r_lgtb = netmeta.netleague(r_nma, bracket="(", digits=2)
    r_j_lgtb = jsonlite.toJSON(r_lgtb, force=True)
    j_lgtb = json.loads(r_j_lgtb[0])

    # the forest
    # r_forestplt = netmeta.forest(r_nma)
    # r_j_forestplt = jsonlite.toJSON(r_forestplt, force=True)
    # j_forestplt = json.loads(r_j_forestplt[0])

    # the rank
    r_rank = netmeta.netrank(
        r_nma, 
        small_values = 'good' if cfg['which_is_better'] == 'lower' else 'bad'
    )
    r_j_rank = jsonlite.toJSON(r_rank, force=True)
    j_rank = json.loads(r_j_rank[0])


    ret = {
        'submission_id': 'rpy2',
        'params': cfg,
        'success': True,
        'data': {
            'forest': j_lgtb,
            'league': j_lgtb,
            'netcha': j_netplt,
            'netplt': j_netplt,
            'psrank': j_rank
        }
    }

    pprint(ret)



def analyze_nma_freq_pre(rs, cfg):
    '''
    Analyze the pre-calculated data 

    The given rs should contains:

    study, t1, t2, sm, lowerci, upperci
    '''
    # create a dataframe first
    df = pd.DataFrame(rs)

    # convert the TE
    df['TE'] = np.log(df['sm'])

    # usually the SE is not in the data
    if 'seTE' not in df.columns:
        # need to convert the SE
        df['seTE'] = (np.log(df['upperci']) - np.log(df['lowerci'])) / 3.92

    # get the primary
    r_nma = netmeta(
        TE = df.TE,
        seTE = df.seTE,
        treat1 = df.t1,
        treat2 = df.t2,
        studlab = df.study,
        sm = cfg['measure_of_effect'],
        comb_random = cfg['fixed_or_random']=='random',
        reference_group = cfg['treatments'][0]
    )

    # convert to R json object
    r_j_prim = jsonlite.toJSON(r_nma, force=True)

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
            
        }
    }

    return ret


def analyze_nma_freq_raw(rs, cfg):
    '''
    
    '''

    return None


###########################################################
# Analyzer for the IO project API usage
###########################################################

def analyze(rs, cfg):
    '''
    Analyze the records as the parameters in cfg
    '''
    # for general analyze
    ret = None
    if 'input_format' in cfg:
        if cfg['input_format'] == 'NMA_PRE_SMLU':
            if cfg['analysis_method'] == 'freq':
                ret = analyze_nma_freq_pre(rs, cfg)

        elif cfg['input_format'] == 'NMA_RAW_ET':
            if cfg['analysis_method'] == 'freq':
                ret = analyze_nma_freq_raw(rs, cfg)

    return ret


if __name__ == '__main__':
    demo()