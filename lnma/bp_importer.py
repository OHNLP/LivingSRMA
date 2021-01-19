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

from lnma.bp_screener import create_pr_rs_details

from tqdm import tqdm

import json

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
    return render_template('importer/by_endnote_xml.html', ss=ss_state)


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
        is_existed, _paper = dora.is_existed_paper(project_id, pmid)

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
            title, pub_date, authors, journal, None, ss_state.SS_ST_AUTO_OTHER
        )

        ret['rs'].append({
            'pmid': pmid,
            'success': True,
            'msg': 'PAPER CREATED'
        })


    return jsonify(ret)


@bp.route('/import_pmids', methods=['GET', 'POST'])
@login_required
def import_pmids():
    if request.method == 'GET':
        return redirect(url_for('importer.index'))

    # save the uploads
    project_id = request.form.get('project_id')
    rs = json.loads(request.form.get('rs'))

    # TODO check the pmids and project_id

    if len(rs) > 200:
        rs = rs[:200]

    rs2 = []
    pmids = []
    pmid2rct_id = {}

    # remove the duplicated rows
    for r in rs:
        if r['pmid'] not in pmids:
            pmid = r['pmid']
            pmids.append(pmid)
            rs2.append(r)
            pmid2rct_id[pmid] = r['rct_id']

    # get detail by PubMed API
    data = util.e_fetch(pmids)

    # prepare the return object
    ret = {
        'rs': []
    }

    uids = data['result']['uids']
    # check each pmid
    for pmid in uids:

        # ok, save this pmid
        paper = data['result'][pmid]
        title = paper['title']
        abstract = paper['abstract']
        pub_date = paper['sortpubdate']
        authors = ', '.join([ a['name'] for a in paper['authors'] ])
        journal = paper['source']
        rct_id = pmid2rct_id[pmid]

        is_existed, paper = dora.create_paper_if_not_exist_and_predict_rct(
            project_id, pmid, 'PMID', title, abstract, pub_date, authors, journal,
            {'rct_id': rct_id}, 
            ss_state.SS_ST_IMPORT_SIMPLE_CSV, 
            ss_state.SS_PR_NA,
            ss_state.SS_RS_NA,
        )

        ret['rs'].append({
            'pmid': pmid,
            'paper': paper.as_simple_dict(),
            'is_existed': is_existed
        })

    return jsonify(ret)


