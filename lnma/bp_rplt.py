import os
import json
from functools import wraps

from flask import request
from flask import flash
from flask import render_template
from flask import Blueprint
from flask import jsonify
from flask import url_for
from flask import current_app

from werkzeug.utils import secure_filename

from lnma.settings import *

from lnma import dora
from lnma.analyzer import rplt_analyzer

PATH_PUBDATA = 'pubdata'

bp = Blueprint("rplt", __name__, url_prefix="/rplt")


def apikey_required(f):
    '''Check the APIKEY 
    '''
    @wraps(f)
    def wrap(*args, **kwargs):
        if request.method=='GET':
            return f(*args, **kwargs)

        # check the API Keys here
        apikey_set = set([
            '7323590e-577b-4f46-b19f-3ec401829bd6',
            '9bebaa87-983d-42e4-ad70-4430c99aa886',
            'a8c0c749-7263-4072-a313-99ccc76569d3'
        ])
        apikey = request.form.get('apikey', '').strip()
        if apikey not in apikey_set:
            ret = {
                'success': False,
                'msg': 'Unauthorized request'
            }
            return jsonify(ret)

        return f(*args, **kwargs)

    return wrap


@bp.route('/')
def index():
    return 'RPLT Service'


@bp.route('/IOTOX', methods=['GET', 'POST'])
@apikey_required
def iotox():
    if request.method=='GET':
        return render_template('rplt.IOTOX.html')
    # define the pro ject name
    prj = 'IOTOX'

    # prepare the return object
    ret = {
        'success': False,
        'msg': '',
        'img': {
            'outplt1': { 'url': '' },
            'cumuplt': { 'url': '' }
        }
    }

    # analyzer model
    am = request.form.get('am', '').strip()
    # measure_of_effect
    sm = request.form.get('sm', '').strip()
    # is_hakn
    hk = request.form.get('hk', '').strip()

    # check am
    if am not in set(['FOREST', 'FORESTDATA']):
        ret['msg'] = 'Unsupported analyzer'
        return jsonify(ret)
    
    # check rs
    if sm not in set(['OR', 'RR', 'RD']):
        ret['msg'] = 'Unsupported measure of effect'
        return jsonify(ret)
    
    # check hk
    if hk not in set(['TRUE', 'FALSE']):
        ret['msg'] = 'Unsupported value for Hartung-Knapp adjustment'
        return jsonify(ret)

    # extract data
    try:
        rs = request.form.get('rs')
        rs = json.loads(rs)
    except Exception as err:
        print('wrong rs:', err)
        ret['msg'] = 'Input data is missing or not valid JSON format.'
        return jsonify(ret) 

    # create a config
    cfg = {
        'prj': prj,
        'analyzer_model': am,
        'measure_of_effect': sm,
        'is_hakn': hk,
    }

    # set the params for callback usage
    ret['params'] = {
        'am': am,
        'sm': sm,
        'hk': hk
    }

    try:
        result = rplt_analyzer.analyze(rs, cfg)
        # TODO the return should be checked here
        # but most of time, the figure will be generated.
        if result['success']:
            ret['success'] = True
            if am == 'FOREST':
                ret['img']['outplt1']['url'] = url_for('index.f', fn=result['params']['fn_outplt1'])
                ret['img']['cumuplt']['url'] = url_for('index.f', fn=result['params']['fn_cumuplt'])
            elif am == 'FORESTDATA': 
                ret['data'] = result['data']
        else:
            ret['msg'] = result['msg']
    except Exception as err:
        print('Handling run-time error:', err)

        if current_app.config['DEBUG']:
            raise err

        ret['msg'] = 'System error, please check input data.'

    print(ret)

    return jsonify(ret)
    
