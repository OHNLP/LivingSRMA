import os
from pprint import pprint
import re
import time
import datetime

from flask import request
from flask import flash
from flask import render_template
from flask import Blueprint
from flask import redirect
from flask import url_for
from flask import current_app
from flask import jsonify
from sqlalchemy.sql.operators import exists

from flask_login import login_required
from flask_login import current_user

import pandas as pd

from werkzeug.utils import secure_filename

from lnma import dora, settings, srv_import
from lnma import util
from lnma import ss_state

from lnma.bp_screener import create_pr_rs_details

from tqdm import tqdm

import json

bp = Blueprint("importer", __name__, url_prefix="/importer")


@bp.route('/by_pmid_list')
@login_required
def by_pmid_list():
    return render_template('importer/by_pmid_list.html', ss=ss_state)


@bp.route('/by_pubmed_csv')
@login_required
def by_pubmed_csv():
    return render_template('importer/by_pubmed_csv.html', ss=ss_state)


@bp.route('/by_endnote_xml')
@login_required
def by_endnote_xml():
    return render_template('importer/by_endnote_xml.html', ss=ss_state)


@bp.route('/by_user_input')
@login_required
def by_user_input():
    return render_template('importer/by_user_input.html', ss=ss_state)



# @bp.route('/upload_pmids', methods=['GET', 'POST'])
# @login_required
# def upload_pmids():
#     if request.method == 'GET':
#         return redirect(url_for('importer.index'))

#     # save the uploads
#     project_id = request.form.get('project_id')
#     pmids = request.form.get('pmids')

#     # TODO check the pmids and project_id

#     # remove the white space at start and end
#     pmids = pmids.strip()

#     # split by . , \s 
#     pmids = re.split(r'[.,\s]+', pmids)

#     if len(pmids) > 200:
#         pmids = pmids[:200]

#     # get detail by PubMed API
#     data = util.e_summary(pmids)

#     # prepare the return object
#     ret = {
#         'rs': []
#     }

#     uids = data['result']['uids']
#     # check each pmid
#     for pmid in uids:

#         if not util.is_valid_pmid(pmid):
#             # that's weird
#             ret['rs'].append({
#                 'pmid': pmid,
#                 'success': False,
#                 'msg': 'NOT VALID PMID'
#             })
#             continue
        
#         # first check if pmid exists
#         is_existed = False
#         is_existed, _paper = dora.is_existed_paper(project_id, pmid)

#         if is_existed:
#             # that's possible!
#             ret['rs'].append({
#                 'pmid': pmid,
#                 'success': False,
#                 'msg': 'PMID EXISTED'
#             })
#             continue
        
#         # ok, save this pmid
#         paper = data['result'][pmid]
#         title = paper['title']
#         pub_date = paper['sortpubdate'].split(' ')[0]
#         authors = ', '.join([ a['name'] for a in paper['authors'] ])
#         journal = paper['source']

#         paper = dora.create_paper(project_id, pmid, 'pmid',
#             title, pub_date, authors, journal, None, ss_state.SS_ST_AUTO_OTHER
#         )

#         ret['rs'].append({
#             'pmid': pmid,
#             'success': True,
#             'msg': 'PAPER CREATED'
#         })


#     return jsonify(ret)


@bp.route('/import_one_pmid', methods=['POST'])
@login_required
def import_one_pmid():

    # save the uploads
    project_id = request.form.get('project_id')
    pmid = request.form.get('pmid')
    nct = request.form.get('nct')

    project = dora.get_project(project_id)

    if project is None: 
        return jsonify({
            'success': False,
            'is_existed': None,
            'msg': 'project not found'
        })

    # check data
    pmid = pmid.strip()
    nct = nct.strip()

    is_success, paper = srv_import.import_by_pmid(
        project.keystr, 
        pmid,
        nct
    )

    return jsonify({
        'success': is_success,
        'is_existed': False,
        'paper': paper.as_very_simple_dict()
    })



