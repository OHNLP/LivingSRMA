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
    if full_fn.endswith('csv'):
        df = pd.read_csv(full_fn, skiprows=[0])
    else:
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
