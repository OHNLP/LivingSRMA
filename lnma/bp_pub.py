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

###########################################################
# Modules for public page
###########################################################

@bp.route('/prisma.html')
def prisma():
    return render_template('pub.prisma.html')


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


@bp.route('/outcomeplot.html')
def outcomeplot():
    return render_template('pub.outcomeplot.html')


###########################################################
# Data services
###########################################################

@bp.route('/graphdata/<prj>/<fn>')
def graphdata(prj, fn):
    '''General data files
    '''
    full_path = os.path.join(current_app.instance_path, PATH_PUBDATA, prj)
    return send_from_directory(full_path, fn)


@bp.route('/graphdata/<prj>/ITABLE.json')
def graphdata_itable_json(prj):
    '''Special rule for the ITABLE.json which does not exist
    '''
    fn = 'ITABLE_ATTR_DATA.xlsx'
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


@bp.route('/graphdata/<prj>/img/<fn>')
def graphdata_img(prj, fn):
    '''get image files of specific project
    '''
    full_path = os.path.join(current_app.instance_path, PATH_PUBDATA, prj, 'img')
    return send_from_directory(full_path, fn)


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
    fn = 'OPLOTS_DATA.xls'
    full_fn = os.path.join(current_app.instance_path, PATH_PUBDATA, prj, fn)

    # load data
    xls = pd.ExcelFile(full_fn)

    # build AE Category data
    dft = xls.parse('Adverse events')
    ae_dict = {}
    ae_list = []

    for col in dft.columns:
        ae_cate = col
        ae_names = dft[col][~dft[col].isna()]
        ae_item = {
            'ae_cate': ae_cate,
            'ae_names': []
        }
        
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

    aes_dfts = []

    # add All SEs
    # dft = xls.parse('All SEs', skiprows=1, usecols='A:L', names=cols[:-2])
    # dft.loc[:, cols[-2]] = ''
    # dft.loc[:, cols[-1]] = ''
    # dft.loc[:, 'ae_cate'] = 'All SEs'
    # dft.loc[:, 'ae_name'] = 'All SEs'
    # dft.loc[:, 'is_G34'] = dft.G34_Et.isna()
    # dft.loc[:, 'is_G3H'] = dft.G3H_Et.isna()
    # dft.loc[:, 'is_G5N'] = dft.G5N_Et.isna()
    # aes_dfts.append(dft)

    # add detailed AE
    # the detailed AE starts from 4th sheet
    for sheet_name in xls.sheet_names[3:]:
        ae_name = sheet_name
        dft = xls.parse(sheet_name, skiprows=1, usecols='A:N', names=cols)
        
        # remove those empty lines
        dft = dft[~dft.author.isna()]
        
        # add ae name here
        ae_name = ae_name.strip()
        ae_cate = ae_dict[ae_name]
        dft.loc[:, 'ae_cate'] = ae_cate
        dft.loc[:, 'ae_name'] = ae_name
        
        # add flag
        dft.loc[:, 'is_G34'] = dft.G34_Et.isna()
        dft.loc[:, 'is_G3H'] = dft.G3H_Et.isna()
        dft.loc[:, 'is_G5N'] = dft.G5N_Et.isna()
        
        aes_dfts.append(dft)
        
    df_aes = pd.concat(aes_dfts)

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
    
    rs = json.loads(df_aes.to_json(orient='records'))
    ret = {
        'rs': rs,
        'ae_list': ae_list
    }
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
