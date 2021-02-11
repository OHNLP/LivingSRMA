import os
import uuid
from flask.helpers import send_from_directory
from flask.helpers import send_file

import pandas as pd

from flask import request
from flask import flash
from flask import render_template
from flask import Blueprint
from flask import current_app

from flask_login import login_required
from flask_login import current_user

from lnma import dora, settings
from lnma import util

bp = Blueprint("collector", __name__, url_prefix="/collector")


@bp.route('/')
@login_required
def index():
    return render_template('collector.index.html')


@bp.route('/export', methods=['POST'])
@login_required
def export():
    project_id = request.form.get('project_id')
    seq_nums = request.form.get('seq_nums')
    format = request.form.get('format')

    seq_nums = seq_nums.split(',')

    # get the papers
    papers = dora.get_papers_by_seq_nums(project_id, seq_nums)

    if format == 'endnote_xml':
        fn = _export_endnote_xml(papers)
        mimetype = 'text/xml'
        filename = 'EndNote-export-%d.xml' % len(papers)

    elif format == 'ovid_xml':
        fn = _export_ovid_xml(papers)
        mimetype = 'text/xml'
        filename = 'OVID-export-%d.xml' % len(papers)

    elif format == 'ct01_csv':
        fn = _export_ct01_csv(papers)
        mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        filename = 'Excel-export-%d.xlsx' % len(papers)

    else:
        fn = _export_ovid_xml(papers)
        mimetype = 'text/xml'
        filename = 'OVID-export-%d.xml' % len(papers)

    return send_file(
        os.path.join(
            settings.TMP_FOLDER,
            fn
        ),
        mimetype=mimetype,
        as_attachment=True,
        attachment_filename=filename
    )


def _export_endnote_xml(papers):
    '''
    Export the papers as EndNote XML format
    '''
    xmls = [ p.as_endnote_xml() for p in papers ]
    s = '\n'.join(xmls)
    xml_text = """<?xml version="1.0" encoding="utf-8"?>
<xml>
<records>
%s
</records>
</xml>""" % s

    # generate the file name
    fn = str(uuid.uuid4()) + '.xml'
    full_fn = os.path.join(
        settings.TMP_FOLDER,
        fn
    )

    # write the xml content to an tmp file
    with open(full_fn, 'w') as f:
        f.write(xml_text)

    return fn


def _export_ovid_xml(papers):
    '''
    Export the papers as OVID XML format
    '''
    xmls = [ p.as_ovid_xml() for p in papers ]
    s = '\n'.join(xmls)
    xml_text = """<?xml version="1.0" encoding="utf-8"?>
<ovidresults>
<records>
%s
</records>
</ovidresults>""" % s
    
    # generate the file name
    fn = str(uuid.uuid4()) + '.xml'
    full_fn = os.path.join(
        settings.TMP_FOLDER,
        fn
    )

    # write the xml content to an tmp file
    with open(full_fn, 'w') as f:
        f.write(xml_text)

    return fn


def _export_ct01_csv(papers):
    '''
    Export the papers as Customized Type 
    '''
    # import HTMLParser
    # htmlparser = HTMLParser.HTMLParser()
# htmlparser.unescape(paper.journal)
    ps = []
    for paper in papers:
        authors = paper.authors.split(';')
        p = {
            'NCT': paper.meta['rct_id'],
            'PMID': paper.pid,
            'Journal Name': paper.journal,
            'Year of Publication': util.get_year(paper.pub_date),
            'Number of Authors': len(authors),
            'Number of Citations': '',            
        }
        for i, au in enumerate(authors):
            p['Author %d' % (i+1)] = au

        ps.append(p)
    
    # create a data frame to hold all of the data
    df = pd.DataFrame(ps)

    # generate the file name
    fn = str(uuid.uuid4()) + '.xlsx'
    full_fn = os.path.join(
        settings.TMP_FOLDER,
        fn
    )

    # save!
    df.to_excel(full_fn)

    return fn
