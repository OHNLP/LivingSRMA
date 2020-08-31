import os
import json
from collections import OrderedDict

from flask import request
from flask import flash
from flask import render_template
from flask import Blueprint
from flask import send_from_directory
from flask import current_app
from flask import jsonify

from flask_login import login_required
from flask_login import current_user

import pandas as pd
import numpy as np

from .analyzer import rplt_analyzer
from .analyzer import nma_analyzer

import PythonMeta as PMA

PATH_PUBDATA = 'pubdata'

bp = Blueprint("pub", __name__, url_prefix="/pub")


@bp.route('/')
def index():
    return render_template('pub.index.html')


@bp.route('/blankindex')
def blankindex():
    return render_template('pub.blankindex.html')


@bp.route('/subindex/<prj>')
def subindex(prj):
    prj_data = {
        'CAT': { 'prj': 'CAT', 'title': 'Cancer Associated Thrombosis'},
        'RCC': { 'prj': 'RCC', 'title': 'Metastatic Renal Cell Cancer'},
    }[prj]
    return render_template('pub.subindex.html', prj_data=prj_data)


@bp.route('/IOTOX.html')
def IOTOX():
    prj = 'IOTOX'
    return render_template('pub.IOTOX.html')


@bp.route('/RCC.html')
def RCC():
    prj = 'RCC'
    # load the graph data
    full_fn = os.path.join(current_app.instance_path, PATH_PUBDATA, prj, 'NMA_LIST.json')
    nma = json.load(open(full_fn))

    return render_template('pub.RCC.html', nma=nma)


@bp.route('/CAT.html')
def CAT():
    prj = 'CAT'
    # load the graph data
    full_fn = os.path.join(current_app.instance_path, PATH_PUBDATA, prj, 'NMA_LIST.json')
    nma = json.load(open(full_fn))

    # load the dma data
    full_fn = os.path.join(current_app.instance_path, PATH_PUBDATA, prj, 'DMA_DATA.xlsx')
    df = pd.read_excel(full_fn)
    dma = OrderedDict()
    for idx, row in df.iterrows():
        dma_type = row['type']
        option_text = row['option_text']
        legend_text = row['legend_text']
        filename = row['filename']
        if dma_type not in dma: dma[dma_type] = {
            '_default_option': option_text
        }
        if option_text not in dma[dma_type]: dma[dma_type][option_text] = {
            'text': option_text,
            'slides': [],
            'fns': []
        }
        # add this img
        dma[dma_type][option_text]['fns'].append({
            'fn': filename,
            'txt': legend_text
        })
        dma[dma_type][option_text]['slides'].append(filename + '$' + legend_text)
    
    return render_template('pub.CAT.html', dma=dma, nma=nma)



@bp.route('/CAT_v2.html')
def CAT_v2():
    prj = 'CAT'
    # load the graph data
    full_fn = os.path.join(current_app.instance_path, PATH_PUBDATA, prj, 'NMA_LIST.json')
    nma = json.load(open(full_fn))

    # load the dma data
    full_fn = os.path.join(current_app.instance_path, PATH_PUBDATA, prj, 'DMA_DATA.xlsx')
    df = pd.read_excel(full_fn)
    dma = OrderedDict()
    for idx, row in df.iterrows():
        dma_type = row['type']
        option_text = row['option_text']
        legend_text = row['legend_text']
        filename = row['filename']
        if dma_type not in dma: dma[dma_type] = {
            '_default_option': option_text
        }
        if option_text not in dma[dma_type]: dma[dma_type][option_text] = {
            'text': option_text,
            'slides': [],
            'fns': []
        }
        # add this img
        dma[dma_type][option_text]['fns'].append({
            'fn': filename,
            'txt': legend_text
        })
        dma[dma_type][option_text]['slides'].append(filename + '$' + legend_text)
    
    return render_template('pub.CAT_v2.html', dma=dma, nma=nma)

###########################################################
# Modules for public page
###########################################################

@bp.route('/prisma.html')
def prisma():
    return render_template('pub.prisma.html')


@bp.route('/prisma_IOTOX.html')
def prisma_IOTOX():
    '''A special PRISMA for IOTOX project
    The looking is different from others
    '''
    return render_template('pub.prisma_IOTOX.html')


@bp.route('/itable.html')
def itable():
    return render_template('pub.itable.html')


