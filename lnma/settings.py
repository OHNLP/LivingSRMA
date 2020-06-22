import os
import pathlib

TMP_FOLDER = '/dev/shm/lnma'

RSCRIPT_TPL_FOLDER = os.path.join(
    os.path.join(pathlib.Path(__file__).parent.absolute(), 'analyzer'),
    'r_tpl'
)

INPUT_FORMATS_HRLU = 'HRLU'
INPUT_FORMATS_FTET = 'FTET'
INPUT_FORMATS_ET = 'ET'

STANDARD_DATA_COLS = {
    # for NMA
    'HRLU': ['study', 't1', 't2', 'hr', 'upperci', 'lowerci'],
    'FTET': ['study', 'treat', 'event', 'total', 'time'],
    'ET': ['study', 'treat', 'event', 'total'],
    # for PWMA - PRIMARY ANALYSIS / SENSITIVITY / CUMULATIVE
    'PRIM_CAT_RAW': ['study', 'year', 'et', 'tt', 'ec', 'tc', 'treatment', 'control'],
    'PRIM_CAT_PRE': ['study', 'year', 'te', 'lowerci', 'upperci', 'treatment', 'control'],
    'PRIM_CONTD_RAW': ['study', 'year', 'nt', 'mt', 'sdt', 'nc', 'mc', 'sdc', 'treatment', 'control'],
    'PRIM_CONTD_PRE': ['study', 'year', 'te', 'se', 'treatment', 'control'],
    # for PWMA - SUBGROUP
    'SUBG_CAT_RAW': ['study', 'year', 'et', 'tt', 'ec', 'tc', 'treatment', 'control', 'subgroup'],
    'SUBG_CAT_PRE': ['study', 'year', 'te', 'lowerci', 'upperci', 'treatment', 'control', 'subgroup'],
    'SUBG_CONTD_RAW': ['study', 'year', 'nt', 'mt', 'sdt', 'nc', 'mc', 'sdc', 'treatment', 'control', 'subgroup'],
    'SUBG_CONTD_PRE': ['study', 'year', 'te', 'se', 'treatment', 'control', 'subgroup'],
}

RSCRIPT_TPL = {
    # for frequentist NMA
    'freq_pairwise_netmeta': 'lnma_freq_pairwise_netmeta.tpl.r',
    'freq_netmeta': 'lnma_freq_netmeta.tpl.r',

    # for Bayesian NMA
    'bayes_bugsnet': 'lnma_bayes_bugsnet.tpl.r',
    'bayes_dmetar': 'lnma_bayes_dmetar.tpl.r',
    'bayes_gemtc': 'lnma_bayes_gemtc.tpl.r'
}

R_BUGSNET_MEASURE2LINK = {
    'hr': 'cloglog',  # Hazard Ratio
    'rr': 'log',      # Risk Ratio
    'or': 'logit'     # Odds Ratio
}

TPL_FN = {
    'rscript': 'rscript-{subtype}-{submission_id}.r',
    'csvfile': 'csvfile-{subtype}-{submission_id}.csv',
    'jsonret': 'jsonret-{subtype}-{submission_id}.json',
    'leaguet': 'leaguet-{subtype}-{submission_id}.png',
}