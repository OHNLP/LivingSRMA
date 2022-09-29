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

from lnma import settings
from lnma import dora
# from lnma.analyzer import rplt_analyzer
from lnma.analyzer import rpy2_pwma_analyzer as rplt_analyzer

PATH_PUBDATA = 'pubdata'

bp = Blueprint("rplt", __name__, url_prefix="/rplt")


def apikey_required(f):
    '''
    Check the APIKEY 
    '''
    @wraps(f)
    def wrap(*args, **kwargs):
        if request.method=='GET':
            return f(*args, **kwargs)

        # check the API Keys here
        # apikey_set = set([
        #     '7323590e-577b-4f46-b19f-3ec401829bd6',
        #     '9bebaa87-983d-42e4-ad70-4430c99aa886',
        #     'a8c0c749-7263-4072-a313-99ccc76569d3'
        # ])
        apikey = request.form.get('apikey', '').strip()
        if apikey not in settings.API_SYSTEM_APIKEYS:
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


@bp.route('/PWMA_INCD', methods=['GET', 'POST'])
@apikey_required
def pwma_incd():
    if request.method=='GET':
        return render_template('rplt/PWMA_INCD.html')

    # prepare the return object
    ret = {
        'success': False,
        'msg': '',
        'analysis_method': 'pwma_incd',
        'img': {
            'outplt1': { 'url': '' },
            'cumuplt': { 'url': '' }
        }
    }

    # measure_of_effect
    sm = request.form.get('sm', '').strip()
    # is_hakn
    hk = request.form.get('hk', '').strip()
    # is_create_figure
    cf = request.form.get('cf', '').strip()

    # check rs
    if sm not in set(['PLOGIT', 'PAS', "PFT", "PLN", "PRAW"]):
        ret['msg'] = 'Unsupported measure of effect'
        return jsonify(ret)
    
    # check hk
    if hk not in set(['TRUE', 'FALSE']):
        ret['msg'] = 'Unsupported value for Hartung-Knapp adjustment'
        return jsonify(ret)
    
    # check cf
    if cf not in set(['YES', 'NO']):
        ret['msg'] = 'Unsupported value for figure creation'
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
        'analyzer_model': 'PWMA_INCD',
        'measure_of_effect': sm,
        'input_format': 'CAT_RAW',
        'fixed_or_random': 'random',
        'is_fixed': 'FALSE',
        'is_random': 'TRUE',
        'pooling_method': 'Inverse',
        'tau_estimation_method': 'DL',
        'is_hakn': hk,
        'hakn_adjustment': hk,
        'adhoc_hakn': '' if hk == 'FALSE' else 'se',
        'is_create_figure': cf,
        'sort_by': 'year',
        'assumed_baseline': 100
    }

    # set the params for callback usage
    ret['params'] = {
        'sm': sm,
        'hk': hk
    }
    ret['params'].update(cfg)

    try:
        result = rplt_analyzer.analyze_pwma_incd(rs, cfg)
        # TODO the return should be checked here
        # but most of time, the figure will be generated.
        if result['success']:
            ret['success'] = True
            if cf == 'YES':
                ret['img']['outplt1']['url'] = url_for('index.f', fn=result['params']['fn_outplt1'])
                ret['img']['cumuplt']['url'] = url_for('index.f', fn=result['params']['fn_cumuplt'])
                ret['data'] = result['data']
            else:
                ret['data'] = result['data']

            # merge the rs value
            for i, r in enumerate(rs):
                for k in r:
                    ret['data']['incdma']['stus'][i][k] = r[k]
                
            # the cumulative may NOT be in the results if there is only one record
            if 'cumuma' in ret['data'] and ret['data']['cumuma'] is not None:
                for i, r in enumerate(rs):
                    for k in r:
                        ret['data']['cumuma']['stus'][i][k] = r[k]
        else:
            ret['msg'] = result['msg']

    except Exception as err:
        print('Handling run-time error:', err)

        if current_app.config['DEBUG']:
            raise err

        ret['msg'] = 'System error, please check input data.'

    # print(ret)

    return jsonify(ret)


