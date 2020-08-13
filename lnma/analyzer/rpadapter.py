import re
import math

import numpy as np

TPN_NETMETA_LGTB_VALUES = r"(\-?\d+\.\d+)\s+\((\-?\d+\.\d+)\;\s+(\-?\d+\.\d+)\)"


###############################################################
# Adpaters for BUGSnet
###############################################################

def _bugsnet_trans_netcha(arr, params):
    '''
    Transform the network.char into netcha format request by the client
    '''
    ret = []
    for v in arr:
        ret.append({
            'cha': v['Characteristic'],
            'val': v['Value']
        })
    
    return ret

def _bugsnet_trans_league(arr, params):
    '''
    '''
    cols = []
    tb = {}
    all_stats = []

    for v in arr:
        t = v['Treatment']
        c = v['Comparator']
        if t not in cols: cols.append(t)
        if c not in tb: tb[c] = { 'row': c, 'stat': [], 'lci': [], 'uci': [], 'star': []}

        tb[c]['stat'].append(v['median'])
        all_stats.append(v['median'])
        tb[c]['lci'].append(v['lci'])
        tb[c]['uci'].append(v['uci'])
        tb[c]['star'].append('')

    ret = {
        'n': len(cols),
        'cols': cols,
        'tabledata': [ tb[r] for r in tb ],
        'backend': 'bugsnet',
        'fig_fn': params['fn_leaguet'],
        'min_max': [min(all_stats), max(all_stats)]
    }

    return ret

def _bugsnet_trans_netplt(arr, params):
    '''
    Transform to network plot data format
    '''
    nodes = {}
    links = []

    for c in arr:
        ts = c['comparison'].split('vs.')
        t1 = ts[0].strip()
        t2 = ts[1].strip()

        if t1 not in nodes: nodes[t1] = { 'name': t1, 'value': 0}
        if t2 not in nodes: nodes[t2] = { 'name': t2, 'value': 0}

        nodes[t1]['value'] += c['n.studies']
        nodes[t2]['value'] += c['n.studies']

        links.append({
            'source': t1,
            'target': t2,
            'value': c['n.studies']
        })

    ret = {
        'nodes': [ nodes[t] for t in nodes ],
        'links': links,
        'backend': 'bugsnet'
    }
    return ret


def _bugsnet_trans_forest(arr, params):
    ref_treat = params['reference_treatment']
    vals = []
    glb_min = 0
    glb_max = 0
    val_min = 0
    val_max = 0

    for v in arr:
        t = v['Treatment']
        c = v['Comparator']

        if c != ref_treat: continue
        if t == ref_treat: continue

        vals.append({
            'treatment': t,
            'val': v['median'],
            'upper': v['uci'],
            'lower': v['lci']
        })

    # find min and max
    val_min = min([ v['val'] for v in vals])
    val_max = max([ v['val'] for v in vals])
    glb_min = min([ min(v['upper'], v['lower']) for v in vals])
    glb_max = max([ max(v['upper'], v['lower']) for v in vals])

    ret = {
        'title': "Comparison vs '%s'" % params['reference_treatment'],
        'subtitle': "%s Effect Model" % params['fixed_or_random'].title(),
        'sm': params['measure_of_effect'],
        'val_min': val_min,
        'val_max': val_max,
        'glb_min': glb_min,
        'glb_max': glb_max,
        'vals': vals,
        'backend': 'bugsnet'
    }

    return ret 


def _bugsnet_trans_scrplt(arr, params):
    '''
    Transform the SUCRA plot format
    '''
    rst = {}
    for i in range(len(arr) - 1):
        d = arr[i]
        for k in d:
            if k == 'rank': continue
            if k not in rst: rst[k] = { 'name': k, 'vals': []}
            rst[k]['vals'].append(float(d[k]))

    vals = list(rst.values())

    ret = {
        'n_ranks': len(arr) - 1,
        'vals': vals,
        'backend': 'bugsnet'
    }
    return ret


def _bugsnet_trans_rksucra(arr, params):
    rs = []

    ranks = arr[-1]
    for treat in ranks:
        if treat == 'rank' and ranks[treat] == 'SUCRA': continue

        rs.append({
            'treat': treat,
            'value': float(ranks[treat])
        })

    ret = {
        'col': 'sucra',
        'rs': rs,
        'backend': 'bugsnet'
    }
    return ret



###############################################################
# Adpaters for netmeta
###############################################################

