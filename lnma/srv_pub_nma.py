import os
import json

from tqdm import tqdm

from flask import current_app

# from lnma.analyzer import rpy2_pwma_analyzer as pwma_analyzer
from lnma.analyzer import nma_analyzer
from lnma import dora, srv_analyzer
from lnma import util
from lnma import ss_state
from lnma import settings
from lnma import db

from lnma import srv_paper


def get_graph_nma_data_from_db(keystr, cq_abbr):
    '''
    Get the NMA graph data
    '''
    # get basic information
    project = dora.get_project_by_keystr(keystr)

    if project is None:
        return None

    papers = srv_paper.get_included_papers_by_cq(
        project.project_id, cq_abbr
    )
    print('* found %s papers included in %s-%s' % (
        len(papers), keystr, cq_abbr
    ))
    # make a dictionary for lookup
    paper_dict = {}
    rs = []
    for paper in papers:
        paper_dict[paper.pid] = paper
        rs.append(paper.as_quite_simple_dict())

    # Then, we need to build the oc_list for the navigation
    extracts = dora.get_extracts_by_keystr_and_cq_and_oc_type(
        keystr, 
        cq_abbr, 
        'nma'
    )
    print('* found %s extracts defined in %s-%s' % (
        len(extracts), keystr, cq_abbr
    ))

    # OK, let's check each outcome
    ret = {
        'oc_dict': {},
        'graph_dict': {}
    }
    for extract in tqdm(extracts):
        oc_name = extract.abbr

        # create an oc object for ... what?
        treat_list = extract.meta['treatments']
        input_format = settings.INPUT_FORMATS_HRLU
        if extract.meta['input_format'] == 'NMA_RAW_ET':
            input_format = settings.INPUT_FORMATS_ET

        oc = {
            "oc_method": extract.meta['analysis_method'],
            "oc_name": extract.abbr,
            "oc_fullname": extract.meta['full_name'],
            "oc_measures": [extract.meta['measure_of_effect']],
            "oc_datatype": input_format,
            "param": {
                "analysis_method": extract.meta['analysis_method'],
                "fixed_or_random": extract.meta['fixed_or_random'],
                "which_is_better": extract.meta['which_is_better']
            },
            "treat_list": treat_list
        }
        ret['oc_dict'][extract.abbr] = oc

        # build rs and cfg
        cfg = {
            # for init analyzer
            "backend": extract.meta['analysis_method'],
            "input_format": input_format,
            "reference_treatment": treat_list[0],
            "measure_of_effect": extract.meta['measure_of_effect'],
            "fixed_or_random": extract.meta['fixed_or_random'],
            "which_is_better": 'small' if extract.meta['fixed_or_random'] == 'lower' else 'big',

            # a special rule for database format
            'format_converted': 'yes'
        }
    
        # get the rs for this oc
        rscfg = extract.get_raw_rs_cfg(
            paper_dict, 
            is_skip_unselected=True
        )
        rs = rscfg['rs']

        # calc!
        ret_nma = nma_analyzer.analyze(rs, cfg)

        # put in result
        ret['graph_dict'][oc_name] = ret_nma

    return ret