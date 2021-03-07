from flask import Blueprint
from flask import render_template
from flask import send_from_directory
from flask import current_app
from flask import Response

from flask_login import login_required
from flask_login import current_user

import pandas as pd

from lnma import ss_state
from lnma import settings
from lnma import dora

bp = Blueprint("exporter", __name__, url_prefix="/exporter")

@bp.route('/')
def index():
    return render_template('index.html')


@login_required
@bp.route('/get_dataset/<prj>.json')
def get_dataset(prj):
    '''
    Get the dataset from a project keystr
    '''
    papers = dora.get_papers_by_keystr(prj)

    rs = []
    cnt = {
        0: 0,
        1: 0
    }
    
    for paper in papers:
        decision = 0
        if paper.ss_rs in [
            ss_state.SS_RS_INCLUDED_ONLY_MA,
            ss_state.SS_RS_INCLUDED_ONLY_SR,
            ss_state.SS_RS_INCLUDED_SRMA,
            ss_state.SS_RS_EXCLUDED_UPDATE
        ]:
            decision = 1
        cnt[decision] += 1

        r = {
            'seq_num': paper.seq_num,
            'pid': paper.pid,
            'pid_type': paper.pid_type,
            'title': paper.title,
            'pub_date': paper.pub_date,
            'abstract': paper.abstract,
            'decision': decision
        }
        rs.append(r)

    df = pd.DataFrame(rs)

    return Response(
        df.to_json(),
        mimetype="application/json",
        headers={
            "Content-disposition":
            "attachment; filename=%s-%s-%s.json" % (prj, len(papers), cnt[1])
        }
    )