def _netmeta_trans_netcha(arr, params):
    n_studies = len(arr['studlab'])
    n_treats = len(arr['trts'])
    n_links = len(arr['designs'])

    ret = [
        { 'cha': 'Number of Interventions', 'val': n_treats},
        { 'cha': 'Number of Studies', 'val': n_studies},
        { 'cha': 'Total Number of Patients in Network', 'val': '-'},
        { 'cha': 'Total Possible Pairwise Comparisons', 'val': n_treats * n_treats // 2},
        { 'cha': 'Total Number of Pairwise Comparisons With Direct Data', 'val': n_links},
        { 'cha': 'Is the network connected?', 'val': 'TRUE'},
        { 'cha': 'Number of Two-arm Studies', 'val': n_studies},
        { 'cha': 'Number of Multi-Arms Studies', 'val': 0},
        { 'cha': 'Number of Studies With No Zero Events', 'val': n_studies},
        { 'cha': 'Number of Studies With At Least One Zero Event', 'val': 0},
        { 'cha': 'Number of Studies with All Zero Events', 'val': 0},
    ]
    return ret


def _netmeta_trans_netplt(arr, params):
    nodes = {}
    links = []
    
    for n in arr['nodes']:
        node_name = n['trts']
        nodes[node_name] = {
            'name': n['trts'],
            'value': 0
        }
    
    for l in arr['edges']:
        nodes[l['treat1']]['value'] += 1
        nodes[l['treat2']]['value'] += 1
        links.append({
            'source': l['treat1'],
            'target': l['treat2'],
            'value': l['n.stud']
        })

    ret = {
        'nodes': list(nodes.values()),
        'links': links,
        'backend': 'netmeta'
    }
    return ret


def _netmeta_trans_forest(arr, params):
    vals = []
    glb_min = 0
    glb_max = 0
    val_min = 0
    val_max = 0

    for t in arr:
        if t['treat'] == params['reference_treatment']: continue

        vals.append({
            'treatment': t['treat'],
            'val': math.exp(t['TE']),
            'upper': math.exp(t['TE'] + t['seTE'] * 1.96),
            'lower': math.exp(t['TE'] - t['seTE'] * 1.96),
        })

    val_min = min([ v['val'] for v in vals])
    val_max = max([ v['val'] for v in vals])
    glb_min = min([ min(v['upper'], v['lower']) for v in vals])
    glb_max = max([ max(v['upper'], v['lower']) for v in vals])

    ret = {
        'title': "Comparison vs '%s'" % params['reference_treatment'],
        'subtitle': "%s Effect Model" % params['fixed_or_random'].title(),
        'sm': params['measure_of_effect'],
        'val_min': val_min,
        'val_max': val_max,
        'glb_min': glb_min,
        'glb_max': glb_max,
        'vals': vals,
        'backend': 'netmeta'
    }

    return ret


def _netmeta_trans_league(arr, params):
    fixed_or_random = params['fixed_or_random']

    n = 0
    cols = arr['seq']
    tb = []
    all_stats = []

    for i, r in enumerate(arr[fixed_or_random]):
        row = cols[i]
        star = []
        stat = []
        uci = []
        lci = []

        for j, v in enumerate(range(1, len(cols) + 1)):
            val = r['V%d' % v]
            star.append('')
            if val == '.':
                stat.append('')
                lci.append('')
                uci.append('')
            elif val in cols:
                stat.append(1)
                lci.append(1)
                uci.append(1)
            else:
                ps = val.split(' ')
                stat.append(float(ps[0]))
                all_stats.append(float(ps[0]))
                lci.append(ps[1][1:-1])
                uci.append(ps[2][0:-1])
            
        tb.append({
            'row': row,
            'star': star,
            'stat': stat,
            'uci': uci,
            'lci': lci,
        })

        n += 1

    ret = {
        'n': n,
        'cols': cols,
        'tabledata': tb,
        'backend': 'netmeta',
        'min_max': [min(all_stats), max(all_stats)]
    }
    return ret
    

def _netmeta_trans_league_r(arr, params):
    fixed_or_random = params['fixed_or_random']

    n = 0
    cols = arr['seq']
    tb = []
    all_stats = []

    for i, r in enumerate(arr[fixed_or_random]):
        row = cols[i]
        star = []
        stat = []
        uci = []
        lci = []

        for j, v in enumerate(range(1, len(cols) + 1)):
            val = r['V%d' % v]
            star.append('')
            if val == '.':
                stat.append('')
                lci.append('')
                uci.append('')
            elif val in cols or i == j:
                stat.append(1)
                lci.append(1)
                uci.append(1)
            else:
                # split won't deal with multiple space
                # will cause issue.
                # ps = val.split(' ')
                # v = float(ps[0])
                # l = float(ps[1][1:-1])
                # u = float(ps[2][0:-1])
                # 06/18/2020: use regex to detect values
                ret = re.findall(TPN_NETMETA_LGTB_VALUES, val)
                if len(ret) == 0:
                    # values not found?
                    v, l, u = 1, 1, 1
                else:
                    # values should be in the first match groups
                    ps = ret[0]
                    print('* found match %s @ [%s, %s]' % (ret, i, j))
                    v = float(ps[0])
                    l = float(ps[1])
                    u = float(ps[2])
                # put them in to 
                stat.append(v)
                all_stats.append(v)
                lci.append(l)
                uci.append(u)
                # fill the upper triangle
                if i > j:
                    # 06/18/2020: fix the bug when v,l,or u == 0
                    tb[j]['stat'][i] = 1.0 / v if v!=0 else 0
                    tb[j]['uci'][i] = 1.0 / l if l!=0 else 0
                    tb[j]['lci'][i] = 1.0 / u if u!=0 else 0
            
        tb.append({
            'row': row,
            'star': star,
            'stat': stat,
            'uci': uci,
            'lci': lci,
        })

        n += 1

    ret = {
        'n': n,
        'cols': cols,
        'tabledata': tb,
        'backend': 'netmeta',
        'min_max': [min(all_stats), max(all_stats)]
    }
    return ret


def _netmeta_trans_pscore(j, params):
    rs = []
    fixed_or_random = params['fixed_or_random']

    for i in range(len(j['myrank'][fixed_or_random])):
        trt = j['myrank']['trts'][i]
        rnk = j['myrank'][fixed_or_random][i]
        rs.append({ 
            'treat': trt, 
            'value': rnk
        })

    ret = {
        'col': 'pscore',
        'rs': rs,
        'backend': 'netmeta'
    }
    return ret


###############################################################
# Adpaters for dmetar
###############################################################

def _dmetar_trans_rksucra(j, params):
    rs = []
    # 04/07/2020: now we know it's not the problem of jsonlite version
    # the issue is caused by the dmetar!!!
    # let's just use the result of probs and do the calculation of sucra
    # the version diff!
    # if j['version']['jsonlite'] == [[1, 6]]:
    #     for r in j['sucrarank']:
    #         rs.append({
    #             'treat': r['_row'],
    #             'value': np.round(float(r['SUCRA']*100), 2)
    #         })
    # elif j['version']['jsonlite'] == [[1, 6, 1]]:
    #     for i in range(len(j['sucraplot']['treats'])):
    #         treat = j['sucraplot']['treats'][i]
    #         value = np.round(j['sucrarank']['SUCRA'][i]*100, 2)
    #         rs.append({
    #             'treat': treat,
    #             'value': value
    #         })
    # else:
    #     for i in range(len(j['sucraplot']['treats'])):
    #         treat = j['sucraplot']['treats'][i]
    #         value = j['sucrarank']['SUCRA'][i]
    #         rs.append({
    #             'treat': treat,
    #             'value': value
    #         })

    a = len(j['sucraplot']['probs'][0])
    n = len(j['sucraplot']['probs'])
    arr = np.array(j['sucraplot']['probs'])
    c = arr.cumsum(axis=1)
    # this how SUCRA is calculated
    if params['which_is_better'] == 'small':
        sucra = 1 - c[:, :(a-1)].sum(axis=1) / (a-1)
    else:
        sucra = c[:, :(a-1)].sum(axis=1) / (a-1)

    sucra = sucra * 100
    sucra = sucra.tolist()
    sucra = [ float('%.2f' % v) for v in sucra ]

    treats = j['sucraplot']['rows']
    rs = [ { 'treat': treats[i], 'value': sucra[i] } for i in range(n) ]
    
    # ok! done!
    ret = {
        'col': 'sucra',
        'rs': rs,
        'backend': 'dmetar'
    }
    return ret


def _dmetar_trans_scrplt(j, params):
    n = len(j['sucraplot']['probs'])
    treats = j['sucraplot']['rows']
    arr = np.array(j['sucraplot']['probs'])
    

    if params['which_is_better'] == 'small':
        arr = np.flip(arr, axis=1)
    else:
        pass
    
    c = arr.cumsum(axis=1)
    c = c * 100
    c = c.tolist()

    vals = [ { \
        'name': treats[i], \
        'vals': [ '%.2f' % v for v in c[i] ], \
        } for i in range(n) ]

    # 04/07/2020: now we know it's not the problem of jsonlite version
    # the issue is caused by the dmetar!!!
    # if j['version']['jsonlite'] == [[1, 6]]:
    #     for r in j['sucrarank']:
    #         treats.append(r['_row'])
    # elif j['version']['jsonlite'] == [[1, 6, 1]]:
    #     for r in j['sucraplot']['treats']:
    #         treats.append(r)

    # d = j['sucraplot']
    # for i in range(len(treats)):
    #     name = treats[i]
    #     vs1 = d['probs'][i]
    #     vs = (np.cumsum(vs1)*100).tolist()
    #     vals.append({
    #         'name': name,
    #         'vals': vs
    #     })
        
    ret = {
        'n_ranks': len(treats),
        'vals': vals,
        'backend': 'bugsnet'
    }
    return ret


###############################################################
# Adpaters for gemtc
###############################################################

def _gemtc_trans_league(arr, params):
    '''
    '''
    cols = [ r['_row'] for r in arr ]
    tb = []
    all_stats = []

    for item in arr:
        t1 = item['_row']
        stat = []
        lci = []
        uci = []
        for t2 in cols:
            if t1 == t2:
                stat.append(1)
                lci.append(1)
                uci.append(1)
            else:
                tmp = item[t2]
                ps = tmp.split(' ')
                val = float(ps[0])
                val_lci = float(ps[1][1: -1])
                val_uci = float(ps[2][:-1])
                stat.append(val)
                lci.append(val_lci)
                uci.append(val_uci)
                # for get the min and max
                all_stats.append(val)

        tb.append({
            'row': t1,
            'stat': stat,
            'lci': lci,
            'uci': uci
        })

    ret = {
        'n': len(cols),
        'cols': cols,
        'tabledata': tb,
        'backend': 'gemtc',
        'min_max': [min(all_stats), max(all_stats)]
    }

    return ret


def _gemtc_trans_forest(arr, params):
    ref_treat = params['reference_treatment']
    cols = [ r['_row'] for r in arr ]
    vals = []
    glb_min = 0
    glb_max = 0
    val_min = 0
    val_max = 0

    for item in arr:
        if item['_row'] != ref_treat: continue

        for col in cols:
            if col == ref_treat: continue
            tmp = item[col]
            ps = tmp.split(' ')
            val = float(ps[0])
            val_lci = float(ps[1][1: -1])
            val_uci = float(ps[2][:-1])
            
            vals.append({
                'treatment': col,
                'val': val,
                'upper': val_uci,
                'lower': val_lci
            })

    # find min and max
    val_min = min([ v['val'] for v in vals])
    val_max = max([ v['val'] for v in vals])
    glb_min = min([ min(v['upper'], v['lower']) for v in vals])
    glb_max = max([ max(v['upper'], v['lower']) for v in vals])

    ret = {
        'title': "Comparison vs '%s'" % params['reference_treatment'],
        'subtitle': "%s Effect Model" % params['fixed_or_random'].title(),
        'sm': params['measure_of_effect'],
        'val_min': val_min,
        'val_max': val_max,
        'glb_min': glb_min,
        'glb_max': glb_max,
        'vals': vals,
        'backend': 'gemtc'
    }

    return ret


def _gemtc_trans_netcha(j, params):
    arr = j['network']
    studies = list(set([ item['study'] for item in arr['data.re']]))
    n_studies = len(studies)
    n_treats = len(arr['treatments'])
    n_links = len(j['data']['t'])

    ret = [
        { 'cha': 'Number of Interventions', 'val': n_treats},
        { 'cha': 'Number of Studies', 'val': n_studies},
        { 'cha': 'Total Number of Patients in Network', 'val': '-'},
        { 'cha': 'Total Possible Pairwise Comparisons', 'val': n_treats * n_treats // 2},
        { 'cha': 'Total Number of Pairwise Comparisons With Direct Data', 'val': n_links},
        { 'cha': 'Is the network connected?', 'val': 'TRUE'},
        { 'cha': 'Number of Two-arm Studies', 'val': n_studies},
        { 'cha': 'Number of Multi-Arms Studies', 'val': 0},
        { 'cha': 'Number of Studies With No Zero Events', 'val': n_studies},
        { 'cha': 'Number of Studies With At Least One Zero Event', 'val': 0},
        { 'cha': 'Number of Studies with All Zero Events', 'val': 0},
    ]
    return ret


def _gemtc_trans_netplt(j, params):
    treats = [ item['id'] for item in j['network']['treatments'] ]
    cmps = j['data']['t']
    nodes = {}
    links = []
    
    for t in treats:
        nodes[t] = {
            'name': t,
            'value': 0
        }
    
    for l in j['data']['t']:
        t1 = treats[l[0] - 1]
        t2 = treats[l[1] - 1]
        nodes[t1]['value'] += 1
        nodes[t2]['value'] += 1
        links.append({
            'source': t1,
            'target': t2,
            'value': 1
        })

    ret = {
        'nodes': list(nodes.values()),
        'links': links,
        'backend': 'gemtc'
    }
    return ret



###############################################################
# Adpaters for IOTOX FOREST plots
###############################################################

def _meta_trans_metabin(j, params):
    '''Convert the metabin result for forest plot
    In IOTOX project, this can be used for primary meta-analysis
    '''
    data = j['primma']
    # first, put the basic values
    ret = {
        'model': {
            'random': {
                'name': 'Random effects model',
                'Et': sum(data['event.e']),
                'Nt': sum(data['n.e']),
                'Ec': sum(data['event.c']),
                'Nc': sum(data['n.c']),
                'TE': data['TE.random'][0],
                'seTE': data['seTE.random'][0],
                'sm': round(np.e ** data['TE.random'][0], 3),
                'lower': round(np.e ** data['lower.random'][0], 3),
                'upper': round(np.e ** data['upper.random'][0], 3),
                'w': 1
            },
            'fixed': {
                'name': 'Fixed effects model',
                'Et': sum(data['event.e']),
                'Nt': sum(data['n.e']),
                'Ec': sum(data['event.c']),
                'Nc': sum(data['n.c']),
                'TE': data['TE.fixed'][0],
                'seTE': data['seTE.fixed'][0],
                'sm': round(np.e ** data['TE.fixed'][0], 3),
                'lower': round(np.e ** data['lower.fixed'][0], 3),
                'upper': round(np.e ** data['upper.fixed'][0], 3),
                'w': 1
            }
        },
        'heterogeneity': {
            'i2': data['I2'][0],
            'tau2': data['tau2'][0],
            'p': data['pval.Q'][0]
        },
        'stus': []
    }
    # second, add all the studies
    stus = data['studlab']
    for i, stu in enumerate(stus):
        ret['stus'].append({
            'name': stu,
            'Et': data['event.e'][i],
            'Nt': data['n.e'][i],
            'Ec': data['event.c'][i],
            'Nc': data['n.c'][i],
            'TE': data['TE'][i],
            'seTE': data['seTE'][i],
            'sm': round(np.e ** data['TE'][i], 3),
            'lower': round(np.e ** data['lower'][i], 3),
            'upper': round(np.e ** data['upper'][i], 3),
            'w.random': round(data['w.random'][i] / np.sum(data['w.random']), 4),
            'w.fixed': round(data['w.fixed'][i] / np.sum(data['w.fixed']), 4)
        })

    return ret
    

def _meta_trans_metacum(j, params):
    '''Convert the metacum result for forest plot
    In IOTOX project, this can be used for cumulative meta-analysis
    '''
    data = j['cumuma']
    # first, put the basic values
    ret = {
        'model': {
            'random': {
                'name': 'Random effects model',
                'TE': data['TE'][-1],
                'seTE': data['seTE'][-1],
                'sm': round(np.e ** data['TE'][-1], 3),
                'lower': round(np.e ** data['lower'][-1], 3),
                'upper': round(np.e ** data['upper'][-1], 3)
            }
        },
        'stus': []
    }
    # second, add all the studies
    stus = data['studlab'][:-2]
    for i, stu in enumerate(stus):
        ret['stus'].append({
            'name': stu,
            'TE': data['TE'][i],
            'seTE': data['seTE'][i],
            'sm': round(np.e ** data['TE'][i], 3),
            'lower': round(np.e ** data['lower'][i], 3),
            'upper': round(np.e ** data['upper'][i], 3)
        })

    return ret