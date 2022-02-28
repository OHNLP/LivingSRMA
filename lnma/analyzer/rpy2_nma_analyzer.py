#%% load packages
import json
import math
import pandas as pd
import warnings

import numpy as np
from pprint import pprint

import rpy2.robjects as ro
from rpy2.robjects.packages import importr
import rpy2.rinterface as rinterface
# remove the warnings for rpy2
from rpy2.rinterface import RRuntimeWarning

from lnma import settings
warnings.filterwarnings("ignore", category=RRuntimeWarning)

# remove the warnings for rpy2 version > 3
from rpy2.rinterface_lib.callbacks import logger as rpy2_logger
import logging
rpy2_logger.setLevel(logging.ERROR)

from rpy2.robjects import pandas2ri
pandas2ri.activate()

from rpy2.robjects.conversion import localconverter

from lnma.analyzer.rpadapter import _bugsnet_trans_forest 
from lnma.analyzer.rpadapter import _bugsnet_trans_league
from lnma.analyzer.rpadapter import _bugsnet_trans_netcha
from lnma.analyzer.rpadapter import _bugsnet_trans_netplt
from lnma.analyzer.rpadapter import _bugsnet_trans_rksucra
from lnma.analyzer.rpadapter import _bugsnet_trans_scrplt
from lnma.analyzer.rpadapter import _gemtc_trans_netcha
from lnma.analyzer.rpadapter import _gemtc_trans_netplt
from lnma.analyzer.rpadapter import _gemtc_trans_forest
from lnma.analyzer.rpadapter import _gemtc_trans_league
from lnma.analyzer.rpadapter import _dmetar_trans_scrplt
from lnma.analyzer.rpadapter import _dmetar_trans_rksucra
from lnma.analyzer.rpadapter import _netmeta_trans_netcha
from lnma.analyzer.rpadapter import _netmeta_trans_netplt
from lnma.analyzer.rpadapter import _netmeta_trans_forest
from lnma.analyzer.rpadapter import _netmeta_trans_league_r
from lnma.analyzer.rpadapter import _netmeta_trans_pscore

# for R base package
base = importr('base')

# for freq nma
meta = importr('meta')
netmeta = importr('netmeta')
jsonlite = importr('jsonlite')

# for bayes nma
gemtc = importr('gemtc')
rjags = importr('rjags')
dmetar = importr('dmetar')
bugsnet = importr('BUGSnet')

# remove the Rplots.pdf output
ro.r('pdf(NULL)')