@bp.route('/slide.html')
def slide():
    return render_template('pub.slide.html')


@bp.route('/graph_v1.html')
def graph_v1():
    return render_template('pub.graph_v1.html')


@bp.route('/graph_v2.html')
def graph_v2():
    return render_template('pub.graph_v2.html')


@bp.route('/graph_v2_1.html')
def graph_v2_1():
    return render_template('pub.graph_v2_1.html')


@bp.route('/graph_v2_2.html')
def graph_v2_2():
    return render_template('pub.graph_v2_2.html')


@bp.route('/graph_v3.html')
def graph_v3():
    return render_template('pub.graph_v3.html')


@bp.route('/oplot.html')
def oplot():
    return render_template('pub.oplot.html')


@bp.route('/oplot_v2.html')
def oplot_v2():
    return render_template('pub.oplot_v2.html')


@bp.route('/softable_pma.html')
def softable_pma():
    prj = request.args.get('prj')
    if prj == 'IOTOX':
        fn = 'pub.softable_pma_IOTOX.html'
    else:
        fn = 'pub.softable_pma.html'
    return render_template(fn)


@bp.route('/softable_nma.html')
def softable_nma():
    return render_template('pub.softable_nma.html')

###########################################################
# Data services
###########################################################

@bp.route('/graphdata/<prj>/<fn>')
def graphdata(prj, fn):
    '''General data files
    '''
    full_path = os.path.join(current_app.instance_path, PATH_PUBDATA, prj)
    return send_from_directory(full_path, fn)


@bp.route('/graphdata/<prj>/img/<fn>')
def graphdata_img(prj, fn):
    '''get image files of specific project
    '''
    full_path = os.path.join(current_app.instance_path, PATH_PUBDATA, prj, 'img')
    return send_from_directory(full_path, fn)


@bp.route('/graphdata/<prj>/ITABLE.json')
def graphdata_itable_json(prj):
    '''Special rule for the ITABLE.json which does not exist
    '''
    fn = 'ALL_DATA.xlsx'
    full_fn = os.path.join(current_app.instance_path, PATH_PUBDATA, prj, fn)

    # get the cols
    attr_pack = get_attr_pack_from_itable(full_fn)

    # the rows starts from 2nd line are data
    df_h = pd.read_excel(full_fn, skiprows=[0])

    # load file 
    # if full_fn.endswith('csv'):
    #     df = pd.read_csv(full_fn, skiprows=[0])
    # else:
    #     df = pd.read_excel(full_fn, skiprows=[0])
    df = pd.read_excel(full_fn, skiprows=[0])
    rs = json.loads(df.to_json(orient='records'))

    # add the category info for attrs
    attrs = [ {'name': a} for a in df.columns.tolist() ]
    for i in range(len(attrs)):
        name = attrs[i]['name']
        name_parts = name.split('|')
        if len(name_parts) > 1:
            trunk = name_parts[0].strip()
            branch = name_parts[1].strip()
        else:
            trunk = '_'
            branch = name
        attr_id = trunk.upper() + '|' + branch.upper()

        if attr_id in attr_pack['attr_dict']:
            attrs[i].update(attr_pack['attr_dict'][attr_id])
        else:
            attrs[i]['cate'] = 'Other'
            attrs[i]['vtype'] = 'text'
            attrs[i]['trunk'] = trunk
            attrs[i]['branch'] = branch
            attrs[i]['attr_id'] = attr_id

    ret = {
        'rs': rs,
        'attrs': attrs
    }
    # make a copy of this json
    full_output_fn = os.path.join(current_app.instance_path, PATH_PUBDATA, prj, 'ITABLE.json')
    json.dump(ret, open(full_output_fn, 'w'))
    return jsonify(ret)



@bp.route('/graphdata/<prj>/SOFTABLE_PMA.json')
def graphdata_softable_pma_json(prj):
    '''Special rule for the SoF Table PMA which does not exist
    In this function, all the data are stored in ALL_DATA.xlsx
    The first tab is Study characteristics
    The second tab is Adverse events
    From third tab all the events
    '''
    if prj == 'IOTOX':
        fn = 'ALL_DATA.xlsx'
        full_fn = os.path.join(current_app.instance_path, PATH_PUBDATA, prj, fn)
        ret = get_ae_pma_data(full_fn, is_getting_sms=True)
    else:
        fn = 'SOFTABLE_PMA_DATA.xlsx'
        full_fn = os.path.join(current_app.instance_path, PATH_PUBDATA, prj, fn)
        ret = get_ae_pma_data_simple(full_fn)

    return jsonify(ret)



