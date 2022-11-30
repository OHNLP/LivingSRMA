from functools import wraps
import json

from flask import Blueprint
from flask import request
from flask import jsonify
from flask import render_template
from flask import current_app
from flask import abort


from lnma.models import Paper
from lnma import dora
from lnma import srv_paper
from lnma import settings


bp = Blueprint("api", __name__, url_prefix="/api")

apikey_set = settings.API_SYSTEM_APIKEYS

def apikey_get_required(f):
    '''
    Check the APIKEY 
    '''
    @wraps(f)
    def wrap(*args, **kwargs):
        # check the API Keys here
        apikey = request.args.get('apikey', '').strip()
        if apikey not in apikey_set:
            ret = {
                'success': False,
                'msg': 'Unauthorized request'
            }
            return jsonify(ret)

        return f(*args, **kwargs)

    return wrap


def apikey_post_required(f):
    '''
    Check the APIKEY 
    '''
    @wraps(f)
    def wrap(*args, **kwargs):
        # check the API Keys here
        if request.method == 'GET':
            return f(*args, **kwargs)

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

#####################################################################
# RESTful APIs
#####################################################################

@bp.route('/r/paper/<keystr>/<pid>', methods=['GET'])
@apikey_get_required
def r_paper(keystr, pid):
    '''
    Restful Style Resource API for paper
    '''
    paper = dora.get_paper_by_keystr_and_pid(
        keystr, pid
    )

    # what?
    if paper is None:
        abort(404, description="Resource not found")

    return jsonify(paper.as_dict())


#####################################################################
# API for upload decisions
#####################################################################

@bp.route('/get_papers', methods=['GET', 'POST'])
@apikey_post_required
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
    # if keystr not in set(['IO', 'RCC', 'LBR', 'CAT', 'TEST']):
    #     ret['msg'] = 'Unsupported ks value'
    #     return jsonify(ret)

    try:
        papers = dora.get_papers_by_keystr(keystr)
        data = [ p.as_quite_simple_dict() for p in papers ]
        ret['success'] = True
        ret['data'] = data

    except Exception as err:
        ret['msg'] = 'System Err %s' % err
        return jsonify(ret)

    return jsonify(ret)


@bp.route('/set_pred_decisions', methods=['GET', 'POST'])
@apikey_post_required
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
    if keystr not in set(['IO', 'RCC', 'LBR', 'CAT', 'TEST']):
        ret['msg'] = 'Unsupported ks value'
        return jsonify(ret)

    # check the model id
    if mi not in set(['MIHIR']):
        ret['msg'] = 'Unsupported model id'
        return jsonify(ret)
    
    # extract data
    # the rs is a list of predictions
    # [
    #   { 'pid': 12345678, 'pred': 'e' },
    # ]
    try:
        rs = request.form.get('rs')
        rs = json.loads(rs)

    except Exception as err:
        print('wrong rs:', err)
        ret['msg'] = 'Input data is missing or not valid JSON format.'
        return jsonify(ret) 

    if len(rs) > 200:
        ret['msg'] = 'Too many records.'
        return jsonify(ret) 

    # do the implementation
    ps = []
    cnt = 0
    try:
        for r in rs:
            if 'pid' in r:
                # what?
                success, paper = srv_paper.set_paper_pred(
                    keystr, 
                    r['pid'],
                    mi,
                    r
                )
                if paper is None: 
                    msg = 'paper not found'
                else:
                    msg = ''

            else:
                success = False
                msg = 'pid is missing'

            ps.append({
                'pid': r['pid'],
                'flag': success,
                'msg': msg
            })

            if success: cnt += 1

        ret['success'] = True
        ret['msg'] = 'Updated %s/%s records' % (cnt, len(rs))
        ret['data'] = ps

    except Exception as err:
        ret['msg'] = 'System Err %s' % err
        return jsonify(ret)

    return jsonify(ret)