def analyze_nma_freq_pre(rs, cfg):
    '''
    Analyze the pre-calculated data by freq method

    The given rs should contains:

    study, t1, t2, sm, lowerci, upperci

    measure_of_effect
    fixed_or_random
    reference_treatment
    which_is_better

    '''
    # create a dataframe first
    df = pd.DataFrame(rs)

    # convert the TE
    df['TE'] = np.log(df['sm'])

    # usually the SE is not in the data
    if 'seTE' not in df.columns:
        # need to convert the SE
        df['seTE'] = (np.log(df['upperci']) - np.log(df['lowerci'])) / 3.92

    all_treats = list(set(df.t1.to_list() + df.t2.to_list()))

    if 'reference_treatment' in cfg:
        reference_treatment = cfg['reference_treatment']
    else:
        reference_treatment = all_treats[0]
        cfg['reference_treatment'] = reference_treatment

    # get the primary
    r_nma = netmeta.netmeta(
        TE = df.TE,
        seTE = df.seTE,
        treat1 = df.t1,
        treat2 = df.t2,
        studlab = df.study,
        sm = cfg['measure_of_effect'],
        comb_fixed = cfg['fixed_or_random']=='fixed',
        comb_random = cfg['fixed_or_random']=='random',
        reference_group = reference_treatment
    )

    # get the network plot
    r_netplt = netmeta.netgraph(r_nma)

    # get the league table
    r_lgtb = netmeta.netleague(r_nma, bracket="(", digits=2)

    # get the ps rank
    if cfg['which_is_better'] == 'lower' or \
       cfg['which_is_better'] == 'small':
        small_values = 'good'
    else:
        small_values = 'bad'

    r_rank = netmeta.netrank(
        r_nma, 
        small_values = small_values
    )

    # get the forest
    r_forest = netmeta.forest_netmeta(r_nma)

    # convert to json obj
    r_j_nma = jsonlite.toJSON(r_nma, force=True)
    j_nma = json.loads(r_j_nma[0])
    
    r_j_netplt = jsonlite.toJSON(r_netplt, force=True)
    j_netplt = json.loads(r_j_netplt[0])

    r_j_lgtb = jsonlite.toJSON(r_lgtb, force=True)
    j_lgtb = json.loads(r_j_lgtb[0])

    r_j_rank = jsonlite.toJSON(r_rank, force=True)
    j_rank = json.loads(r_j_rank[0])

    r_j_forest = jsonlite.toJSON(r_forest, force=True)
    j_forest = json.loads(r_j_forest[0])

    # for compability
    jrst = {
        'nma': j_nma,
        'mynetplt': j_netplt,
        'myleaguetb': j_lgtb,
        'myforest': j_forest,
        'myrank': {
            'trts': j_nma['trts'],
            'fixed': j_rank['Pscore.fixed'],
            'random': j_rank['Pscore.random']
        },
    }

    # build the return
    ret = {
        'submission_id': 'rpy2',
        'params': cfg,
        'success': True,
        'data': {
            'netcha': _netmeta_trans_netcha(jrst['nma'], cfg),
            'netplt': _netmeta_trans_netplt(jrst['mynetplt'], cfg),
            'league': _netmeta_trans_league_r(jrst['myleaguetb'], cfg),
            'forest': _netmeta_trans_forest(jrst['myforest'], cfg),
            'psrank': _netmeta_trans_pscore(jrst, cfg)
        }
    }

    return ret


def analyze_nma_freq_raw(rs, cfg):
    '''
    Analyze raw data by freq method

    the input rs follows:

    study, treat1, event1, n1, treat2, event2, n2

    needed paramters:

    measure_of_effect
    fixed_or_random
    which_is_better

    '''
    # create a dataframe first
    df = pd.DataFrame(rs)

    # convert the TE format
    r_mydata = netmeta.pairwise(
        [df.treat1, df.treat2],
        [df.event1, df.event2],
        [df.n1,     df.n2],
        data = df,
        sm = cfg['measure_of_effect']
    )

    # get ref
    all_treats = list(set(df.treat1.to_list() + df.treat2.to_list()))
    if 'reference_treatment' in cfg:
        reference_treatment = cfg['reference_treatment']
    else:
        reference_treatment = all_treats[0]
        cfg['reference_treatment'] = reference_treatment

    # get the primary
    r_nma = netmeta.netmeta(
        TE = r_mydata.TE,
        seTE = r_mydata.seTE,
        treat1 = r_mydata.treat1,
        treat2 = r_mydata.treat2,
        studlab = r_mydata.study,
        data = r_mydata,
        sm = cfg['measure_of_effect'],
        comb_fixed = cfg['fixed_or_random']=='fixed',
        comb_random = cfg['fixed_or_random']=='random'
    )

    # get the network plot
    r_netplt = netmeta.netgraph(r_nma)

    # get the league table
    r_lgtb = netmeta.netleague(r_nma, bracket="(", digits=2)

    # get the forest
    r_forest = netmeta.forest_netmeta(r_nma)

    # get the ps rank
    if cfg['which_is_better'] == 'lower' or \
       cfg['which_is_better'] == 'small':
        small_values = 'good'
    else:
        small_values = 'bad'

    r_rank = netmeta.netrank(
        r_nma, 
        small_values = small_values
    )

    # convert to json obj
    r_j_nma = jsonlite.toJSON(r_nma, force=True)
    j_nma = json.loads(r_j_nma[0])
    
    r_j_netplt = jsonlite.toJSON(r_netplt, force=True)
    j_netplt = json.loads(r_j_netplt[0])

    r_j_lgtb = jsonlite.toJSON(r_lgtb, force=True)
    j_lgtb = json.loads(r_j_lgtb[0])

    r_j_rank = jsonlite.toJSON(r_rank, force=True)
    j_rank = json.loads(r_j_rank[0])

    r_j_forest = jsonlite.toJSON(r_forest, force=True)
    j_forest = json.loads(r_j_forest[0])

    # for compability
    jrst = {
        'nma': j_nma,
        'mynetplt': j_netplt,
        'myleaguetb': j_lgtb,
        'myforest': j_forest,
        'myrank': {
            'trts': j_nma['trts'],
            'fixed': j_rank['Pscore.fixed'],
            'random': j_rank['Pscore.random']
        },
    }

    # build the return
    ret = {
        'submission_id': 'rpy2',
        'params': cfg,
        'success': True,
        'data': {
            'netcha': _netmeta_trans_netcha(jrst['nma'], cfg),
            'netplt': _netmeta_trans_netplt(jrst['mynetplt'], cfg),
            'league': _netmeta_trans_league_r(jrst['myleaguetb'], cfg),
            'forest': _netmeta_trans_forest(jrst['myforest'], cfg),
            'psrank': _netmeta_trans_pscore(jrst, cfg)
        }
    }

    return ret


