from flask import request
from flask import flash
from flask import render_template
from flask import Blueprint
from flask import redirect
from flask import url_for

from flask_login import login_required
from flask_login import current_user

from lnma import dora

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
    pmids = request.form.get('pmids')

    # TODO check the pmids

    return 'TBD'