@bp.route('/import_pmids', methods=['GET', 'POST'])
@login_required
def import_pmids():
    if request.method == 'GET':
        return redirect(url_for('importer.index'))

    # save the uploads
    project_id = request.form.get('project_id')
    rs = json.loads(request.form.get('rs'))

    # get the default stage
    stage = request.form.get('stage')

    # convert stage to pr and rs
    ss_pr, ss_rs = ss_state.SS_STAGE_TO_PR_AND_RS[stage]
    ss_ex = create_pr_rs_details('User specified', stage)

    # TODO check the pmids and project_id

    # only import 40
    if len(rs) > 40:
        rs = rs[:40]

    rs_dict = {}
    pmids = []
    pmid2rct_id = {}
    pmid2idx = {}

    # need to track the status of all the records
    # the idx is needed for the frontend
    for r in rs:
        idx = r['idx']
        pmid = r['pmid']

        is_valid = util.is_valid_pmid(pmid)

        if not is_valid:
            # which means it is not a valid id
            rs_dict[idx] = r
            rs_dict[idx]['paper'] = None
            rs_dict[idx]['result'] = 'not pmid'

            print('* not valid PMID: %s' % pmid)
            continue

        rs_dict[idx] = r
        rs_dict[idx]['paper'] = None
        rs_dict[idx]['result'] = 'notfound'

        if r['pmid'] not in pmids:
            pmids.append(pmid)
            pmid2rct_id[pmid] = r['rct_id']
            pmid2idx[pmid] = [idx]
        else:
            rs_dict[idx]['result'] = 'duplicated'
            pmid2idx[pmid].append(idx)

    # before search in PubMed, check local
    exist_papers = dora.get_papers_by_pids(project_id, pmids)
    exist_pmids = [ p.pid for p in exist_papers ]

    # for those existed papers
    for paper in exist_papers:
        pmid = paper.pid
        paper_id = paper.paper_id
        rct_id = pmid2rct_id[pmid]
        # update the stage
        detail_dict = {
            'date_decided': util.get_today_date_str(),
            'reason': settings.SCREENER_REASON_INCLUDED_IN_SR_BY_IMPORT_PMIDS,
            'decision': stage
        }
        
        # Well. just update the information
        _ = dora.set_paper_rct_id(paper_id, rct_id)
        _paper = dora.set_paper_pr_rs_with_details(paper_id, ss_pr, ss_rs, detail_dict)
        
        for idx in pmid2idx[pmid]:
            rs_dict[idx]['result'] = 'existed'
            rs_dict[idx]['paper'] = _paper.as_very_simple_dict()

    # the new pmids are those not in exist_pmids
    new_pmids = list(
        set(pmids).difference(set(exist_pmids))
    )

    # get detail by PubMed API
    if len(new_pmids) == 0:
        # ok, no new studies
        pass
    else:
        # found new pmid!
        print('* found %s new pmids: %s' % (
            len(new_pmids), new_pmids
        ))
        data = util.e_fetch(new_pmids)

        # prepare the return object
        uids = data['result']['uids']
        # check each pmid
        for pmid in uids:
            # ok, save this paper
            pubmed_record = data['result'][pmid]

            # get the attributes
            title = pubmed_record['title']
            abstract = pubmed_record['abstract']
            pub_date = pubmed_record['sortpubdate']
            authors = ', '.join([ a['name'] for a in pubmed_record['authors'] ])
            journal = pubmed_record['source']
            rct_id = pmid2rct_id[pmid]

            is_existed, paper = dora.create_paper_if_not_exist_and_predict_rct(
                project_id, pmid, 'PMID', title, abstract, 
                pub_date, authors, journal,
                {'rct_id': rct_id}, 
                ss_state.SS_ST_IMPORT_SIMPLE_CSV, 
                ss_pr,
                ss_rs,
                ss_ex
            )

            for idx in pmid2idx[pmid]:
                rs_dict[idx]['result'] = 'created'
                rs_dict[idx]['paper'] = paper.as_very_simple_dict()

    return jsonify({
        'success': True,
        'rs': [ rs_dict[idx] for idx in rs_dict ]
    })


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
        df = pd.read_excel(full_fn, dtype=str)
    else:
        df = pd.read_csv(full_fn)

    # prepare the return object
    ret = {
        'success': True,
        'rs': []
    }

    # col0 = df.columns[0]
    # col1 = df.columns[1]

    # # the first col should be the NCT
    # df[col0] = df[col0].apply(lambda v: str(v))

    # # the second col should be the PMID
    # df[col1] = df[col1].apply(lambda v: 'NA' if pd.isna(v) else str(int(v)))

    pprint(df)

    # parse each record
    for idx, row in df.iterrows():
        # get the NCT
        if 'NCT' in row:
            rct_id = row['NCT']
        elif 'NCT ID' in row:
            rct_id = row['NCT ID']
        else:
            rct_id = row.values[0]

        # get the PMID
        if 'PMID' in row:
            pmid = row['PMID']
        elif 'PubMed ID' in row:
            pmid = row['PubMed ID']
        else:
            pmid = row.values[1]
        
        ret['rs'].append({
            'idx': idx,
            'pmid': '%s' % pmid,
            'rct_id': '%s' % rct_id,
            'result': 'waiting'
        })

    return jsonify(ret)