def analyze_nma_bayes_pre(rs, cfg):
    '''
    Analyze the pre-calculated data by freq method

    The given rs should contains:

    study, t1, t2, sm/hr, lowerci, upperci

    measure_of_effect
    fixed_or_random
    reference_treatment
    which_is_better
    '''
    # create a dataframe first
    df = pd.DataFrame(rs)

    # fix columns
    if 'TE' not in df.columns and 'hr' in df.columns:
        df['TE'] = np.log(df['hr'])
    
    if 'TE' not in df.columns and 'sm' in df.columns:
        df['TE'] = np.log(df['sm'])

    if 'seTE' not in df.columns:
        f_ci2se = lambda r: (math.log(r['upperci']) - math.log(r['lowerci'])) / 3.92
        df['seTE'] = df.apply(lambda r: round(f_ci2se(r), 4), axis=1)
        print('* fixed seTE column with upper and lower ci')

    # get ref
    all_treats = list(set(df.t1.to_list() + df.t2.to_list()))
    if 'reference_treatment' in cfg:
        reference_treatment = cfg['reference_treatment']
    else:
        reference_treatment = all_treats[0]
        cfg['reference_treatment'] = reference_treatment

    # get sucra better
    if cfg['which_is_better'] == 'lower' or \
       cfg['which_is_better'] == 'small':
        sucra_lower_is_better = True
    else:
        sucra_lower_is_better = False

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

    # create a mtc network
    r_network = gemtc.mtc_network(
        data_re = df2
    )
    r_model = gemtc.mtc_model(
        r_network,
        link = 'log',
        likelihood = 'poisson',
        linearModel = cfg['fixed_or_random']
    )
    r_mcmc = gemtc.mtc_run(
        r_model,
        n_adapt = 50,
        n_iter = 1000,
        thin = 1
    )
    # r_results = gemtc.mtc_run(
    #     r_model
    # )
    # base.summary(r_results)

    # rankogram
    r_rank_probability = gemtc.rank_probability(r_mcmc)

    # fix for python env to assign rownames to the r_rank_probability
    r_rank_probability_df = base.data_frame(
        r_rank_probability, 
        row_names=base.rownames(r_network.rx2('treatments'))
    )

    # r_rank_probsmat = base.as_matrix(r_rank_probability)
    # r_rank_rownames = base.rownames(r_rank_probsmat)
    r_rank_rownames = base.rownames(r_network.rx2('treatments'))

    r_rank_sucra = dmetar.sucra(
        r_rank_probability_df, 
        lower_is_better = sucra_lower_is_better
    )
    
    # forest
    r_forest = gemtc.forest(
        gemtc.relative_effect(
            r_mcmc,
            t1 = reference_treatment
        ),
        digits = 2
    )

    # league table
    r_league = gemtc.relative_effect_table(r_mcmc)
    r_expleague = base.data_frame(
        base.exp(r_league),
        row_names=base.rownames(r_network.rx2('treatments'))
    )

    # convert R to JSON
    j_r_model = jsonlite.toJSON(r_model, force=True)
    j_model = json.loads(j_r_model[0])

    j_r_expleague = jsonlite.toJSON(r_expleague, force=True)
    j_expleague = json.loads(j_r_expleague[0])

    j_r_rank_sucra = jsonlite.toJSON(r_rank_sucra, force=True)
    j_rank_sucra = json.loads(j_r_rank_sucra[0])

    j_r_rank_probability = jsonlite.toJSON(r_rank_probability, force=True)
    j_rank_probability = json.loads(j_r_rank_probability[0])

    j_r_rank_rownames = jsonlite.toJSON(r_rank_rownames, force=True)
    j_rank_rownames = json.loads(j_r_rank_rownames[0])

    # make a result
    jrst = {
        'model': j_model,
        'expleague': j_expleague,
        'sucraplot': {
            'probs': j_rank_probability,
            'rows': j_rank_rownames
        },
        'sucrarank': j_rank_sucra,
    }

    # convertion to output for analyzer
    ret = {
        'submission_id': 'rpy2',
        'params': cfg,
        'success': True,
        'data': {
            'netcha': _gemtc_trans_netcha(jrst['model'], cfg),
            'netplt': _gemtc_trans_netplt(jrst['model'], cfg),
            'forest': _gemtc_trans_forest(jrst['expleague'], cfg),
            'league': _gemtc_trans_league(jrst['expleague'], cfg),
            'scrplt': _dmetar_trans_scrplt(jrst, cfg),
            'tmrank': _dmetar_trans_rksucra(jrst, cfg)
        }
    }

    return ret


