import json

from flask import Blueprint
from flask import request
from flask import render_template
from flask import send_from_directory
from flask import current_app
from flask.json import jsonify

from flask_login import login_required
from flask_login import current_user

from lnma import settings
from lnma import util
from lnma import dora


bp = Blueprint("pdfworker", __name__, url_prefix="/")

@bp.route('/')
def index():
    return render_template('pdfworker/index.html')


@bp.route('/f/<fn>')
def f(fn):
    return send_from_directory(TMP_FOLDER, fn)


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
    files = request.files.getlist('files[]')
    paper_id = request.form.get('paper_id')

    # save the files first
    pdf_metas = []
    for file in files:
        if file and allowed_file(file.filename):
            pdf_meta = util.save_pdf(file)
            pdf_metas.append(pdf_meta)
    
    # update the paper itself
    paper = dora.add_pdfs_to_paper(paper_id, pdf_metas)

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
    

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in settings.ALLOWED_PDF_UPLOAD_EXTENSIONS
