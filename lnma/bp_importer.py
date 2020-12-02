import os
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

import pandas as pd

from werkzeug.utils import secure_filename

from lnma import dora
from lnma import util
from lnma import ss_state

bp = Blueprint("importer", __name__, url_prefix="/importer")


@bp.route('/by_pmid_list')
@login_required
def by_pmid_list():
    return render_template('importer/by_pmid_list.html')


@bp.route('/by_pubmed_csv')
@login_required
def by_pubmed_csv():
    return render_template('importer/by_pubmed_csv.html')


@bp.route('/by_endnote_xml')
@login_required
def by_endnote_xml():
    return render_template('importer/by_endnote_xml.html')


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

    if len(pmids) > 200:
        pmids = pmids[:200]

    # get detail by PubMed API
    data = util.e_summary(pmids)

    # prepare the return object
    ret = {
        'rs': []
    }

    uids = data['result']['uids']
    # check each pmid
    for pmid in uids:

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
        is_existed = dora.is_existed_paper(project_id, pmid)

        if is_existed:
            # that's possible!
            ret['rs'].append({
                'pmid': pmid,
                'success': False,
                'msg': 'PMID EXISTED'
            })
            continue
        
        # ok, save this pmid
        paper = data['result'][pmid]
        title = paper['title']
        pub_date = paper['sortpubdate'].split(' ')[0]
        authors = ', '.join([ a['name'] for a in paper['authors'] ])
        journal = paper['source']

        paper = dora.create_paper(project_id, pmid, 'pmid',
            title, pub_date, authors, journal, ss_state.SS_ST_AUTO_OTHER
        )

        ret['rs'].append({
            'pmid': pmid,
            'success': True,
            'msg': 'PAPER CREATED'
        })


    return jsonify(ret)



@bp.route('/upload_pubmedcsv', methods=['GET', 'POST'])
@login_required
def upload_pubmedcsv():
    if request.method == 'GET':
        return redirect(url_for('importer.index'))

    # save tmp file
    if 'input_csvfile' not in request.files:
        return jsonify({'success': False, 'msg':'No file is uploaded'})

    file_obj = request.files['input_csvfile']
    if file_obj.filename == '':
        return jsonify({'success': False, 'msg':'No selected file'})

    # save the upload file
    if file_obj and util.allowed_file_format(file_obj.filename):
        fn = secure_filename(file_obj.filename)
        full_fn = os.path.join(current_app.config['UPLOAD_FOLDER'], fn)
        file_obj.save(full_fn)
    else:
        return jsonify({'success': False, 'msg': 'Not supported file format'})

    # get the project_id
    project_id = request.form.get('project_id')

    # read file
    fmt = full_fn.split('.')[-1].lower()
    if fmt == 'xls' or fmt == 'xlsx':
        df = pd.read_excel(full_fn)
    else:
        df = pd.read_csv(full_fn)

    # prepare the return object
    ret = {
        'success': True,
        'rs': []
    }

    # parse each record
    for idx, row in df.iterrows():
        pmid = row['PMID']
        title = row['Title']
        pub_date = row['Create Date']
        authors = row['Authors']
        journal = row['Journal/Book']

        p = dora.create_paper_if_not_exist(
            project_id, pmid, 'pmid',
            title, pub_date, authors, journal, 
            ss_state.SS_ST_AUTO_OTHER
        )

        if p is None:
            ret['rs'].append({
                'pmid': pmid,
                'success': False,
                'msg': 'PAPER EXISTED'
            })
        else:
            ret['rs'].append({
                'pmid': pmid,
                'success': True,
                'msg': 'PAPER CREATED'
            })

    return jsonify(ret)


@bp.route('/upload_endnote_xml', methods=['GET', 'POST'])
@login_required
def upload_endnote_xml():
    ret = {
        "success": True
    }
    return jsonify(ret)