@bp.route('/upload_pmid_data_file', methods=['GET', 'POST'])
@login_required
def upload_pmid_data_file():
    if request.method == 'GET':
        return redirect(url_for('importer.index'))

    # save tmp file
    if 'input_file' not in request.files:
        return jsonify({'success': False, 'msg':'No file is uploaded'})

    file_obj = request.files['input_file']
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
        rct_id = row['NCT ID']
        pmid = row['PMID']
        
        ret['rs'].append({
            'pmid': pmid,
            'rct_id': rct_id
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

        _, p = dora.create_paper_if_not_exist(
            project_id, pmid, 'pmid',
            title, pub_date, authors, journal, None,
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
    if request.method == 'GET':
        return redirect(url_for('importer.by_endnote_xml'))

    # save tmp file
    if 'input_file' not in request.files:
        return jsonify({'success': False, 'msg':'No file is uploaded'})

    file_obj = request.files['input_file']
    if file_obj.filename == '':
        return jsonify({'success': False, 'msg':'No selected file'})

    # save the upload file
    if file_obj and util.allowed_file_format(file_obj.filename):
        # TODO may rename the filename in the future to avoid conflict names
        fn = secure_filename(file_obj.filename)
        full_fn = os.path.join(current_app.config['UPLOAD_FOLDER_IMPORTS'], fn)
        file_obj.save(full_fn)
    else:
        return jsonify({'success': False, 'msg': 'Not supported file format'})

    # get the project_id
    project_id = request.form.get('project_id')

    # get the study list from the uploaded file
    papers = util.parse_endnote_exported_xml(full_fn)

    if papers is None:
        # which means something wrong with the file
        return jsonify({'success': False, 'msg': 'Not supported file format'})

    ret = {
        "success": True,
        "papers": papers
    }

    return jsonify(ret)


@bp.route('/save_papers', methods=['GET', 'POST'])
@login_required
def save_papers():
    if request.method == 'GET':
        return redirect(url_for('importer.by_endnote_xml'))

    # get the project_id
    project_id = request.form.get('project_id')
    # get the papers
    papers = json.loads(request.form.get('papers'))
    # get the default stage
    stage = request.form.get('stage')

    # convert stage to pr and rs
    ss_pr, ss_rs = ss_state.SS_STAGE_TO_PR_AND_RS[stage]
    ss_ex = create_pr_rs_details('User specified', stage)

    ret = {
        "success": True,
        "cnt": {
            'total': len(papers),
            'existed': 0,
            'created': 0,
        },
        "papers": [],
    }

    for p in papers:
    # for p in tqdm(papers):
        is_exist, paper = dora.create_paper_if_not_exist_and_predict_rct(
            project_id, 
            p['pid'], 
            p['pid_type'],
            p['title'],
            p['abstract'],
            util.check_paper_pub_date(p['pub_date']),
            p['authors'],
            util.check_paper_journal(p['journal']),
            None,
            ss_state.SS_ST_IMPORT_ENDNOTE_XML,
            ss_pr,
            ss_rs,
            ss_ex,
            None,
        )
        
        # create a return obj
        _p = {
            'result': 'existed',
            'success': False,
            'seq': p['seq']
        }
        if is_exist:
            ret['cnt']['existed'] += 1
            _p = {
                'result': 'existed',
                'success': False,
                'seq': p['seq']
            }
        else:
            ret['cnt']['created'] += 1
            _p = {
                'result': 'created',
                'success': False,
                'seq': p['seq']
            }

        ret['papers'].append(_p)

    return jsonify(ret)


@bp.route('/upload_endnote_xml_and_save_papers', methods=['GET', 'POST'])
@login_required
def upload_endnote_xml_and_save_papers():
    if request.method == 'GET':
        return redirect(url_for('importer.by_endnote_xml'))

    # save tmp file
    if 'input_file' not in request.files:
        return jsonify({'success': False, 'msg':'No file is uploaded'})

    file_obj = request.files['input_file']
    if file_obj.filename == '':
        return jsonify({'success': False, 'msg':'No selected file'})

    # save the upload file
    if file_obj and util.allowed_file_format(file_obj.filename):
        # TODO may rename the filename in the future to avoid conflict names
        fn = secure_filename(file_obj.filename)
        full_fn = os.path.join(current_app.config['UPLOAD_FOLDER_IMPORTS'], fn)
        file_obj.save(full_fn)
    else:
        return jsonify({'success': False, 'msg': 'Not supported file format'})

    # get the project_id
    project_id = request.form.get('project_id')

    # get the study list from the uploaded file
    papers = util.parse_endnote_exported_xml(full_fn)
    if papers is None:
        # which means something wrong with the file
        return jsonify({'success': False, 'msg': 'Not supported file format'})

    else:
        # now create the paper in db
        cnt = {
            'total': len(papers),
            'existed': 0,
            'created': 0,
        }
        for p in tqdm(papers):
            is_exist, paper = dora.create_paper_if_not_exist_and_predict_rct(
                project_id, 
                p['pid'], 
                p['pid_type'],
                p['title'],
                p['abstract'],
                util.check_paper_pub_date(p['pub_date']),
                p['authors'],
                util.check_paper_journal(p['journal']),
                None,
                ss_state.SS_ST_IMPORT_ENDNOTE_XML,
                ss_state.SS_PR_NA,
                ss_state.SS_RS_NA,
                None,
                None,
            )
            if is_exist:
                cnt['existed'] += 1
            else:
                cnt['created'] += 1

    ret = {
        "success": True,
        "cnt": cnt
    }
    return jsonify(ret)