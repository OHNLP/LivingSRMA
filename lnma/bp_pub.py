import os
import json

from flask import request
from flask import flash
from flask import render_template
from flask import Blueprint
from flask import send_from_directory
from flask import current_app

from flask_login import login_required
from flask_login import current_user

import pandas as pd

from lnma import dora

PATH_PUBDATA = 'pubdata'


bp = Blueprint("pub", __name__, url_prefix="/pub")

@bp.route('/')
def index():
    print('* current app instance_path:', current_app.instance_path)
    return render_template('pub.index.html')


@bp.route('/RCC.html')
def RCC():
    return render_template('pub.RCC.html')


@bp.route('/CAT.html')
def CAT():
    full_fn = os.path.join(current_app.instance_path, PATH_PUBDATA, 'CAT', 'GRAPH_LIST.json')
    j = json.load(open(full_fn))
    return render_template('pub.CAT.html', j=j)


@bp.route('/prisma.html')
def prisma():
    prj = request.args.get('prj')
    fn = 'PRISMA.json'
    full_fn = os.path.join(current_app.instance_path, PATH_PUBDATA, prj, fn)
    print('* load data from %s' % full_fn)
    j = open(full_fn).read()
    return render_template('pub.prisma.html', j=j)


@bp.route('/itable.html')
def itable():
    prj = request.args.get('prj')
    fn_attr = 'ITABLE_ATTR.csv'
    fn_data = 'ITABLE_DATA.csv'

    # attrs for project
    full_fn_attr = os.path.join(current_app.instance_path, PATH_PUBDATA, prj, fn_attr)
    full_fn_data = os.path.join(current_app.instance_path, PATH_PUBDATA, prj, fn_data)

    # get the cols
    attr_pack = get_attr_pack(full_fn_attr)

    # load file 
    if full_fn_data.endswith('csv'):
        df = pd.read_csv(full_fn_data)
    else:
        df = pd.read_excel(full_fn_data)
    rs = df.to_json(orient='records')

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

    return render_template('pub.itable.html', rs=rs, attrs=json.dumps(attrs))


@bp.route('/graph_v1.html')
def graph_v1():
    return render_template('pub.graph_v1.html')


@bp.route('/graph_v2.html')
def graph_v2():
    return render_template('pub.graph_v2.html')


@bp.route('/graphdata/<prj_fn>')
def graphdata(prj_fn):
    tmp = prj_fn.split('|')
    prj = tmp[0]
    fn = tmp[1]
    full_path = os.path.join(current_app.instance_path, PATH_PUBDATA, prj)
    return send_from_directory(full_path, fn)


def get_attr_pack(full_fn):
    df_attrs = pd.read_csv(full_fn)
    attr_dict = {}
    attr_tree = {}

    for idx, row in df_attrs.iterrows():
        name = row['name'].strip()
        vtype = row['vtype'].strip()
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