def analyze_nma_bayes_raw(rs, cfg):
    '''
    Analyze raw data by freq method

    the input rs follows:

    study, treat, event, total

    needed paramters:

    measure_of_effect
    fixed_or_random
    which_is_better
    reference_treatment
    
    '''
    df = pd.DataFrame(rs)
    with localconverter(ro.default_converter + pandas2ri.converter):
        r_df = ro.conversion.py2rpy(df)

    # get param
    if cfg['measure_of_effect'] == 'HR':
        model_param_time = 'time'
    else:
        model_param_time = rinterface.NULL

    # the link
    measure_of_effect_to_link = settings.R_BUGSNET_MEASURE2LINK[
        cfg['measure_of_effect']
    ]

    # the sucra_largerbetter

    # get sucra better
    if cfg['which_is_better'] == 'lower' or \
       cfg['which_is_better'] == 'small':
        sucra_largerbetter = False
    else:
        sucra_largerbetter = True

    # get ref
    all_treats = list(set(df.treat.to_list()))
    if 'reference_treatment' in cfg:
        reference_treatment = cfg['reference_treatment']
    else:
        reference_treatment = all_treats[0]
        cfg['reference_treatment'] = reference_treatment

    # prepare data
    r_dich_slr = bugsnet.data_prep(
        arm_data = r_df,
        varname_t = 'treat',
        varname_s = 'study'
    )

    # get netchar
    r_network_char = bugsnet.net_tab(
        data = r_dich_slr,
        outcome = "event",
        N = "total", 
        type_outcome = "binomial",
        time = rinterface.NULL
    )

    # get model
    r_fr_effects_model = bugsnet.nma_model(
        data = r_dich_slr,
        outcome = "event",
        N = "total",
        reference = reference_treatment,
        family = "binomial",
        link = measure_of_effect_to_link,
        time = model_param_time,
        effects = cfg["fixed_or_random"]
    )

    # run model
    base.set_seed(20190829)
    r_fr_effects_results = bugsnet.nma_run(
        r_fr_effects_model,
        n_iter = 10000, # original 10000
        n_adapt = 1000,  # original 1000
        n_burnin = 1000  # original 1000
    )

    # get sucra
    r_sucra_out = bugsnet.nma_rank(
        r_fr_effects_results, 
        largerbetter = sucra_largerbetter, 
        sucra_palette = "Set1"
    )

    # get league table
    r_league_out = bugsnet.nma_league(
        r_fr_effects_results,
        central_tdcy = "median",
        order = r_sucra_out.rx2('order'),
        log_scale = False,
        low_colour = "springgreen4",
        mid_colour = "white",
        high_colour = "red",
        digits = 2
    )

    # convert r to j
    j_r_network_char = jsonlite.toJSON(r_network_char, force=True)
    j_network_char = json.loads(j_r_network_char[0])

    j_r_sucra_out_sucratable = jsonlite.toJSON(r_sucra_out.rx2('sucratable'), force=True)
    j_sucra_out_sucratable = json.loads(j_r_sucra_out_sucratable[0])

    j_r_league_out_longtable = jsonlite.toJSON(r_league_out.rx2('longtable'), force=True)
    j_league_out_longtable = json.loads(j_r_league_out_longtable[0])

    # jrst
    jrst = {
        'network_char': j_network_char,
        'sucraplot': j_sucra_out_sucratable,
        'league': j_league_out_longtable
    }

    ret = {
        'submission_id': 'rpy2',
        'params': cfg,
        'success': True,
        'data': {
            'netplt': _bugsnet_trans_netplt(jrst['network_char']['comparison'], cfg),
            'league': _bugsnet_trans_league(jrst['league'], cfg),
            'tmrank': _bugsnet_trans_rksucra(jrst['sucraplot'], cfg),

            'scrplt': _bugsnet_trans_scrplt(jrst['sucraplot'], cfg),
            'netcha': _bugsnet_trans_netcha(jrst['network_char']['network'], cfg),
            'forest': _bugsnet_trans_forest(jrst['league'], cfg),
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
    # for general analyze
    ret = None
    if 'input_format' not in cfg:
        return None
    
    if cfg['input_format'] == settings.INPUT_FORMAT_NMA_PRE_SMLU:
        if cfg['analysis_method'] == 'freq':
            ret = analyze_nma_freq_pre(rs, cfg)

        elif cfg['analysis_method'] == 'bayes':
            ret = analyze_nma_bayes_pre(rs, cfg)

    elif cfg['input_format'] == settings.INPUT_FORMAT_NMA_RAW_ET:
        if cfg['analysis_method'] == 'freq':
            ret = analyze_nma_freq_raw(rs, cfg)

        elif cfg['analysis_method'] == 'bayes':
            ret = analyze_nma_bayes_raw(rs, cfg)

    return ret


###########################################################
# Test function
###########################################################


def test_nma_bayes_raw():
    '''
    Just for test nma bayes raw
    '''
    cfg = {
        'which_is_better': 'lower',
        'measure_of_effect': 'RR',
        'fixed_or_random': 'random'
    }
    rs = pd.DataFrame(
        [
            ['S1', 'D+ADT', 86, 189],
            ['S1', 'AAP-ADT', 180, 377],
            ['S2', 'AAP-ADT', 443, 955],
            ['S2', 'ADT', 315, 953],
            ['S3', 'AAP-ADT', 411, 597],
            ['S3', 'ADT', 309, 602],
            ['S4', 'E+ADT', 321, 563],
            ['S4', 'NSAA+ADT', 241, 558],
            ['S5', 'APA+ADT', 221, 524],
            ['S5', 'ADT', 215, 527],
            ['S6', 'E+ADT', 139, 572],
            ['S6', 'ADT', 147, 574]
        ], 
        columns=['study', 'treat', 'event', 'total']
    ).to_dict(orient='records')

    ret = analyze_nma_bayes_raw(rs, cfg)

    pprint(ret)

    return ret


def test_nma_bayes_pre():
    '''
    Just for test nma bayes pre
    '''
    cfg = {
        'which_is_better': 'lower',
        'measure_of_effect': 'HR',
        'fixed_or_random': 'fixed',
    }
    rs = pd.DataFrame(
        [
            ['Pembro', 'Placebo', 0.68, 0.53, 0.87, 'S1', 2021],
            ['Suni', 'Placebo', 0.76, 0.59, 0.98, 'S2', 2016],
            ['Sora', 'Placebo', 0.97, 0.80, 1.17, 'S3', 2016],
            ['Pazo', 'Placebo', 0.84, 0.71, 0.99, 'S4', 2017],
            ['Axi', 'Placebo', 0.87, 0.66, 1.15, 'S5', 2018]
        ], 
        columns=['t1', 't2', 'sm','lowerci', 'upperci', 'study', 'year']
    ).to_dict(orient='records')

    ret = analyze_nma_bayes_pre(rs, cfg)

    pprint(ret)

    return ret


def test_nma_bayes_pre_2():
    '''
    Just for test nma bayes pre 2
    '''
    cfg = {
        'which_is_better': 'lower',
        'measure_of_effect': 'HR',
        'fixed_or_random': 'fixed',
    }
    rs = pd.DataFrame(
        [
            ['E_ADT','ADT',0.72,0.47,1.09,'ENZAMET'],
            ['APA_ADT','ADT',0.4,0.15,1.03,'TITAN'],
            ['D_ADT','ADT',0.83,0.47,1.47,'GETUG-AFU15'],
            ['DARO_D_ADT','D_ADT',0.605,0.348,1.052,'ARASENS'],
        ], 
        columns=['t1', 't2', 'sm','lowerci', 'upperci', 'study']
    ).to_dict(orient='records')

    ret = analyze_nma_bayes_pre(rs, cfg)

    pprint(ret)

    return ret


def test_nma_freq_raw():
    '''
    Just for test nma freq raw
    '''
    cfg = {
        'which_is_better': 'lower',
        'measure_of_effect': 'RR',
        'fixed_or_random': 'random'
    }
    rs = pd.DataFrame(
        [
            ['D+ADT', 'AAP-ADT', 86, 189, 180, 377, 'S1', 2021],
            ['AAP-ADT', 'ADT', 443, 955, 315, 953, 'S2', 2016],
            ['AAP-ADT', 'ADT', 411, 597, 309, 602, 'S3', 2016],
            ['E+ADT', 'NSAA+ADT', 321, 563, 241, 558, 'S4', 2017],
            ['APA+ADT', 'ADT', 221, 524, 215, 527, 'S5', 2018],
            ['E+ADT', 'ADT', 139, 572, 147, 574, 'S6', 2018]
        ], 
        columns=['treat1', 'treat2', 'event1','n1', 'event2','n2', 'study', 'year']
    ).to_dict(orient='records')

    ret = analyze_nma_freq_raw(rs, cfg)

    pprint(ret)

    return ret


def test_nma_freq_pre():
    '''
    Just for test nma freq pre
    '''
    cfg = {
        'which_is_better': 'lower',
        'measure_of_effect': 'HR',
        'fixed_or_random': 'fixed',
    }
    rs = pd.DataFrame(
        [
            ['Pembro', 'Placebo', 0.68, 0.53, 0.87, 'S1', 2021],
            ['Suni', 'Placebo', 0.76, 0.59, 0.98, 'S2', 2016],
            ['Sora', 'Placebo', 0.97, 0.80, 1.17, 'S3', 2016],
            ['Pazo', 'Placebo', 0.84, 0.71, 0.99, 'S4', 2017],
            ['Axi', 'Placebo', 0.87, 0.66, 1.15, 'S5', 2018]
        ], 
        columns=['t1', 't2', 'sm','lowerci', 'upperci','study','year']
    ).to_dict(orient='records')

    ret = analyze_nma_freq_pre(rs, cfg)

    pprint(ret)

    return ret


def demo():
    '''
    A demo case for showing how to use rpy2 for NMA
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
    r_forestplt = netmeta.forest_netmeta(r_nma)
    r_j_forestplt = jsonlite.toJSON(r_forestplt, force=True)
    j_forestplt = json.loads(r_j_forestplt[0])

    # the rank
    if cfg['which_is_better'] == 'lower' or \
       cfg['which_is_better'] == 'small':
        small_values = 'good'
    else:
        small_values = 'bad'

    r_rank = netmeta.netrank(
        r_nma, 
        small_values = small_values
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


if __name__ == '__main__':
    demo()