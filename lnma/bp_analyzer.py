import os
import json

from flask import request
from flask import flash
from flask import render_template
from flask import Blueprint
from flask import jsonify
from flask import current_app

from flask_login import login_required
from flask_login import current_user

import pandas as pd

from werkzeug.utils import secure_filename

from lnma.settings import *

from lnma import dora
from lnma.analyzer import freq_analyzer
from lnma.analyzer import bayes_analyzer


PATH_PUBDATA = 'pubdata'

bp = Blueprint("analyzer", __name__, url_prefix="/analyzer")

@bp.route('/')
@login_required
def index():
    return render_template('analyzer.index.html')


@bp.route('/pwma')
@login_required
def pwma():
    return render_template('analyzer.pwma.html')
    

@bp.route('/read_file', methods=['GET', 'POST'])
@login_required
def read_data_file():
    '''
    Read data from filename or a uploaded file
    '''
    if request.method == 'GET':
        fn = request.args.get('fn')
        path = request.args.get('path')
        fmt = fn.split('.')[-1].lower()
        if path is None:
            path = current_app.config['UPLOAD_FOLDER']
        else:
            path = './static/data/'
        full_fn = os.path.join(path, fn)

    elif request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'success': False, 'msg':'No file'})
        file_obj = request.files['file']
        if file_obj.filename == '':
            return jsonify({'success': False, 'msg':'No selected file'})
        # save the upload file
        if file_obj and allowed_file_format(file_obj.filename):
            fn = secure_filename(file_obj.filename)
            full_fn = os.path.join(current_app.config['UPLOAD_FOLDER'], fn)
            file_obj.save(full_fn)
        else:
            return jsonify({'success': False, 'msg': 'Not supported file format'})

    # read csv file
    ret = _read_file(full_fn)
    return jsonify(ret)


@bp.route('/analyze', methods=['GET', 'POST'])
@login_required
def analyze():
    if request.method == 'GET':
        return 'USE POST'

    # get the input data and configs
    rs = json.loads(request.form.get('rs'))
    cfg = json.loads(request.form.get('cfg'))

    # analyze
    ret = _analyze(rs, cfg)

    return jsonify(ret)


@bp.route('/graphdata_maker', methods=['GET', 'POST'])
@login_required
def graphdata_maker():
    if request.method == 'GET':
        return render_template('analyzer.graphdata_maker.html')
    
    # save uploaded file
    if 'file' not in request.files:
        return jsonify({'success': False, 'msg':'No file'})
    file_obj = request.files['file']
    if file_obj.filename == '':
        return jsonify({'success': False, 'msg':'No selected file'})

    if file_obj and allowed_file_format(file_obj.filename):
        fn = secure_filename(file_obj.filename)
        full_fn = os.path.join(current_app.config['UPLOAD_FOLDER'], fn)
        file_obj.save(full_fn)
    
    # prepare the msg for user
    msg = ''
    # read file
    file_data = _read_file(full_fn)

    # analyze
    prj_sname = request.form.get('prj')
    out_sname = request.form.get('out')
    msg += 'Project: %s <br>' % prj_sname
    msg += 'Tag: %s<br>' % out_sname
    
    # cfg = request.form.get('cfg')

    rs = file_data['raw']
    cfg = '{"analysis_method":"freq","input_format":"","treat":"EdoX","measure":"or","model":"fixed","better":"small"}'
    cfg = json.loads(cfg)

    # update file type
    cfg['input_format'] = file_data['coltype']
    
    msg += 'treats: ' + ','.join([ '"%s"' % t for t in file_data['treats'] ]) + '<br>'
    msg += 'cfg.analysis_method: %s <br>' % cfg['analysis_method']
    msg += 'cfg.input_format: %s <br>' % cfg['input_format']
    msg += 'cfg.measure: %s <br>' % cfg['measure']
    msg += 'cfg.model: %s <br>' % cfg['model']
    msg += 'cfg.better: %s <br>' % cfg['better']

    # save the graph data
    for treat in file_data['treats']:
        cfg['treat'] = treat
        graph_data = _analyze(rs, cfg)
        output_fn = 'GRAPH-%s-%s.json' % (out_sname, treat)
        full_output_fn = os.path.join(current_app.instance_path, PATH_PUBDATA, prj_sname, output_fn)
        json.dump(graph_data, open(full_output_fn, 'w'))
        _msg = 'analyzed and saved %s.[%s] on treat [%s] to %s' % (prj_sname, out_sname, treat, output_fn)
        print('* %s' % _msg)
        msg += '%s<br>' % _msg

    ret = {
        'success': True,
        'msg': msg
    }

    return jsonify(ret)


def allowed_file_format(fn):
    return '.' in fn and \
        fn.rsplit('.', 1)[1].lower() in ['csv', 'xls', 'xlsx']


def _read_file(full_fn):
    '''Read data file
    '''
    fmt = full_fn.split('.')[-1].lower()
    fn = full_fn.split('/')[-1]
    if fmt == 'xls' or fmt == 'xlsx':
        df = pd.read_excel(full_fn)
    else:
        df = pd.read_csv(full_fn)

    # detect the format
    df_columns = [ (c.lower()).strip() for c in df.columns.tolist() ]
    df_coltype = None
    for coltype in STANDARD_DATA_COLS:
        is_this_coltype = True
        st_cols = STANDARD_DATA_COLS[coltype]
        for col in st_cols:
            if col in df_columns:
                pass
            else:
                is_this_coltype = False

        if is_this_coltype:
            df_coltype = coltype
            break
    
    # get all treat
    if 'treat' in df_columns:
        treats = list(df['treat'].unique())
    elif 't1' in df_columns:
        treats = list(set(df['t1'].unique().tolist() + df['t2'].unique().tolist()))
    else:
        treats = []

    # get the number of studies
    n_studies = int(df['study'].nunique())

    # return
    ret = {
        'raw': json.loads(df.to_json(orient='records')),
        'filename': fn,
        'coltype': df_coltype,
        'cols': ', '.join(STANDARD_DATA_COLS[coltype]),
        'treats': treats,
        'n_studies': n_studies
    }

    return ret


def _analyze(rs, cfg):
    '''Analyze the rs with cfg
    '''
    # get the analysis type for make static json
    input_format = cfg['input_format']
    analysis_method = cfg['analysis_method']

    # get all treats
    all_treats = set([])
    for r in rs:
        if 'treat' in r:
            all_treats.add(r['treat'])
        if 't1' in r:
            all_treats.add(r['t1'])
    all_treats = list(all_treats)
    all_treats.sort()

    # get the ref treatment
    ref_treat = cfg['treat']

    # analyze!
    if analysis_method == 'freq':
        ret = freq_analyzer.analyze(rs, cfg)
    elif analysis_method == 'bayes':
        ret = bayes_analyzer.analyze(rs, cfg)
    else:
        ret = bayes_analyzer.analyze(rs, cfg)

    return ret