@bp.route('/PWMA_PRCM', methods=['GET', 'POST'])
@apikey_required
def pwma_prcm():
    '''
    Pairwise Meta-Analysis for primary and cumulative
    '''
    if request.method=='GET':
        return render_template('rplt/PWMA_PRCM.html')

    # prepare the return object
    ret = {
        'success': False,
        'msg': '',
        'analysis_method': 'pwma_prcm',
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
        'analyzer_model': 'PWMA_PRCM',
        'measure_of_effect': sm,
        'is_hakn': hk,
        'fixed_or_random': 'random',
        'input_format': 'CAT_RAW',
        'sort_by': 'year',
        'pooling_method': 'MH',
        'tau_estimation_method': 'DL',
        'assumed_baseline': 100
    }

    # set the params for callback usage
    ret['params'] = {
        'am': am,
        'sm': sm,
        'hk': hk
    }
    ret['params'].update(cfg)

    try:
        result = rplt_analyzer.analyze_pwma_prcm(rs, cfg, has_cumu=True)
        # TODO the return should be checked here
        # but most of time, the figure will be generated.
        if result['success']:
            ret['success'] = True
            if am == 'FOREST':
                ret['img']['outplt1']['url'] = url_for('index.f', fn=result['params']['fn_outplt1'])
                ret['img']['cumuplt']['url'] = url_for('index.f', fn=result['params']['fn_cumuplt'])
            elif am == 'FORESTDATA': 
                ret['data'] = result['data']

            # merge the rs value
            # in this proecess, add the pid and other information to results
            for i, r in enumerate(rs):
                for k in r:
                    ret['data']['primma']['stus'][i][k] = r[k]

            # the cumulative may NOT be in the results if there is only one record
            if 'cumuma' in ret['data'] and ret['data']['cumuma'] is not None:
                for i, r in enumerate(rs):
                    for k in r:
                        ret['data']['cumuma']['stus'][i][k] = r[k]
                        
        else:
            ret['msg'] = result['msg']

    except Exception as err:
        print('Handling run-time error:', err)

        if current_app.config['DEBUG']:
            raise err

        ret['msg'] = 'System error, please check input data.'

    # print(ret)

    return jsonify(ret)


@bp.route('/PWMA_PRCM_COE', methods=['GET', 'POST'])
@apikey_required
def pwma_prcm_coe():
    '''
    Pairwise Meta-Analysis for primary and cumulative with CoE
    '''
    if request.method=='GET':
        return render_template('rplt/PWMA_PRCM_COE.html')

    # prepare the return object
    ret = {
        'success': False,
        'msg': '',
        'analysis_method': 'pwma_prcm',
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
        'analyzer_model': 'PWMA_PRCM',
        'measure_of_effect': sm,
        'is_hakn': hk,
        'fixed_or_random': 'random',
        'input_format': 'CAT_RAW',
        'sort_by': 'year',
        'pooling_method': 'MH',
        'tau_estimation_method': 'DL',
        'assumed_baseline': 100
    }

    # set the params for callback usage
    ret['params'] = {
        'am': am,
        'sm': sm,
        'hk': hk
    }
    ret['params'].update(cfg)

    try:
        result = rplt_analyzer.analyze_pwma_prcm(rs, cfg, has_cumu=True)
        # TODO the return should be checked here
        # but most of time, the figure will be generated.
        if result['success']:
            ret['success'] = True
            if am == 'FOREST':
                ret['img']['outplt1']['url'] = url_for('index.f', fn=result['params']['fn_outplt1'])
                ret['img']['cumuplt']['url'] = url_for('index.f', fn=result['params']['fn_cumuplt'])
            elif am == 'FORESTDATA': 
                ret['data'] = result['data']

            # merge the rs value
            # in this proecess, add the pid and other information to results
            for i, r in enumerate(rs):
                for k in r:
                    ret['data']['primma']['stus'][i][k] = r[k]

            # the cumulative may NOT be in the results if there is only one record
            if 'cumuma' in ret['data'] and ret['data']['cumuma'] is not None:
                for i, r in enumerate(rs):
                    for k in r:
                        ret['data']['cumuma']['stus'][i][k] = r[k]
                        
        else:
            ret['msg'] = result['msg']

    except Exception as err:
        print('Handling run-time error:', err)

        if current_app.config['DEBUG']:
            raise err

        ret['msg'] = 'System error, please check input data.'

    # print(ret)

    return jsonify(ret)
    
