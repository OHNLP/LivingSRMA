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
    # for PWMA - SUBGROUP
    'SUBG_CATIRR_RAW': ['study', 'year', 'Et', 'Tt', 'Ec', 'Tc', 'treatment', 'control', 'subgroup'],
    'SUBG_CAT_RAW': ['study', 'year', 'Et', 'Nt', 'Ec', 'Nc', 'treatment', 'control', 'subgroup'],
    'SUBG_CAT_PRE': ['study', 'year', 'TE', 'lowerci', 'upperci', 'treatment', 'control', 'subgroup'],
    'SUBG_CONTD_RAW': ['study', 'year', 'Nt', 'Nt', 'SDt', 'Nc', 'Mc', 'SDc', 'treatment', 'control', 'subgroup'],
    'SUBG_CONTD_PRE': ['study', 'year', 'TE', 'SE', 'treatment', 'control', 'subgroup'],
    # for PWMA - PRIMARY ANALYSIS / SENSITIVITY / CUMULATIVE
    'PRIM_CATIRR_RAW': ['study', 'year', 'Et', 'Tt', 'Ec', 'Tc', 'treatment', 'control'],
    'PRIM_CAT_RAW': ['study', 'year', 'Et', 'Nt', 'Ec', 'Nc', 'treatment', 'control'],
    'PRIM_CAT_PRE': ['study', 'year', 'TE', 'lowerci', 'upperci', 'treatment', 'control'],
    'PRIM_CONTD_RAW': ['study', 'year', 'Nt', 'Mt', 'SDt', 'Nc', 'Mc', 'SDc', 'treatment', 'control'],
    'PRIM_CONTD_PRE': ['study', 'year', 'TE', 'SE', 'treatment', 'control'],
}

RSCRIPT_TPL = {
    # for frequentist NMA
    'freq_pairwise_netmeta': 'lnma_freq_pairwise_netmeta.tpl.r',
    'freq_netmeta': 'lnma_freq_netmeta.tpl.r',

    # for Bayesian NMA
    'bayes_bugsnet': 'lnma_bayes_bugsnet.tpl.r',
    'bayes_dmetar': 'lnma_bayes_dmetar.tpl.r',
    'bayes_gemtc': 'lnma_bayes_gemtc.tpl.r',

    # for PWMA
    'pwma_PRIM_CAT_PRE': 'lnma_pwma_PRIM_CAT_PRE.tpl.r',
    'pwma_PRIM_CAT_RAW': 'lnma_pwma_PRIM_CAT_RAW.tpl.r',
    'pwma_PRIM_CATIRR_RAW': 'lnma_pwma_PRIM_CATIRR_RAW.tpl.r',
    'pwma_PRIM_CONTD_PRE': 'lnma_pwma_PRIM_CONTD_PRE.tpl.r',
    'pwma_PRIM_CONTD_RAW': 'lnma_pwma_PRIM_CONTD_RAW.tpl.r',
    'pwma_SUBG_CAT_PRE': 'lnma_pwma_SUBG_CAT_PRE.tpl.r',
    'pwma_SUBG_CAT_RAW': 'lnma_pwma_SUBG_CAT_RAW.tpl.r',
    'pwma_SUBG_CATIRR_RAW': 'lnma_pwma_SUBG_CATIRR_RAW.tpl.r',
    'pwma_SUBG_CONTD_PRE': 'lnma_pwma_SUBG_CONTD_PRE.tpl.r',
    'pwma_SUBG_CONTD_RAW': 'lnma_pwma_SUBG_CONTD_RAW.tpl.r',

    # for NMA
    'nma_freq_CAT_RAW': 'lnma_nma_freq_CAT_RAW.tpl.r',
    'nma_bayes_CAT_RAW': 'lnma_nma_bayes_CAT_RAW.tpl.r',

    # for R Plots (RPLT)
    'rplt_IOTOX_FOREST': 'lnma_rplt_IOTOX_FOREST.tpl.r',
    'rplt_IOTOX_FORESTDATA': 'lnma_rplt_IOTOX_FORESTDATA.tpl.r',
    'rplt_ALL_PRIM_CAT_RAW': 'lnma_rplt_ALL_PRIM_CAT_RAW.tpl.r',
}

R_BUGSNET_MEASURE2LINK = {
    'HR': 'cloglog',  # Hazard Ratio
    'RR': 'log',      # Risk Ratio
    'OR': 'logit'     # Odds Ratio
}

TPL_FN = {
    'rscript': 'rscript-{subtype}-{submission_id}.r',
    'csvfile': 'csvfile-{subtype}-{submission_id}.csv',
    'jsonret': 'jsonret-{subtype}-{submission_id}.json',
    'leaguet': 'leaguet-{subtype}-{submission_id}.png',
    'outplt1': 'outplt1-{subtype}-{submission_id}.png',
    'outplt2': 'outplt2-{subtype}-{submission_id}.png',
    'outplt3': 'outplt3-{subtype}-{submission_id}.png',
    'sensplt': 'sensplt-{subtype}-{submission_id}.png',
    'cumuplt': 'cumuplt-{subtype}-{submission_id}.png',
    'fnnlplt': 'fnnlplt-{subtype}-{submission_id}.png',
}

DIS_TEXT = {
    "MOE": {
        "HR": "Hazard Ratio",
        "OR": "Odds Ratio",
        "RR": "Relative Risk",
        "RD": "Risk Difference",
        "IRR": "Incidence Rate Ratio",
        "MD": "Mean Difference",
        "SMD": "Standardized Mean Difference"
    }
}