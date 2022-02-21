import copy
from lnma import settings
from lnma import util
from lnma.analyzer import rpy2_pwma_analyzer as pwma_analyzer
from lnma.analyzer import rpy2_nma_analyzer as nma_analyzer
# from lnma.analyzer import nma_analyzer


def get_nma(extract, paper_dict, is_skip_unselected=True):
    '''
    Get the NMA result in the given extract with paper dict

    The NMA result may be complex depends on the given input

    Returns

    A list of results:

    [
        {
            'rs': rs,
            'cfg': cfg,
            'result':
        },
        ...
    ]    
    '''
    # double check the type
    if extract.oc_type != 'nma':
        return None

    # get the input_format
    # input_format affect the way of calc
    input_format = extract.meta['input_format']

    if input_format not in settings.INPUT_FORMAT_TPL['nma']:
        # what??? how could it be??
        print('* unknown input_format %s for NMA' % input_format)
        return None

    # treatments
    treat_list = extract.get_treatments_in_data()

    # the second, build the rs
    rscfg = extract.get_raw_rs_cfg(
        paper_dict, 
        is_skip_unselected=is_skip_unselected
    )

    # may use it in future
    rscfg_hash = util.hash_json(rscfg)
    rs = rscfg['rs']
    cfg = rscfg['cfg']

    # update the config for R script
    cfg['backend'] = extract.meta['analysis_method']
    cfg['reference_treatment'] = treat_list[0]

    # the R script use different param
    cfg["which_is_better"] = 'small' if extract.meta['which_is_better'] == 'lower' else 'big',

    # 2022-02-20: no need to change this,
    # since all the format convert has been done in the model level.
    # in the Extract._get_rs_nma(), the format will be changed automatically.
    cfg['format_converted'] = 'yes'

    # cfg = {
    #     # for init analyzer
    #     "backend": extract.meta['analysis_method'],
    #     "analysis_method": extract.meta['analysis_method'],
    #     "input_format": input_format,
    #     "reference_treatment": treat_list[0],
    #     "measure_of_effect": extract.meta['measure_of_effect'],
    #     "fixed_or_random": extract.meta['fixed_or_random'],
        
    #     # a special rule for database format
    #     # 2022-02-20: no need to change this,
    #     # since all the format convert has been done in the model level.
    #     # in the Extract._get_rs_nma(), the format will be changed automatically.
    #     'format_converted': 'yes'
    # }
    ret_nma = nma_analyzer.analyze(
        rs, 
        cfg
    )

    # maybe more than one results?
    results = []
    results.append({
        'rs': rs,
        'cfg': cfg,
        'rst': ret_nma
    })

    return results
        

def get_pma(extract, paper_dict, is_skip_unselected=True):
    '''
    Get the PMA result in the given extract with paper dict

    The pma result may be complex depends on the given input

    Returns

    A list of results:

    [
        {
            'rs': rs,
            'cfg': cfg,
            'result':
        },
        ...
    ]    
    '''
    # double check the type
    if extract.oc_type != 'pwma':
        return None

    # get the input_format
    # input_format affect the way of calc
    input_format = extract.meta['input_format']

    if input_format not in settings.INPUT_FORMAT_TPL['pwma']:
        # what??? how could it be??
        print('* unknown input_format %s for PMA' % input_format)
        return None

    # the second, build the rs
    rscfg = extract.get_raw_rs_cfg(
        paper_dict, 
        is_skip_unselected=is_skip_unselected
    )

    # may use it in future
    rscfg_hash = util.hash_json(rscfg)

    # run pma
    # result = pwma_analyzer.analyze(
    #     rscfg['rs'],
    #     rscfg['cfg']
    # )


    # the return object is a list, which may contains multiple
    # results, e.g., prim, cumu, 
    results = []
    if 'input_format' in rscfg['cfg']:
        if rscfg['cfg']['input_format'] == 'PRIM_CAT_PRE':
            if extract.meta['group'] == 'subgroup':
                # which means this is a subg analysis
                # the parsing is different
                rc = copy.deepcopy(rscfg)
                result = pwma_analyzer.analyze_subg_cat_pre(
                    rc['rs'],
                    rc['cfg']
                )
                results.append({
                    'rs': rc['rs'],
                    'cfg': rc['cfg'],
                    'rst': result
                })

            else:
                rc = copy.deepcopy(rscfg)
                result = pwma_analyzer.analyze_pwma_cat_pre(
                    rc['rs'],
                    rc['cfg']
                )
                results.append({
                    'rs': rc['rs'],
                    'cfg': rc['cfg'],
                    'rst': result
                })

        elif rscfg['cfg']['input_format'] == 'PRIM_CAT_RAW':
            rc = copy.deepcopy(rscfg)
            result = pwma_analyzer.analyze_pwma_cat_raw(
                rc['rs'],
                rc['cfg']
            )
            results.append({
                'rs': rc['rs'],
                'cfg': rc['cfg'],
                'rst': result
            })

            # RAW format also could do incd analysis
            # but by default this option may not be available.
            # so, just put a default value there:
            rc = copy.deepcopy(rscfg)
            if 'incd_measure_of_effect' not in rc['cfg']:
                # set these two to make sure the analysis could be correct
                rc['cfg']['measure_of_effect'] = 'PLOGIT'
                rc['cfg']['incd_measure_of_effect'] = 'PLOGIT'

            result = pwma_analyzer.analyze_pwma_cat_raw_incd(
                rc['rs'],
                rc['cfg']
            )
            results.append({
                'rs': rc['rs'],
                'cfg': rc['cfg'],
                'rst': result
            })

    else:
        # what??? something wrong!
        return None

    # now, let's do some quick patch to the result
    # 1. add the pid to the PMA result stus
    # 2. second thing, I don't have any idea yet.
    for result in results:
        # patch the pid into the result stus
        dict_stu2pid = {}
        for r in result['rs']:
            study = r['study']
            pid = r['pid']
            dict_stu2pid[study] = pid

        # add patch to the prim analysis
        if 'primma' in result['rst']['data']:
            for i, _ in enumerate(result['rst']['data']['primma']['stus']):
                # get the study name which is used for analysis
                study_name = result['rst']['data']['primma']['stus'][i]['name']

                # convert to the pid
                pid = dict_stu2pid[study_name]

                # set the pid to this record
                result['rst']['data']['primma']['stus'][i]['pid'] = pid

        # ok, add patch to the subg result
        if 'subgps' in result['rst']['data']:
            for subg_name in result['rst']['data']['subgps']['subgroups']:
                for i, _ in enumerate(result['rst']['data']['subgps']['subgroups'][subg_name]['stus']):
                    # get the study name which is used for analysis
                    study_name = result['rst']['data']['subgps']['subgroups'][subg_name]['stus'][i]['name']

                    # convert to the pid
                    pid = dict_stu2pid[study_name]

                    # set the pid to this record
                    result['rst']['data']['subgps']['subgroups'][subg_name]['stus'][i]['pid'] = pid


        # add patch to the incidence
        if 'incdma' in result['rst']['data']:
            for i, _ in enumerate(result['rst']['data']['incdma']['stus']):
                # get the study name which is used for analysis
                study_name = result['rst']['data']['incdma']['stus'][i]['name']

                # convert to the pid
                pid = dict_stu2pid[study_name]

                # set the pid to this record
                result['rst']['data']['incdma']['stus'][i]['pid'] = pid

    
    # we only the data part
    return results
    