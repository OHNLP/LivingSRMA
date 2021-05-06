import os
import pathlib

ALLOWED_UPLOAD_EXTENSIONS = {'pdf', 'png', 'jpg'}
ALLOWED_PDF_UPLOAD_EXTENSIONS = {'pdf'}

TMP_FOLDER = '/dev/shm/lnma'
PATH_PUBDATA = 'pubdata'
PATH_PDF_FILES = '/data/lnma/pdfs'
PATH_PDF_FOLDER_FORMAT = '%Y%m%d'

RSCRIPT_TPL_FOLDER = os.path.join(
    os.path.join(pathlib.Path(__file__).parent.absolute(), 'analyzer'),
    'r_tpl'
)

INPUT_FORMATS_HRLU = 'HRLU'
INPUT_FORMATS_FTET = 'FTET'
INPUT_FORMATS_ET = 'ET'

STANDARD_DATA_COLS = {
    # for NMA, the column `hr` could be `sm` or `TE`, the analyzer will handle
    'HRLU': ['study', 't1', 't2', 'hr', 'upperci', 'lowerci'],
    'FTET': ['study', 'treat', 'event', 'total', 'time'],
    'ET': ['study', 'treat', 'event', 'total'],
    
    # for PWMA - SUBGROUP
    'SUBG_CAT_RAW': ['study', 'year', 'Et', 'Nt', 'Ec', 'Nc', 'treatment', 'control', 'subgroup'],
    'SUBG_CAT_PRE': ['study', 'year', 'TE', 'lowerci', 'upperci', 'treatment', 'control', 'subgroup'],
    'SUBG_CONTD_RAW': ['study', 'year', 'Nt', 'Nt', 'SDt', 'Nc', 'Mc', 'SDc', 'treatment', 'control', 'subgroup'],
    'SUBG_CONTD_PRE': ['study', 'year', 'TE', 'SE', 'treatment', 'control', 'subgroup'],
    'SUBG_CATIRR_RAW': ['study', 'year', 'Et', 'Tt', 'Ec', 'Tc', 'treatment', 'control', 'subgroup'],

    # for PWMA - PRIMARY ANALYSIS / SENSITIVITY / CUMULATIVE
    'PRIM_CAT_RAW': ['study', 'year', 'Et', 'Nt', 'Ec', 'Nc', 'treatment', 'control'],
    'PRIM_CAT_PRE': ['study', 'year', 'TE', 'lowerci', 'upperci', 'treatment', 'control'],
    'PRIM_CONTD_RAW': ['study', 'year', 'Nt', 'Mt', 'SDt', 'Nc', 'Mc', 'SDc', 'treatment', 'control'],
    'PRIM_CONTD_PRE': ['study', 'year', 'TE', 'SE', 'treatment', 'control'],
    'PRIM_CATIRR_RAW': ['study', 'year', 'Et', 'Tt', 'Ec', 'Tc', 'treatment', 'control'],

    # for PWMA - Special for IO project
    'PRIM_CAT_RAW_G5': ['study', 'year', 'treatment', 'control', 
                        'GA_Et', 'GA_Nt', 'GA_Ec', 'GA_Nc', 
                        'G34_Et', 'G34_Ec', 
                        'G3H_Et', 'G3H_Ec', 
                        'G5N_Et', 'G5N_Ec', 
                        'drug_used', 'malignancy'],

    # for INCD - Incidence analysis
    'INCD_CAT_RAW': ['study', 'year', 'Et', 'Nt', 'treat']
}

INPUT_FORMAT_NAMES = {
    "PRIM_CAT_PRE": "Categorical Precalculated Data",
    "PRIM_CAT_RAW": "Categorical Raw Data",
    "PRIM_CATIRR_RAW": "Categorical Raw (Incidence Rate Ratios) Data",
    "PRIM_CONTD_PRE": "Continuous Precalculated Data",
    "PRIM_CONTD_RAW": "Continuous Raw Data",
    "PRIM_CAT_RAW_G5": "Categorical Raw Data of Adv Grades (for IO project use only)",
}

