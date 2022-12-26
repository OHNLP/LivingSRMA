#%% load packages
import json
import math
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

from lnma.analyzer.rpadapter import _meta_trans_metabin_subg
from lnma.analyzer.rpadapter import _meta_trans_metagen_subg
from lnma.analyzer import coe_helper


#%% load R packages
meta = importr('meta')
pwr = importr('pwr')
jsonlite = importr('jsonlite')

def calc_OIS_by_p1(p1):
    '''Calculate OIS by p1 value

    @param p1: p1 is Et/Nt

    For OIS, we need a baseline risk (that should come from the included studies) 
    and a plausible RRR (usually we use 25%, which is RR of 0.75).
    Thus, we do not use the RR from the meta-analysis or 2x2 table from the meta-analysis.
    '''
    p2 = 0.75 * p1
    h = 2 * math.asin(math.sqrt(p1)) - 2*math.asin(math.sqrt(p2))
    return calc_OIS(h)


def calc_OIS(h, alpha=0.05, power=0.8, alternative='two.sided'):
    '''Calculate OIS by R pwr
    '''
    r = pwr.pwr_2p_test(
        h=h,
        sig_level=alpha,
        power=power,
        alternative=alternative
    )
    # convert r to dict
    r_dict = dict(zip(r.names, list(r)))
    # fix the numpy.int64 encoder bug
    n = int(r_dict['n'][0])

    return n * 2


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
    return j


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
    return j


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
        df.Et, 
        df.Nt, 
        df.Ec, 
        df.Nc,
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
    # print(r_j_prim)

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
            'primma': _meta_trans_metagen(j, cfg),
            'subgps': _meta_trans_metagen_subg(j, cfg)
        }
    }

    return ret


