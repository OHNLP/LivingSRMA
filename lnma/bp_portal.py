import os

from flask import request
from flask import redirect
from flask import flash
from flask import render_template
from flask import Blueprint
from flask import current_app
from flask import url_for

from flask_login import login_required
from flask_login import current_user

from werkzeug.utils import secure_filename

from lnma import dora
from lnma import settings

bp = Blueprint("portal", __name__, url_prefix="/portal")

UPLOAD_FOLDER = '/path/to/the/uploads'
ALLOWED_EXTENSIONS = {'png', 'xlsx', 'svg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

        
@bp.route('/')
@login_required
def index():
    return render_template('portal/portal.index.html')


@bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'GET':
        return render_template('portal/portal.upload.html')

    # get basic info
    prj = request.form.get('input_project')
    input_filetype = request.form.get('input_filetype')

    if input_filetype not in settings.PUBWEB_DATAFILES:
        # this type is not defined?
        flash('The file type [%s] is not supported, please contack administrator.' % input_filetype)
        return redirect(url_for('portal.upload'))

    # handle the POST request
    if 'input_datafile' not in request.files:
        flash('No file is selected')
        return redirect(url_for('portal.upload'))

    f = request.files['input_datafile']
    # if user does not select file, browser also
    # submit an empty part without filename
    if f.filename == '':
        flash('No selected file')
        return redirect(url_for('portal.upload'))

    if f and allowed_file(f.filename):
        # use pre defined filename
        filename = settings.PUBWEB_DATAFILES[input_filetype]

        # get the path to the project pub data folder
        full_path = os.path.join(current_app.instance_path, settings.PATH_PUBDATA, prj)
        
        f.save(os.path.join(full_path, filename))

        flash('%s is uploaded!' % (filename))
        return redirect(url_for('portal.upload'))

    else:
        flash('%s is not supported or file error' % (f.filename))
        return redirect(url_for('portal.upload'))
