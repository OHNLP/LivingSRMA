from flask import Blueprint
from flask import render_template
from flask import send_from_directory
from flask import current_app

from flask_login import login_required
from flask_login import current_user

from lnma.settings import *


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


@bp.route('/upload_pdf')
def upload_pdf():
    '''
    Upload PDF files
    '''
    return 'upload'