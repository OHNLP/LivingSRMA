import PythonMeta as PMA



def analyze(rs, cfg):
    '''
    PWMA Analyze the given records with configs
    '''
    pass



def get_pma(dataset, datatype='CAT_RAW', 
    sm='RR', method='MH', fixed_or_random='random'):
    '''
    Get the PMA results
    The input dataset should follow:

    [Et, Nt, Ec, Nc, Name 1],
    [Et, Nt, Ec, Nc, Name 2], ...

    for example:

    dataset = [
        [41, 522, 59, 524, 'A'], 
        [8, 203, 18, 203, 'B']
    ]
    '''
    meta = PMA.Meta()
    meta.datatype = 'CATE' if datatype == 'CAT_RAW' else 'CATE'
    meta.models = fixed_or_random.capitalize()
    meta.algorithm = method
    meta.effect = sm
    rs = meta.meta(dataset)

    ret = {
        "model": {
            'measure': rs[0][0],
            'sm': rs[0][1],
            'lower': rs[0][3],
            'upper': rs[0][4],
            'total': rs[0][5],
            'i2': rs[0][9],
            'tau2': rs[0][12],
            'q_tval': rs[0][7],
            'q_pval': rs[0][8],
            'z_tval': rs[0][10],
            'z_pval': rs[0][11]
        },
        'stus': []
    }

    # put results of other studies
    for i in range(1, len(rs)):
        r = rs[i]
        ret['stus'].append({
            'name': r[0],
            'sm': r[1],
            'lower': r[3],
            'upper': r[4],
            'total': r[5],
            'w': r[2] / rs[0][2],
        })
    
    return ret