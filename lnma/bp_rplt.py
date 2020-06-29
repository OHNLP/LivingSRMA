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

    # analyzer model
    am = request.form.get('am')
    # measure_of_effect
    sm = request.form.get('sm')
    # is_hakn
    hk = request.form.get('hk')

    # data
    rs = request.form.get('rs')
    rs = json.loads(rs)

    cfg = {
        'prj': prj,
        'analyzer_model': am,
        'measure_of_effect': sm,
        'is_hakn': hk,
    }

    ret = {
        'success': True,
        'img': {
            'outplt1': { 'url': '' },
            'cumuplt': { 'url': '' }
        }
    }
    # create a config
    result = rplt_analyzer.analyze(rs, cfg)

    ret['img']['outplt1']['url'] = url_for('index.f', fn=result['params']['fn_outplt1'])
    ret['img']['cumuplt']['url'] = url_for('index.f', fn=result['params']['fn_cumuplt'])
    
    # TODO the return should be checked here
    # but most of time, the figure will be generated.

    return jsonify(ret)
    
