import functools

from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from flask import current_app
from flask import jsonify

from flask_login import UserMixin
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user

from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from lnma import dora
from lnma import util

bp = Blueprint("sysmgr", __name__, url_prefix="/sysmgr")


@bp.route('/')
@login_required
def index():
    return render_template('sysmgr/index.html')


@bp.route('/make_study_dict', methods=['GET', 'POST'])
@login_required
def make_study_dict():
    if request.method == 'GET':
        return render_template('sysmgr.make_study_dict.html')

    pmids_txt = request.form.get('pmids')
    pmids = pmids_txt.split(',')

    # the attrs we need:
    # * title
    # * authors
    # * date
    # * journal
    # * pid
    # * pid_type

    rst = util.e_fetch(pmids)

    sd = {}
    for pid in rst['result']['uids']:
        p = rst['result'][pid]
        sd[pid] = {
            'title': p['title'],
            'authors': ', '.join(list(map(lambda v: v['name'], p['authors']))),
            'date': p['sortpubdate'],
            'journal': p['source'],
            'pid': pid,
            'pid_type': 'pmid'
        }

    ret = {
        'success': True,
        'data': sd
    }
    return jsonify(ret)


@bp.route('/pred_rct_demo', methods=['GET', 'POST'])
@login_required
def pred_rct_demo():
    if request.method == 'GET':
        return render_template('sysmgr/pred_rct_demo.html')

    ti = request.form.get('ti')
    ab = request.form.get('ab')

    # the attrs we need:
    # * title
    # * abstract
    # * date
    rst = util.pred_rct(ti, ab)

    ret = {
        'success': True,
        'data': rst
    }
    return jsonify(ret)


# @bp.route('/')