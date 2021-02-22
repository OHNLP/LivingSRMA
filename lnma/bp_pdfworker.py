import os
import json

from flask import Blueprint
from flask import request
from flask import render_template
from flask import send_from_directory
from flask import current_app
from flask.helpers import send_file
from flask.json import jsonify

from flask_login import login_required
from flask_login import current_user

from lnma import settings
from lnma import util
from lnma import dora


bp = Blueprint("pdfworker", __name__, url_prefix="/pdfworker")

@bp.route('/')
def index():
    return render_template('pdfworker/index.html')


@bp.route('/pdf/<folder>/<fn>')
def pdf(folder, fn):
    return send_from_directory(
        os.path.join(settings.PATH_PDF_FILES, folder),
        fn
    )


@bp.route('/default_pdf')
def default_pdf():
    '''
    The default PDF file for the viewer
    '''
    return send_from_directory(settings.PATH_PDF_FILES, 'default.pdf')


@bp.route('/download_pdf/<folder>/<file_id>')
def download_pdf(folder, file_id):
    download_file_name = request.args.get('fn')
    full_path = os.path.join(
        settings.PATH_PDF_FILES, folder
    )
    file_name = file_id + '.pdf'

    ret = send_file(
        os.path.join(full_path, file_name),
        mimetype="application/pdf",
        as_attachment=True,
        conditional=False
    )

    ret.headers["x-suggested-filename"] = download_file_name

    return ret


@bp.route('/view_pdf')
def view_pdf():
    return render_template('pdfworker/view_pdf.html')


@bp.route('/upload_pdfs', methods=['POST'])
def upload_pdfs():
    '''
    Upload PDF files
    '''
    # for a pdf upload, it require two things
    # 1. the paper_id
    # 2. the PDF files
    if 'files[]' not in request.files:
        return jsonify({
            'success': False,
            'msg': 'missing files'
        })
    # get the info of paper and files
    paper_id = request.form.get('paper_id')
    files = request.files.getlist('files[]')

    # save the files
    pdf_metas = util.save_pdfs_from_request_files(files)
    
    # update the paper itself
    paper = dora.add_pdfs_to_paper(paper_id, pdf_metas)

    # ok
    ret = {
        'success': True,
        'paper': paper.as_simple_dict()
    }
    return jsonify(ret)


@bp.route('/remove_pdf', methods=['POST'])
def remove_pdf():
    '''
    Remove a PDF file from
    '''
    paper_id = request.form.get('paper_id')
    pdf_metas = request.form.get('pdf_metas')
    pdf_metas = json.loads(pdf_metas)

    # delete the pdf files
    for pdf_meta in pdf_metas:
        util.delete_pdf(pdf_meta)

    # remove the records from db
    paper = dora.remove_pdfs_from_paper(paper_id, pdf_metas)

    ret = {
        'success': True,
        'paper': paper.as_simple_dict()
    }
    return jsonify(ret)
    

