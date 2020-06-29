import os
import json

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

@bp.route('/')
def index():
    return 'rplt'


@bp.route('/IOTOX', methods=['GET', 'POST'])
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

    # extract data
    try:
        rs = request.form.get('rs')
        rs = json.loads(rs)
    except Exception as err:
        print('wrong rs:', err)
        ret['msg'] = 'Input data is not valid JSON format.'
        return jsonify(ret) 

    # create a config
    cfg = {
        'prj': prj,
        'analyzer_model': am,
        'measure_of_effect': sm,
        'is_hakn': hk,
    }
    try:
        result = rplt_analyzer.analyze(rs, cfg)
        # TODO the return should be checked here
        # but most of time, the figure will be generated.
        if result['success']:
            ret['success'] = True
            ret['img']['outplt1']['url'] = url_for('index.f', fn=result['params']['fn_outplt1'])
            ret['img']['cumuplt']['url'] = url_for('index.f', fn=result['params']['fn_cumuplt'])
        else:
            ret['msg'] = result['msg']
    except Exception as err:
        print('Handling run-time error:', err)
        ret['msg'] = 'System error, please check input data.'

    return jsonify(ret)
    