@bp.route('/upload_userinput', methods=['GET', 'POST'])
@login_required
def upload_userinput():
    if request.method == 'GET':
        return ''

    # first, check pid to decide what to do next
    pid = request.form.get('pid').strip()

    if pid == '':
        # ok, need to create a temp pid for this one
        pid, pid_type = util.make_temp_pid()
    else:
        pid_type = 'PubMed / MEDLINE'

    # then check is this ID exists?

    project_id = request.form.get('project_id').strip()
    title = request.form.get('title').strip()
    abstract = request.form.get('abstract').strip()
    pub_date = request.form.get('pub_date').strip()
    authors = request.form.get('authors').strip()
    journal = request.form.get('journal').strip()
    nct = request.form.get('nct').strip()

    # other information could be none
    is_existed, paper = dora.create_paper_if_not_exist_and_predict_rct(
        project_id, pid, pid_type, title, abstract,
        pub_date, authors, journal, {'rct_id': nct}
    )

    if is_existed:
        ret = {
            'success': False,
            'is_existed': is_existed,
            'paper': paper.as_dict()
        }

        return jsonify(ret)


    # get the PDF files
    files = request.files.getlist('files[]')
    pdf_metas = util.save_pdfs_from_request_files(files)

    # update the paper itself
    paper = dora.add_pdfs_to_paper(paper.paper_id, pdf_metas)

    # OK!
    ret = {
        'success': True,
        'is_existed': is_existed,
        'paper': paper.as_dict()
    }

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
    papers, cnt = util.parse_endnote_exported_xml(full_fn)

    if papers is None:
        # which means something wrong with the file
        return jsonify({'success': False, 'msg': 'Not supported file format'})

    ret = {
        "success": True,
        "papers": papers,
        "cnt": cnt
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
        # meta
        meta = {}
        if 'raw_type' in p:
            if p['raw_type'] in ['pubmed_xml', 'endnote_xml', 'ovid_xml']:
                meta['raw_type'] = p['raw_type']
                meta['xml'] = p['xml']
        else:
            meta['raw_type'] = None

        # add the DOI when uploading a new study
        if 'doi' in p:
            meta['doi'] = p['doi']
        else:
            meta['doi'] = ''

        # create
        try:
            is_exist, paper = dora.create_paper_if_not_exist_and_predict_rct(
                project_id, 
                p['pid'], 
                p['pid_type'],
                p['title'],
                p['abstract'],
                util.check_paper_pub_date(p['pub_date']),
                util.check_paper_authors(p['authors']),
                util.check_paper_journal(p['journal']),
                meta,
                ss_state.SS_ST_IMPORT_ENDNOTE_XML,
                ss_pr,
                ss_rs,
                ss_ex,
                None,
            )
        except Exception as err:
            # give some feedback to frontend
            ret['papers'].append({
                'result': 'error',
                'success': False,
                'seq': p['seq']
            })
            continue
        
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
    papers, _ = util.parse_endnote_exported_xml(full_fn)
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



@bp.route('/test', methods=['GET', 'POST'])
@login_required
def test():
    ret = {
        'success': True,
        'msg': '%s' % datetime.datetime.now()
    }
    time.sleep(2)

    return jsonify(ret)