SOFTABLE_NMA_COLS = {
    'raw': ['A:D', ['study', 'treat', 'event', 'total' ]],
    'pre': ['A:L', ['t1', 't2', 'sm', 'lowerci', 'upperci', 
                    'study', 
                    'survival in t1', 'survival in t2',
                    'Ec_t1', 'Et_t1', 'Ec_t2', 'Et_t2']]
}

OC_TYPE_TPL = {
    "pwma": {
        "default": {
            "abbr": '',
            "oc_type": 'pwma',
            "category": 'default',
            "group": 'primary',
            "full_name": 'pwma Outcome full name',
            "included_in_plots": 'yes',
            "included_in_sof": 'yes',
            "input_format": 'PRIM_CAT_RAW',
            "measure_of_effect": 'RR',
            "fixed_or_random": 'fixed',
            "which_is_better": 'lower',
            "pooling_method": "Inverse",
            "tau_estimation_method": "DL",
            "hakn_adjustment": "no",
            "smd_estimation_method": "Hedges",
            "prediction_interval": "no",
            "sensitivity_analysis": "no",
            "cumulative_meta_analysis": "no",
            "cumulative_meta_analysis_sortby": "year",
            "attrs": None,
            "cate_attrs": None
        }
    },
    "itable": {
        "default": {
            'abbr': 'itable',
            'oc_type': 'itable',
            'category': 'default',
            'group': 'itable',
            'full_name': 'Interactive Table',
            'input_format': 'custom',
            'filters': [{
                'display_name': 'Included in MA',
                'type': 'radio',
                'attr': 'Included in MA',
                'value': 0,
                'values': [{
                    'display_name': 'All',
                    'value': 0,
                    'sql_cond': "1=1",
                    'default': True
                }]
            }],
            'cate_attrs': [
            {
                'abbr': 'ITABLECAT000',
                'name': "TRIAL CHARACTERISTICS",
                'attrs': [{
                    'abbr': 'ITABLEATT000',
                    'name': 'Phase',
                    'subs': None
                }]
            },
            {
                'abbr': 'ITABLECATSYS',
                'name': "_SYS",
                'attrs': [{
                    'abbr': 'ITABLEECATSYS001',
                    'name': 'URL',
                    'subs': None
                }, {
                    'abbr': 'ITABLEECATSYSSUB002',
                    'name': 'Included in MA',
                    'subs': None
                }]
            }
            ]
        }
    }
}