@bp.route('/graphdata/<prj>/SOFTABLE_NMA.json')
def graphdata_softable_nma_json(prj):
    '''Special rule for the SoF Table NMA which does not exist
    In this function, all the data are stored in ALL_DATA.xlsx
    The first tab is Study characteristics
    The second tab is Adverse events
    From third tab all the events
    '''
    fn = 'SOFTABLE_NMA_DATA.xlsx'
    fn_json = 'SOFTABLE_NMA.json'
    full_fn_json = os.path.join(current_app.instance_path, PATH_PUBDATA, prj, fn_json)

    use_cache = request.args.get('use_cache')
    if use_cache == 'yes':
        return send_from_directory(
            os.path.join(current_app.instance_path, PATH_PUBDATA, prj),
            fn_json
        )
    full_fn = os.path.join(current_app.instance_path, PATH_PUBDATA, prj, fn)
    ret = get_ae_nma_data(full_fn)

    # cache the result
    json.dump(ret, open(full_fn_json, 'w'))

    return jsonify(ret)



@bp.route('/graphdata/<prj>/OPLOTS.json')
def graphdata_oplots(prj):
    '''Special rule for the OPLOTS.json which does not exist
    
    The input file is OPLOTS.xls with multiple sheets

    S.1: Adverse events
    S.2: ?
    S.3: All SEs
    S.4: AE_NAME_1 
    S.n: AE_NAME_2

    '''
    fn = 'ALL_DATA.xlsx'
    full_fn = os.path.join(current_app.instance_path, PATH_PUBDATA, prj, fn)
    ret = get_ae_pma_data(full_fn, is_getting_sms=False)

    return jsonify(ret)

###########################################################
# Other utils
###########################################################

def get_attr_pack_from_itable(full_fn):
    # read data, hope it is xlsx format ...
    if full_fn.endswith('csv'):
        df = pd.read_csv(full_fn, header=None, nrows=2)
    else:
        df = pd.read_excel(full_fn, header=None, nrows=2)

    # convert to other shape
    dft = df.T
    df_attrs = dft.rename(columns={0: 'cate', 1: 'name'})

    # not conver to tree format
    attr_dict = {}
    attr_tree = {}

    for idx, row in df_attrs.iterrows():
        vtype = 'text'
        name = row['name'].strip()
        cate = row['cate'].strip()

        # split the name into different parts
        name_parts = name.split('|')
        if len(name_parts) > 1:
            trunk = name_parts[0].strip()
            branch = name_parts[1].strip()
        else:
            trunk = '_'
            branch = name
        attr_id = trunk.upper() + '|' + branch.upper()

        if cate not in attr_tree: attr_tree[cate] = {}
        if trunk not in attr_tree[cate]: attr_tree[cate][trunk] = []

        attr = {
            'name': name,
            'cate': cate,
            'vtype': vtype,
            'trunk': trunk,
            'branch': branch,
            'attr_id': attr_id,
        }

        # put this item into dict
        attr_tree[cate][trunk].append(attr)
        attr_dict[attr_id] = attr

    return { 'attr_dict': attr_dict, 'attr_tree': attr_tree }


