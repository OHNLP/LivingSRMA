import re

from flask import request
from flask import flash
from flask import render_template
from flask import Blueprint
from flask import redirect
from flask import url_for
from flask import current_app
from flask import jsonify

from flask_login import login_required
from flask_login import current_user

from lnma import dora
from lnma import util

bp = Blueprint("importer", __name__, url_prefix="/importer")

@bp.route('/')
@login_required
def index():
    return render_template('importer.index.html')


@bp.route('/upload_pmids', methods=['GET', 'POST'])
@login_required
def upload_pmids():
    if request.method == 'GET':
        return redirect(url_for('importer.index'))

    # save the uploads
    project_id = request.form.get('project_id')
    pmids = request.form.get('pmids')

    # TODO check the pmids and project_id

    # remove the white space at start and end
    pmids = pmids.strip()

    # split by . , \s 
    pmids = re.split(r'[.,\s]+', pmids)

    # prepare the return object
    ret = {
        'rs': []
    }

    # check each pmid
    for pmid in pmids:
        if not util.is_valid_pmid(pmid):
            # that's weird
            ret['rs'].append({
                'pmid': pmid,
                'success': False,
                'msg': 'NOT VALID PMID'
            })
            continue
        
        # first check if pmid exists
        is_existed = False
        is_existed = dora.is_existed(project_id, pmid)

        if is_existed:
            # that's possible!
            ret['rs'].append({
                'pmid': pmid,
                'success': False,
                'msg': 'PMID EXISTED'
            })
            continue
        
        # ok, save this pmid
        paper = dora.create_paper(project_id, pmid)

        ret['rs'].append({
            'pmid': pmid,
            'success': True,
            'msg': 'PAPER CREATED'
        })


    return jsonify(ret)
