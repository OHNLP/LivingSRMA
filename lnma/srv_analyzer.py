from lnma import settings
from lnma import util
from lnma.analyzer import rpy2_pwma_analyzer as pwma_analyzer


def get_pma(extract, paper_dict, is_skip_unselected=True):
    '''
    Get the pma result in the given extract with paper dict
    '''
    # double check the type
    if extract.oc_type != 'pwma':
        return None

    # get the input_format
    # input_format affect the way of calc
    input_format = extract.meta['input_format']

    if input_format not in settings.INPUT_FORMAT_TPL['pwma']:
        # what??? how could it be??
        print('* unknown input_format %s' % input_format)
        return None

    # the second, build the rs
    rscfg = extract.get_raw_rs_cfg(
        paper_dict, 
        is_skip_unselected=is_skip_unselected
    )

    # may use it in future
    rscfg_hash = util.hash_json(rscfg)

    # run pma
    result = pwma_analyzer.analyze(
        rscfg['rs'],
        rscfg['cfg']
    )
    
    # we only the data part
    return rscfg['rs'], rscfg['cfg'], result['data']
    