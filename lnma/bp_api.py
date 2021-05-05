from functools import wraps
import json

from flask import Blueprint
from flask import request
from flask import jsonify
from flask import render_template
from flask import current_app


from lnma.models import Paper
from lnma import dora

bp = Blueprint("api", __name__, url_prefix="/api")


def apikey_required(f):
    '''
    Check the APIKEY 
    '''
    @wraps(f)
    def wrap(*args, **kwargs):
        if request.method=='GET':
            return f(*args, **kwargs)

        # check the API Keys here
        apikey_set = set([
            '7323590e-577b-4f46-b19f-3ec402829bd6',
            '9bebaa87-983d-42e4-ad70-4430c29aa886',
            'a8c0c749-7263-4072-a313-99ccc26569d3'
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
    return 'Data API Service'


@bp.route('/get_papers', methods=['GET', 'POST'])
@apikey_required
def get_papers():
    '''
    Get papers
    '''
    if request.method=='GET':
        return render_template('api/get_papers.html')

    # prepare the return object
    ret = {
        'success': False,
        'msg': ''
    }

    # project keystr
    keystr = request.form.get('ks')
    if keystr not in set(['IO', 'RCC', 'LBR', 'CAT']):
        ret['msg'] = 'Unsupported ks value'
        return jsonify(ret)

    try:
        papers = dora.get_papers_by_keystr(keystr)
        data = [ p.as_extreme_simple_dict() for p in papers ]
        ret['success'] = True
        ret['data'] = data

    except Exception as err:
        ret['msg'] = 'System Err %s' % err
        return jsonify(ret)

    return jsonify(ret)


@bp.route('/set_pred_decisions', methods=['GET', 'POST'])
@apikey_required
def set_pred_decisions():
    '''
    Set the prediction
    '''
    if request.method=='GET':
        return render_template('api/set_pred_decisions.html')

    # prepare the return object
    ret = {
        'success': False,
        'msg': '',
    }

    # project ks
    keystr = request.form.get('ks', '').strip()
    # model id
    mi = request.form.get('mi', '').strip()

    # check the keystr
    if keystr not in set(['IO', 'RCC', 'LBR', 'CAT']):
        ret['msg'] = 'Unsupported ks value'
        return jsonify(ret)

    # check the model id
    if mi not in set(['MIHIR']):
        ret['msg'] = 'Unsupported model id'
        return jsonify(ret)
    
    # extract data
    try:
        rs = request.form.get('rs')
        rs = json.loads(rs)
    except Exception as err:
        print('wrong rs:', err)
        ret['msg'] = 'Input data is missing or not valid JSON format.'
        return jsonify(ret) 

    # do the implementation
    ps = []

    try:
        for r in rs:
            ps.append({
                'pid': r['pid'],
                'pred': r['pred'],
                'flag': True
            })

        ret['success'] = True
        ret['msg'] = 'Not implemented yet'
        ret['data'] = ps

    except Exception as err:
        ret['msg'] = 'System Err %s' % err
        return jsonify(ret)

    return jsonify(ret)