INPUT_FORMAT_TPL = {
    "pwma": {
        'PRIM_CAT_RAW_G5': [{
            'abbr': 'default',
            'name': 'Regimen',
            'attrs': [{
                'abbr': 'treatment',
                'name': 'Treatment',
                'subs': None
            }, {
                'abbr': 'control',
                'name': 'Control',
                'subs': None
            }]
        },{
            'abbr': 'GA',
            'name': 'All Grade',
            'attrs': [{
                'abbr': 'GA_Et',
                'name': 'Tx',
                'subs': None
            }, {
                'abbr': 'GA_Nt',
                'name': 'N',
                'subs': None
            }, {
                'abbr': 'GA_Ec',
                'name': 'Placebo',
                'subs': None
            }, {
                'abbr': 'GA_Nc',
                'name': 'n',
                'subs': None
            }]
        }, {
            'abbr': 'G34',
            'name': 'Grade 3/4',
            'attrs': [{
                'abbr': 'G34_Et',
                'name': 'Tx',
                'subs': None
            }, {
                'abbr': 'G34_Ec',
                'name': 'Placebo',
                'subs': None
            }]
        }, {
            'abbr': 'G3H',
            'name': 'Grade 3 or higher',
            'attrs': [{
                'abbr': 'G3H_Et',
                'name': 'Tx',
                'subs': None
            }, {
                'abbr': 'G3H_Ec',
                'name': 'Placebo',
                'subs': None
            }]
        }, {
            'abbr': 'G5N',
            'name': 'Grade 5 only',
            'attrs': [{
                'abbr': 'G5N_Et',
                'name': 'Tx',
                'subs': None
            }, {
                'abbr': 'G5N_Ec',
                'name': 'Placebo',
                'subs': None
            }]
        }]
    }
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

    # for incidence analysis
    'incd_INCD_CAT_RAW': 'lnma_incd_INCD_CAT_RAW.tpl.r',

    # for PWMA v2
    'pwma_v2_PRIM_CAT_PRE': 'lnma_pwma_v2_PRIM_CAT_PRE.tpl.r',

    # for NMA
    'nma_freq_CAT_RAW': 'lnma_nma_freq_CAT_RAW.tpl.r',
    'nma_freq_CAT_PRE': 'lnma_nma_freq_CAT_PRE.tpl.r',
    'nma_bayes_CAT_RAW': 'lnma_nma_bayes_CAT_RAW.tpl.r',
    'nma_bayes_CAT_PRE': 'lnma_nma_bayes_CAT_PRE.tpl.r',

    # for NMA v2
    'nma_freq_ET': 'lnma_nma_freq_ET.tpl.r',
    'nma_freq_HRLU': 'lnma_nma_freq_HRLU.tpl.r',
    'nma_bayes_ET': 'lnma_nma_bayes_ET.tpl.r',
    'nma_bayes_HRLU': 'lnma_nma_bayes_HRLU.tpl.r',


    # for R Plots (RPLT)
    #'rplt_IOTOX_FOREST': 'lnma_rplt_IOTOX_FOREST.tpl.r',
    #'rplt_IOTOX_FORESTDATA': 'lnma_rplt_IOTOX_FORESTDATA.tpl.r',
    #'rplt_ALL_PRIM_CAT_RAW': 'lnma_rplt_ALL_PRIM_CAT_RAW.tpl.r',
    'rplt_PWMA_PRCM_CAT_RAW': 'lnma_rplt_PWMA_PRCM_CAT_RAW.tpl.r',
    'rplt_PWMA_INCD_CAT_RAW': 'lnma_rplt_PWMA_INCD_CAT_RAW.tpl.r',
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
        "SMD": "Standardized Mean Difference",

        # incidence analysis
        "PLOGIT": "Logit Transformation",
        "PAS": "Arcsine Transformation ",
        "PFT": "Freeman-Tukey Double Arcsine Transformation",
        "PLN": "Log Transformation",
        "PRAW": "Raw Proportions",
    }
}

PUBWEB_DATAFILES = {
    'concept_image':      'CONCEPT_IMAGE.svg',
    'itable_attr_data':   'ITABLE_ATTR_DATA.xlsx',
    'itable_filters':     'ITABLE_FILTERS.xlsx',
    'softable_pma_data':  'SOFTABLE_PMA_DATA.xlsx',
    'softable_nma_data':  'SOFTABLE_NMA_DATA.xlsx',
    'all_data':           'ALL_DATA.xlsx',
    'prisma_data':        'PRISMA_DATA.xlsx'
}

# the maximum length
PID_TYPE_MAX_LENGTH = 32
PID_TYPE_NONE_TYPE = 'UNKNOWN'

PAPER_PID_MAX_LENGTH = 64
PAPER_PUB_DATE_MAX_LENGTH = 32
PAPER_JOURNAL_MAX_LENGTH = 128

# screening reasons
SCREENER_REASON_INCLUDED_IN_SR_BY_IMPORT_PMIDS = 'User import'


PAPER_STUDY_TYPE_ORIGINAL = 'original'
PAPER_STUDY_TYPE_FOLLOWUP = 'followup'