def get_pma(dataset, datatype='CAT_RAW', sm='OR', method='MH', random_or_fixed='random', ):
    '''Get the PMA results
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
    meta.models = random_or_fixed.capitalize()
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


def get_nma_by_r(dataset, datatype='CAT_RAW', sm='OR', random_or_fixed='random'):
    '''Get the NMA results by R script 
    '''
    ret = {

    }
    return ret


def get_pma_by_rplt(dataset, datetype='CAT_RAW', sm='OR', method='MH', random_or_fixed='random'):
    '''Get the PMA results by R script (PRIM_CAT_RAW)
    The input dataset should follow:

    [Et, Nt, Ec, Nc, Name 1],
    [Et, Nt, Ec, Nc, Name 2], ...

    for example:

    dataset = [
        [41, 522, 59, 524, 'A'], 
        [8, 203, 18, 203, 'B']
    ]
    '''
    rs = []
    for d in dataset:
        rs.append({
            'study': d[4],
            'year': 2020,
            'Et': d[0],
            'Nt': d[1],
            'Ec': d[2],
            'Nc': d[3]
        })
    cfg = {
        'prj': 'ALL',
        'analyzer_model': 'PRIM_CAT_RAW',
        'measure_of_effect': sm,
        'is_hakn': 'FALSE'
    }
    # use R to get the results
    rst = rplt_analyzer.analyze(rs, cfg)

    ret = {
        "model": {
            'measure': sm,
            'sm': rst['data']['primma']['model'][random_or_fixed]['sm'],
            'lower': rst['data']['primma']['model'][random_or_fixed]['lower'],
            'upper': rst['data']['primma']['model'][random_or_fixed]['lower'],
            'total': 0,
            'i2': rst['data']['primma']['heterogeneity']['i2'],
            'tau2': rst['data']['primma']['heterogeneity']['tau2'],
            'q_tval': 0,
            'q_pval': rst['data']['primma']['heterogeneity']['p'],
            'z_tval': 0,
            'z_pval': 0
        },
        'stus': []
    }

    for i in range(len(rst['data']['primma']['stus'])):
        r = rst['data']['primma']['stus'][i]
        ret['stus'].append({
            'name': r['name'],
            'sm': r['sm'],
            'lower': r['lower'],
            'upper': r['upper'],
            'total': r['Nt'],
            'w': r['w.%s' % random_or_fixed],
        })

    return ret


def get_ae_pma_data(full_fn, is_getting_sms=False):
    # load data
    xls = pd.ExcelFile(full_fn)

    # build AE Category data
    first_sheet_name = 'Adverse events'
    dft = xls.parse(first_sheet_name)
    ae_dict = {}
    ae_list = []

    for col in dft.columns:
        ae_cate = col
        # get those rows not NaN, which means containing adverse event name
        ae_names = dft[col][~dft[col].isna()]
        ae_item = {
            'ae_cate': ae_cate,
            'ae_names': []
        }
        # build ae_name dict
        for ae_name in ae_names:
            # remove the white space
            ae_name = ae_name.strip()
            if ae_name in ae_dict:
                cate1 = ae_dict[ae_name]
                print('! duplicate %s in [%s] and [%s]' % (ae_name, cate1, ae_cate))
                continue
            ae_dict[ae_name] = ae_cate
            ae_item['ae_names'].append(ae_name)

        ae_list.append(ae_item)
            
        print('* parsed ae_cate %s with %s names' % (col, len(ae_names)))
    print('* created ae_dict %s terms' % (len(ae_dict)))

    # build AE details
    cols = ['author', 'year', 'GA_Et', 'GA_Nt', 'GA_Ec', 'GA_Nc', 
            'G34_Et', 'G34_Ec', 'G3H_Et', 'G3H_Ec', 'G5N_Et', 'G5N_Ec', 
            'drug_used', 'malignancy']
    # sms = ['OR', 'RR', 'RD']
    sms = ['OR', 'RR']
    # grades = ['GA', 'G34', 'G3H', 'G5N']
    grades = ['GA', 'G3H', 'G5N']
    ae_dfts = []
    ae_rsts = {}

    # add detailed AE
    # the detailed AE starts from 3rd sheet
    # each sheet_name is an AE
    for sheet_name in xls.sheet_names[2:]:
        ae_name = sheet_name
        # the first row is no use
        # the second row is used as column name, but replaced with `cols` from A to N
        dft = xls.parse(sheet_name, skiprows=1, usecols='A:N', names=cols)
        
        # remove those empty lines based on author
        dft = dft[~dft.author.isna()]

        if len(dft) == 0: 
            print('* %s: [%s]' % (
                'EMPTY AE Tab'.ljust(25, ' '),
                ae_name.rjust(35, ' ')
            ))
            continue
        
        # add ae name here
        ae_name = ae_name.strip()
        ae_cate = ae_dict[ae_name]
        dft.loc[:, 'ae_cate'] = ae_cate
        dft.loc[:, 'ae_name'] = ae_name
        
        # add flag for each one, but need to be modified later
        dft.loc[:, 'has_GA'] = dft.GA_Et.notna()
        dft.loc[:, 'has_G34'] = dft.G34_Et.notna()
        dft.loc[:, 'has_G3H'] = dft.G3H_Et.notna()
        dft.loc[:, 'has_G5N'] = dft.G5N_Et.notna()

        # re-mark some flags to remove some studies
        for idx, r in dft.iterrows():
            # first, check the total number
            Nt = r['GA_Nt']
            Nc = r['GA_Nc']
            author = r['author']
            if np.isnan(Nt) or np.isnan(Nc):
                print('* %s: [%s] [%s] [%s] ' % (
                    'NaN Value Nt or Nc'.ljust(25, ' '),
                    ae_name.rjust(35, ' '), 
                    grade.rjust(3, ' '),
                    author
                ))
                # when Nt or Nc is NaN, the whole shouldn't appear
                for grade in grades:
                    dft.loc[idx, 'has_%s' % grade] = False
                continue

            for grade in grades:
                Et = r['%s_Et' % grade]
                Ec = r['%s_Ec' % grade]

                # second, check the Et, Ec NaN
                if np.isnan(Et) or np.isnan(Ec):
                    # print('* %s: [%s] [%s] [%s] ' % (
                    #     'Et or Ec is NaN'.ljust(25, ' '),
                    #     ae_name.rjust(35, ' '), 
                    #     grade.rjust(3, ' '), 
                    #     author
                    # ))
                    dft.loc[idx, 'has_%s' % grade] = False

                # third, check the Et Ec is 0
                if Et == 0 and Ec == 0:
                    # print('* %s: [%s] [%s] [%s]' % (
                    #     'ZERO Et and Ec'.ljust(25, ' '),
                    #     ae_name.rjust(35, ' '), 
                    #     grade.rjust(3, ' '), 
                    #     author
                    # ))
                    dft.loc[idx, 'has_%s' % grade] = False

        # add the AE model result
        # for each grade of each AE, the structure of rsts is as follows:
        # {
        #    'grade': grade,
        #    'stus': ['Name 1', 'Name 2'],
        #    'result': {
        #       'OR': {
        #          'random': pma_result,
        #          'fixed': pma_result
        #       } 
        #    }
        # }
        ae_rsts[ae_name] = {}
        for grade in grades:
            ae_rsts[ae_name][grade] = {
                'grade': grade,
                'stus': [],
                'Et': 0,
                'Nt': 0,
                'Ec': 0,
                'Nc': 0,
                'result': {}
            }
            # get records of this grade
            dftt = dft[dft['has_%s' % grade]==True]
            
            if len(dftt) < 2:
                # print('* %s: [%s] [%s]' % (
                #     'LESS than 2 studies'.ljust(25, ' '),
                #     ae_name.rjust(35, ' '), 
                #     grade.rjust(3, ' ')
                # ))
                continue 
            
            # ok, use the existing data to calcuate the 
            ae_rsts[ae_name][grade]['Et'] = int(dftt['%s_Et' % grade].sum())
            ae_rsts[ae_name][grade]['Nt'] = int(dftt['GA_Nt'].sum())
            ae_rsts[ae_name][grade]['Ec'] = int(dftt['%s_Ec' % grade].sum())
            ae_rsts[ae_name][grade]['Nc'] = int(dftt['GA_Nc'].sum())
            # fill the effective number of studies
            ae_rsts[ae_name][grade]['stus'] = dftt['author'].values.tolist()

            # get the dataset of this grade
            # from here, getting the OR/RR values of each AE of each grade
            if is_getting_sms:
                pass
            else: 
                continue

            # prepare the dataset for Pairwise MA
            ds = []
            for idx, r in dftt.iterrows():
                Et = r['%s_Et' % grade]
                Nt = r['GA_Nt']
                Ec = r['%s_Ec' % grade]
                Nc = r['GA_Nc']
                author = r['author']

                # a data fix for PythonMeta
                if Et == 0: Et = 0.4
                if Ec == 0: Ec = 0.4

                # convert data to PythonMeta Format
                ds.append([
                    Et,
                    Nt,
                    Ec, 
                    Nc,
                    author
                ])

            # for each sm, get the PMA result
            for sm in sms:
                # get the pma result
                try:
                    pma_r = get_pma(ds, datatype="CAT_RAW", sm=sm, random_or_fixed='random')
                    # validate the result, if isNaN, just set None
                    if np.isnan(pma_r['model']['sm']):
                        pma_r = None
                    
                except:
                    print('* %s: [%s] [%s] [%s]' % (
                        'ISSUE Data cause error'.ljust(25, ' '),
                        ae_name.rjust(35, ' '), 
                        grade.rjust(3, ' '),
                        ds
                    ))
                    pma_r = None

                # use R script to calculate the OR/RR
                # pma_r = get_pma_by_rplt(ds, datetype="CAT_RAW", sm=sm, random_or_fixed='random')

                ae_rsts[ae_name][grade]['result'][sm] = {
                    'random': pma_r,
                    # 'fixed': pma_f
                }
        
        # add to aes list
        ae_dfts.append(dft)

    # convert all small AE dft to a big one df_aes
    df_aes = pd.concat(ae_dfts)

    # fix data type
    df_aes['year'] = df_aes['year'].astype('int')
    def _asint(v):
        # if v is NaN
        if v!=v: return v
        # convert value to int
        try:
            v1 = int(v)
            return v1
        except:
            # convert other string to 0
            return 0
    for col in cols[2: -3]:
        df_aes[col] = df_aes[col].apply(_asint)
        df_aes[col] = df_aes[col].astype('Int64')

    # set index as a column
    df_aes = df_aes.reset_index()
    df_aes.rename(columns={'index': 'pid'}, inplace=True)
    rs = json.loads(df_aes.to_json(orient='records'))

    # build the return object
    ret = {
        'rs': rs,
        'ae_list': ae_list
    }

    if is_getting_sms:
        ret['ae_rsts'] = ae_rsts

    return ret


def get_ae_pma_data_simple(full_fn):
    # load data
    xls = pd.ExcelFile(full_fn)

    # build AE Category data
    first_sheet_name = xls.sheet_names[0]
    dft = xls.parse(first_sheet_name)
    dft = dft[~dft['name'].isna()]
    ae_dict = {}
    ae_list = []

    cie_cols = [
        'risk of bias',
        'inconsistency',
        'indirectness',
        'imprecision',
    ]

    col_pub_bia = 'publication bias'
    col_importance = 'importance'

    ae_item = {}
    for idx, row in dft.iterrows():
        ae_cate = row['category']
        ae_name = row['name']
        ae_fullname = row['full name']

        # create a new AE item to hold all the data
        if ae_item == {}:
            ae_item = {
                "ae_cate": ae_cate,
                "ae_names": []
            }
        elif ae_cate != ae_item['ae_cate']:
            # append the ae_cate and add a new one
            ae_list.append(ae_item)
            ae_item = {
                "ae_cate": ae_cate,
                "ae_names": []
            }
        
        # put current row in to ae_item
        ae_item['ae_names'].append(ae_name)

        # calc the Certainty in Evidence
        cie = calc_cie(row[cie_cols].tolist())

        # put current row in to ae_dict
        ae_dict[ae_name] = {
            "ae_cate": ae_cate,
            "ae_name": ae_name,
            "ae_fullname": ae_fullname,
            "cie": cie,
            "cie_rob": row[cie_cols[0]],
            "cie_inc": row[cie_cols[1]],
            "cie_ind": row[cie_cols[2]],
            "cie_imp": row[cie_cols[3]],
            "pub_bia": row['publication bias'],
            "importance": row[col_importance]
        }

    # put the last ae_item
    ae_list.append(ae_item)
    print('* created ae_dict %s terms' % (len(ae_dict)))

    # build AE details
    cols = ['study', 'year', 'Et', 'Nt', 'Ec', 'Nc', 'treatment', 'control']
    sms = ['OR', 'RR']
    ae_dfts = []
    ae_rsts = {}

    # add detailed AE
    # the detailed AE starts from 3rd sheet
    # each sheet_name is an AE
    for sheet_name in xls.sheet_names[1:]:
        ae_name = sheet_name
        # the first row is no use
        # the second row is used as column name, but replaced with `cols` from A to N
        dft = xls.parse(sheet_name, usecols='A:H', names=cols)
        
        # remove those empty lines based on author
        dft = dft[~dft.study.isna()]

        if len(dft) == 0: 
            print('* %s: [%s]' % (
                'EMPTY AE Tab'.ljust(25, ' '),
                ae_name.rjust(35, ' ')
            ))
            continue
        
        # add ae name here
        ae_name = ae_name.strip()
        ae_cate = ae_dict[ae_name]['ae_cate']
        ae_fullname = ae_dict[ae_name]['ae_fullname']
        dft.loc[:, 'ae_cate'] = ae_cate
        dft.loc[:, 'ae_name'] = ae_name
        dft.loc[:, 'ae_fullname'] = ae_fullname

        # add ae info
        ae_rsts[ae_name] = {
            'stus': [],
            'Et': 0,
            'Nt': 0,
            'Ec': 0,
            'Nc': 0,
            'result': {}
        }

        # copy ae_dict info to ae_rsts
        for k in ae_dict[ae_name]:
            ae_rsts[ae_name][k] = ae_dict[ae_name][k]
            
        # ok, use the existing data to calcuate the 
        ae_rsts[ae_name]['Et'] = int(dft['Et'].sum())
        ae_rsts[ae_name]['Nt'] = int(dft['Nt'].sum())
        ae_rsts[ae_name]['Ec'] = int(dft['Ec'].sum())
        ae_rsts[ae_name]['Nc'] = int(dft['Nc'].sum())

        # fill the effective number of studies
        ae_rsts[ae_name]['stus'] = dft['study'].values.tolist()

        # prepare the dataset for Pairwise MA
        ds = []
        for idx, r in dft.iterrows():
            Et = r['Et']
            Nt = r['Nt']
            Ec = r['Ec']
            Nc = r['Nc']
            study = r['study']

            # a data fix for PythonMeta
            if Et == 0: Et = 0.4
            if Ec == 0: Ec = 0.4

            # convert data to PythonMeta Format
            ds.append([
                Et,
                Nt,
                Ec, 
                Nc,
                study
            ])

            # for each sm, get the PMA result
            for sm in sms:
                # get the pma result
                try:
                    pma_r = get_pma(ds, datatype="CAT_RAW", sm=sm, random_or_fixed='random')
                    # validate the result, if isNaN, just set None
                    if np.isnan(pma_r['model']['sm']):
                        pma_r = None
                    
                except:
                    print('* %s: [%s] [%s]' % (
                        'ISSUE Data cause error'.ljust(25, ' '),
                        ae_name.rjust(35, ' '), 
                        ds
                    ))
                    pma_r = None

                # use R script to calculate the OR/RR
                # pma_r = get_pma_by_rplt(ds, datetype="CAT_RAW", sm=sm, random_or_fixed='random')

                ae_rsts[ae_name]['result'][sm] = {
                    'random': pma_r,
                    # 'fixed': pma_f
                }
        
        # add to aes list
        ae_dfts.append(dft)

    # convert all small AE dft to a big one df_aes
    df_aes = pd.concat(ae_dfts)

    # fix data type
    df_aes['year'] = df_aes['year'].astype('int')
    def _asint(v):
        # if v is NaN
        if v!=v: return v
        # convert value to int
        try:
            v1 = int(v)
            return v1
        except:
            # convert other string to 0
            return 0
    for col in cols[2: -3]:
        df_aes[col] = df_aes[col].apply(_asint)
        df_aes[col] = df_aes[col].astype('Int64')

    # set index as a column
    df_aes = df_aes.reset_index()
    df_aes.rename(columns={'index': 'pid'}, inplace=True)
    rs = json.loads(df_aes.to_json(orient='records'))

    # build the return object
    ret = {
        'rs': rs,
        'ae_list': ae_list,
        'ae_dict': ae_rsts
    }

    return ret


def get_ae_nma_data(full_fn):
    # load data
    xls = pd.ExcelFile(full_fn)

    # build AE Category data
    first_sheet_name = xls.sheet_names[0]
    dft = xls.parse(first_sheet_name)

    # ignore nan rows
    dft = dft[~dft['name'].isna()]
    ae_dict = {}
    ae_list = []

    cie_cols = [
        'risk of bias',
        'inconsistency',
        'indirectness',
        'imprecision',
    ]
    ae_item = {}
    for idx, row in dft.iterrows():
        ae_cate = row['category']
        ae_name = row['name']
        ae_fullname = row['full name']

        # create a new AE item to hold all the data
        if ae_item == {}:
            ae_item = {
                "ae_cate": ae_cate,
                "ae_names": []
            }
        elif ae_cate != ae_item['ae_cate']:
            # append the ae_cate and add a new one
            ae_list.append(ae_item)
            ae_item = {
                "ae_cate": ae_cate,
                "ae_names": []
            }
        
        # put current row in to ae_item
        ae_item['ae_names'].append(ae_name)

        # calc the Certainty in Evidence
        cie = calc_cie(row[cie_cols].tolist())

        # put current row in to ae_dict
        ae_dict[ae_name] = {
            "ae_cate": ae_cate,
            "ae_name": ae_name,
            "ae_fullname": ae_fullname,
            "cie": cie,
            "cie_rob": row[cie_cols[0]],
            "cie_inc": row[cie_cols[1]],
            "cie_ind": row[cie_cols[2]],
            "cie_imp": row[cie_cols[3]],
            "pub_bia": row['publication bias']
        }

        # get the result of CIE
        

    # put the last ae_item
    ae_list.append(ae_item)

    # extract the results
    cols = ['study', 'treat', 'event', 'total']
    sms = ['OR', 'RR']
    ae_dfts = []
    ae_rsts = {}

    for sheet_name in xls.sheet_names[1:]:
        ae_name = sheet_name
        # the first row is used as column name, but replaced with `cols` from A to D
        dft = xls.parse(sheet_name, usecols='A:D', names=cols)

        # remove those empty lines based on first col
        dft = dft[~dft[cols[0]].isna()]
        
        # get the record list like:
        # [
        #    { "col1": val1, "col2": val2 }, ...
        # ]
        rs = json.loads(dft.to_json(orient='table', index=False))['data']

        if len(dft) == 0: 
            print('* %s: [%s]' % (
                'EMPTY AE Tab'.ljust(25, ' '),
                ae_name.rjust(35, ' ')
            ))
            continue

        # count the treats and bind to ae_dict
        treat_list = dft['treat'].unique().tolist()
        ae_dict[ae_name]['treat_list'] = treat_list

        # sum the event and total
        dftt = dft.groupby('treat')[['event', 'total']].sum()
        treats = {}
        for idx, row in dftt.iterrows():
            treat = idx
            treats[treat] = {
                "event": int(row['event']),
                "total": int(row['total']),
                "rank": 0
            }
        ae_dict[ae_name]['treats'] = treats

        # now get the league table
        ae_dict[ae_name]['lgtable'] = {}
        for sm in sms:
            ae_dict[ae_name]['lgtable'][sm] = {}

            # make a config dictionary for calcuating
            cfg = {
                # for init analyzer
                "backend": "freq",
                "input_format": "ET",
                "data_type": 'CAT_RAW',

                # for R script
                "measure_of_effect": sm,
                "fixed_or_random": 'random'
            }

            # get the league table
            ret_nma = nma_analyzer.analyze(rs, cfg)

            # convert nma result to page format
            lgt_cols = ret_nma['data']['league']['cols']
            for lgt_rs in ret_nma['data']['league']['tabledata']:
                lgt_r = lgt_rs['row']
                # create a new comparator row
                ae_dict[ae_name]['lgtable'][sm][lgt_r] = {}

                for j, lgt_c in enumerate(lgt_cols):
                    lgt_cell = {
                        "sm": lgt_rs['stat'][j],
                        'lw': lgt_rs['lci'][j],
                        'up': lgt_rs['uci'][j]
                    }
                    # create a new treat col
                    ae_dict[ae_name]['lgtable'][sm][lgt_r][lgt_c] = lgt_cell

            # get the rank data
            psranks = sorted(ret_nma['data']['psrank']['rs'], key=lambda v: v['value'])
            for i, r in enumerate(psranks):
                ae_dict[ae_name]['treats'][r['treat']]['rank'] = i+1
                ae_dict[ae_name]['treats'][r['treat']]['pscore'] = r['value']
            # bind the raw results
            # ae_dict[ae_name]['lgtable'][sm]['raw_rst'] = ret_nma

    # return object
    rs = []
    ret = {
        'rs': rs,
        'ae_dict': ae_dict,
        'ae_list': ae_list
    }

    return ret


def calc_cie(vals):
    v = sum(vals)
    if v == 4:
        return 4
    if v == 5:
        return 3
    if v == 6:
        return 2
    else:
        return 1