def analyze_subg_cat_raw(rs, cfg):
    '''
    Analyze the subgroup of Categorical Raw Data

    The given rs should contains:

    study, Et, Nt, Ec, Nc, subgroup
    '''
    # create a dataframe first
    df = pd.DataFrame(rs)

    # get the primary
    r_subgrst = meta.metabin(
        df.Et, 
        df.Nt, 
        df.Ec, 
        df.Nc,
        studlab=df.study,
        byvar=df.subgroup,
        comb_random=cfg['fixed_or_random']=='random',
        sm=cfg['measure_of_effect'],
        hakn=True if cfg['hakn_adjustment'] == 'TRUE' else False,
        method=cfg['pooling_method'],
        method_tau=cfg['tau_estimation_method']
    )

    # convert to R json object
    r_j_subgrst = jsonlite.toJSON(r_subgrst, force=True)

    # convert to Python JSON object
    j_subgrst = json.loads(r_j_subgrst[0])

    # for compability
    j = {
        'primma': j_subgrst
    }

    # build the return
    ret = {
        'submission_id': 'rpy2',
        'params': cfg,
        'success': True,
        'data': {
            'primma': _meta_trans_metabin(j, cfg),
            'subgps': _meta_trans_metabin_subg(j, cfg)
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


def analyze_pwma_prcm_coe(rs, cfg, has_cumu=True):
    '''
    Analyze the primary and cumulative and CoE

    Make sure the rs is like:
      {
        "study": "Raskob et al",
        "year": 2017,
        "Et": 41,
        "Nt": 522,
        "Ec": 59,
        "Nc": 524,
        "pid": "1234",
        "rob": "L", # L, M, H, NA
        "ind": "V", # V, M, N, NA
    },
    '''
    # create a dataframe first
    df = pd.DataFrame(rs)

    # the sum of Et and Nt
    ttEt = df.Et.sum()
    ttNt = df.Nt.sum()
    ttEc = df.Ec.sum()
    ttNc = df.Nc.sum()

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
    # r_d_prim = dict(zip(r_prim.names, list(r_prim)))

    # get the trimfill primary
    r_prim_trimfill = meta.trimfill_meta(r_prim)

    # get the bias
    r_bias = meta.metabias(
        r_prim,
        method = 'linreg'
    )

    # convert to R json object
    r_j_prim = jsonlite.toJSON(r_prim, force=True)
    # get adjusted effect
    r_j_prim_trimfill = jsonlite.toJSON(r_prim_trimfill, force=True)
    # get bias information
    r_j_bias = jsonlite.toJSON(r_bias, force=True)

    # convert to Python JSON object
    j_prim = json.loads(r_j_prim[0])
    j_prim_trimfill = json.loads(r_j_prim_trimfill[0])
    j_bias = json.loads(r_j_bias[0])

    # for compability
    j = {
        'primma': j_prim,
    }
    # get adjusted effect for compability
    j_trimfill = {
        'primma': j_prim_trimfill,
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

    # update the format for easier usage
    primma = _meta_trans_metabin(j, cfg)
    # get adjusted effect
    primma_trimfill = _meta_trans_metabin(j_trimfill, cfg)

    #######################################################
    # Risk of Bias
    #######################################################
    # get the everything that needed first
    # get number of NA studies
    n_rob_na = len(df[df['rob']=='NA'])

    # only use those with non-NA records
    dft = df[df['rob']!='NA']

    # get all robs of non-NA 
    robs = dft.rob.to_list()

    # set default for these two
    is_all_low = True
    for r in robs:
        if r != 'L':
            # ok, not all low
            is_all_low = False
            break
    
    # get all high
    is_all_high = True
    for r in robs:
        if r != 'H' and r != 'M':
            # this record is not H and not M, must be L or NA
            is_all_high = False
            break

    # get percentage of high
    per_high_stus = None
    if len(robs) != 0:
        per_high_stus = 0
        for r in robs:
            if r == 'H':
                per_high_stus += 1
        # the percentage of high-risk
        per_high_stus = per_high_stus / len(robs)

    # get subg if needed
    j_subg = None
    subg_pval = None
    if is_all_high:
        # then no need to further check, just eval
        pass

    else:
        # add a subgroup column for df
        dft['subgroup'] = dft['rob'].apply(lambda v: 'L' if v == 'L' else 'H')
        r_subg = meta.metabin(
            dft.Et, dft.Nt, dft.Ec, dft.Nc,
            studlab=dft.study,
            comb_random=cfg['fixed_or_random']=='random',
            sm=cfg['measure_of_effect'],
            hakn=True if cfg['is_hakn'] == 'TRUE' else False,
            method=cfg['pooling_method'],
            method_tau=cfg['tau_estimation_method'],
            byvar=dft.subgroup
        )
        r_j_subg = jsonlite.toJSON(r_subg, force=True)
        j_subg = json.loads(r_j_subg[0])
        subg_pval = j_subg['pval.Q.b.random'][0]

    rob_vals = {
        'n_rob_na': n_rob_na,
        'is_all_low': is_all_low,
        'is_all_high': is_all_high,
        'subg_pval': subg_pval,
        'per_high_stus': per_high_stus,
        'user_judgement': cfg.get('rob_user_judgement', None)
    }

    risk_of_bias = coe_helper.judge_risk_of_bias(rob_vals)

    #######################################################
    # Imprecision
    #######################################################
    # get the relative effect of this pwma
    pma_pooled_effect = primma['model']['random']['bt_TE']
    # get the ci of sm
    ci_of_sm = [
        primma['model']['random']['bt_lower'],
        primma['model']['random']['bt_upper']
    ]
    # get a flag for relative effect
    is_relative_effect_large = bool(pma_pooled_effect < 0.7 or pma_pooled_effect > 1.3)

    # the propotion of treatment group
    p1 = float(ttEt / ttNt)
    # get the OIS
    OIS = calc_OIS_by_p1(p1)
    # get the MA size
    ma_size = int(ttNt + ttNc)

    # get rd by PMA
    r_pma_imp = meta.metabin(
        df.Et, df.Nt, df.Ec, df.Nc,
        studlab=df.study,
        comb_random=cfg['fixed_or_random']=='random',
        sm='RD',
        hakn=True if cfg['is_hakn'] == 'TRUE' else False,
        method=cfg['pooling_method'],
        method_tau=cfg['tau_estimation_method']
    )
    # convert to a dictionary for getting values
    r_d_pma_imp = dict(zip(r_pma_imp.names, list(r_pma_imp)))
    # get RD, and RD doesn't require backtransf
    imp_rd = float(r_d_pma_imp['TE.random'][0])
    # get the confidence interval of RD
    ci_of_rd = [
        float(r_d_pma_imp['lower.random'][0]),
        float(r_d_pma_imp['upper.random'][0])
    ]
    imp_t = cfg['imp_t']

    # judge the T included in ci or not
    # use bool() to fix numpy.bool_ bug
    is_t_included_in_ci_of_rd = bool(imp_t >= ci_of_rd[0] and imp_t <= ci_of_rd[1])
    # judge the -T and +T
    is_both_ts_included_in_ci_of_rd = bool(is_t_included_in_ci_of_rd and \
        -imp_t >= ci_of_rd[0] and -imp_t <= ci_of_rd[1])
    # judge the 200 per 1000
    is_both_200p1000_included_in_ci_of_rd = bool( \
        -0.2 >= ci_of_rd[0] and -0.2 <= ci_of_rd[1] and \
        0.2 >= ci_of_rd[0] and 0.2 <= ci_of_rd[1])

    imp_vals = {
        't': imp_t,
        'is_t_user_provided': cfg['is_t_user_provided'],
        'sm': pma_pooled_effect,
        'ci_of_sm': ci_of_sm,
        'is_relative_effect_large': is_relative_effect_large,
        'p1': p1,
        'rd': imp_rd,
        'ci_of_rd': ci_of_rd,
        'is_t_included_in_ci_of_rd': is_t_included_in_ci_of_rd,
        'is_both_ts_included_in_ci_of_rd': is_both_ts_included_in_ci_of_rd,
        'is_both_200p1000_included_in_ci_of_rd': is_both_200p1000_included_in_ci_of_rd,
        'ois': OIS,
        'ma_size': ma_size
    }
    imprecision = coe_helper.judge_imprecision(imp_vals)

    #######################################################
    # Publication Bias
    #######################################################
    # get the publication_bias
    n_studies = j_prim['k'][0]
    egger_test_p_value = j_bias['p.value'][0] if 'p.value' in j_bias else None
    pooled_sm = primma['model']['random']['bt_TE']
    adjusted_sm = primma_trimfill['model']['random']['bt_TE']
    difference_sm = adjusted_sm - pooled_sm

    pbb_vals = {
        'n_studies': n_studies,
        'egger_test_p_value': egger_test_p_value,
        'pooled_sm': pooled_sm,
        'adjusted_sm': adjusted_sm,
        'difference_sm': difference_sm
    }

    publication_bias = coe_helper.judge_publication_bias(pbb_vals)

    #######################################################
    # Inconsistency
    #######################################################
    # get the inconsistency
    i2 = primma['heterogeneity']['i2']
    heter_pval = primma['heterogeneity']['p']
    
    # get category
    # so, get the SM for all studies first
    df_inc = pd.DataFrame(primma['stus'])
    def _get_sm_cate(v):
        if v>= 0.9:   return 'T' # Trivial
        elif v>= 0.8: return 'S' # Small
        elif v>= 0.5: return 'M' # Moderate
        else:         return 'L' # large
    df_inc['sm_cate'] = df_inc['bt_TE'].apply(_get_sm_cate)
    pooled_sm_cate = _get_sm_cate(primma['model']['random']['bt_TE'])
    df_inc_stat = df_inc[['name', 'sm_cate']] \
        .groupby(by=['sm_cate'])['name'] \
        .count() \
        .sort_values(ascending=False) \
        .reset_index()
    # get the top major cate and number
    major_sm_cate = df_inc_stat.iloc[0]['sm_cate']
    major_sm_cnt = int(df_inc_stat.iloc[0]['name'])

    # count the cate
    is_major_in_same_category = \
        pooled_sm_cate == major_sm_cate and \
        major_sm_cnt >= 0.75 * len(df)

    inc_vals = {
        'i2': i2,
        'heter_pval': heter_pval,
        'pooled_sm_cate': pooled_sm_cate,
        'major_sm_cate': major_sm_cate,
        'major_sm_cnt': major_sm_cnt,
        'is_major_in_same_category': is_major_in_same_category,
    }
    inconsistency = coe_helper.judge_inconsistency(inc_vals)


    #######################################################
    # Indirectness
    #######################################################
    n_very_close = len(df[df['ind']=='V'])
    percentage_very_close = n_very_close / n_studies
    n_moderately_close = len(df[df['ind']=='M'])
    n_not_close = len(df[df['ind']=='N'])
    n_ind_na = len(df[df['ind']=='NA'])

    ind_vals = {
        "n_very_close": n_very_close,
        "percentage_very_close": percentage_very_close,
        "n_moderately_close": n_moderately_close,
        "n_not_close": n_not_close,
        "n_ind_na": n_ind_na,
        "n_studies": n_studies
    }

    indirectness = coe_helper.judge_indirectness(ind_vals)

    #######################################################
    # FINALLY! the return object
    #######################################################

    # build the return
    ret = {
        'submission_id': 'rpy2',
        'params': cfg,
        'success': True,
        'data': {
            'primma': primma,
            'raw': {
                'prim': j_prim,
                'bias': j_bias,
                'subg_by_rob': j_subg
            },
            'coe': {
                'risk_of_bias': risk_of_bias,
                'inconsistency': inconsistency,
                'publication_bias': publication_bias,
                'imprecision': imprecision,
                'indirectness': indirectness,

                'info': {
                    'risk_of_bias': rob_vals,
                    'inconsistency': inc_vals,
                    'publication_bias': pbb_vals,
                    'imprecision': imp_vals,
                    'indirectness': ind_vals
                }
            }
        }
    }

    # add cumu info
    if has_cumu:
        ret['data']['cumuma'] = _meta_trans_metacum(j, cfg)
        ret['data']['raw']['cumu'] = j_cumu

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

    # get the bias
    r_bias = meta.metabias(
        r_prim,
        method = 'linreg'
    )

    # convert to R json object
    r_j_prim = jsonlite.toJSON(r_prim, force=True)
    r_j_bias = jsonlite.toJSON(r_bias, force=True)

    # convert to Python JSON object
    j_prim = json.loads(r_j_prim[0])
    j_bias = json.loads(r_j_bias[0])

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
            'primma': _meta_trans_metabin(j, cfg),
            'raw': {
                'prim': j_prim,
                'bias': j_bias
            },
            'coe': {}
        }
    }
    if has_cumu:
        ret['data']['cumuma'] = _meta_trans_metacum(j, cfg)
        ret['data']['raw']['cumu'] = j_cumu

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


###########################################################
# Test function
###########################################################

def test_subg_cat_raw():
    '''
    Just for test pwma subg cat raw
    '''
    cfg = {
        'which_is_better': 'lower',
        'measure_of_effect': 'OR',
        'fixed_or_random': 'fixed',
        'hakn_adjustment': 'TRUE',
        'pooling_method': 'Inverse',
        'tau_estimation_method': 'DL'
    }
    rs = pd.DataFrame(
        [
            ['DOACs', 'LMWH', 20, 277, 10, 263, 'Male', 'S1'],
            ['DOACs', 'LMWH', 16, 245, 11, 261, 'Female', 'S1'],
            ['DOACs', 'LMWH', 12, 292, 13, 276, 'Male', 'S2'],
            ['DOACs', 'LMWH', 10, 284, 10, 303, 'Female', 'S2'],
        ], 
        columns=['treatment', 'control', 'Et','Nt', 'Ec', 'Nc', 'subgroup', 'study']
    ).to_dict(orient='records')

    ret = analyze_subg_cat_raw(rs, cfg)

    # pprint(ret)

    return ret


if __name__ == '__main__':
    demo()