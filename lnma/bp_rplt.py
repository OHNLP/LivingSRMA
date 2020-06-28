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
    # define the project name
    prj = 'IOTOX'

    # analyzer model
    am = request.form.get('am')
    # data source
    ds = request.form.get('ds')
    # cancer type
    ct = request.form.get('ct')
    # adverse event
    ae = request.form.get('ae')

    # create a config object
    fn_outplt = '%s_%s_%s_%s-plot.png' % (am, ds, ct, ae)
    
    # for test, all request redirect to this one
    fn_outplt = 'FOREST_DS92_Melanoma_EVENT_NAME_plot.png'

    fn_outplt = secure_filename(fn_outplt)
    cfg = {
        'prj': prj,
        'analyzer_model': am,
        'data_source': ds,
        'cancer_type': ct,
        'adverse_event': ae,
        'fn_outplt': fn_outplt
    }

    # get the full filename for output image
    full_fn_output = os.path.join(
        current_app.instance_path, 
        PATH_PUBDATA, 
        prj, 'img',
        fn_outplt)

    cfg['full_fn_output'] = full_fn_output

    url_fn_outplt = url_for('pub.graphdata_img', prj=prj, fn=fn_outplt)
    ret = {
        'success': True,
        'fn_outplt': fn_outplt,
        'url': url_fn_outplt,
    }
    if os.path.exists(full_fn_output):
        pass
    else:
        # find the data source file
        full_fn_inputfile = os.path.join(
            current_app.instance_path, 
            PATH_PUBDATA, 
            prj, 'ds',
            ds + '.xlsx')
        cfg['full_fn_inputfile'] = full_fn_inputfile

        # create a config
        _ = rplt_analyzer.analyze(None, cfg)
        
        # TODO the return should be checked here
        # but most of time, the figure will be generated.

    return jsonify(ret)
    
