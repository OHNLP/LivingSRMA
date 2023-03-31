import os
import json
import math
import copy
import random
from re import template
import string

from pprint import pprint

import pandas as pd

from flask import request
from flask import flash
from flask import render_template
from flask import Blueprint
from flask import current_app
from flask import redirect
from flask import url_for
from flask import jsonify

from flask_login import login_required
from flask_login import current_user
from flask_login.utils import login_fresh

from lnma import dora
from lnma import util
from lnma import ss_state
from lnma import settings
from lnma import srv_paper
from lnma import srv_extract

bp = Blueprint("extractor", __name__, url_prefix="/extractor")
template_base = 'extractor/'

@bp.route('/v1')
@login_required
def v1():
    project_id = request.cookies.get('project_id')
    cq_abbr = request.cookies.get('cq_abbr')

    if project_id is None:
        return redirect(url_for('project.mylist'))

    if cq_abbr is None:
        cq_abbr = 'default'

    project = dora.get_project(project_id)

    return render_template(
        'extractor/v1.html',
        cq_abbr=cq_abbr,
        project=project,
        project_json_str=json.dumps(project.as_dict())
    )


@bp.route('/manage_outcomes')
@login_required
def manage_outcomes():
    project_id = request.cookies.get('project_id')
    cq_abbr = request.cookies.get('cq_abbr')

    if project_id is None:
        return redirect(url_for('project.mylist'))

    if cq_abbr is None:
        cq_abbr = 'default'

    project = dora.get_project(project_id)

    return render_template(
        template_base + 'manage_outcomes.html',
        cq_abbr=cq_abbr,
        project=project,
        project_json_str=json.dumps(project.as_dict())
    )


@bp.route('/manage_itable')
@login_required
def manage_itable():
    '''
    Design the ITable
    '''
    project_id = request.cookies.get('project_id')

    if project_id is None:
        return redirect(url_for('project.mylist'))

    # decide which cq to use
    cq_abbr = request.cookies.get('cq_abbr')
    if cq_abbr is None:
        cq_abbr = 'default'

    project = dora.get_project(project_id)

    return render_template(
        template_base + 'manage_itable.html',
        cq_abbr=cq_abbr,
        project=project,
        project_json_str=json.dumps(project.as_dict())
    )


@bp.route('/extract_by_paper')
@login_required
def extract_by_paper():
    project_id = request.cookies.get('project_id')

    if project_id is None:
        return redirect(url_for('project.mylist'))

    # decide which cq to use
    cq_abbr = request.cookies.get('cq_abbr')
    if cq_abbr is None:
        cq_abbr = 'default'

    project = dora.get_project(project_id)

    return render_template(
        template_base + 'extract_by_paper.html',
        cq_abbr=cq_abbr,
        project=project,
        project_json_str=json.dumps(project.as_dict())
    )


@bp.route('/extract_by_outcome')
@login_required
def extract_by_outcome():
    '''
    Extract data
    '''
    project_id = request.cookies.get('project_id')
    # project_id = request.args.get('project_id')
    if project_id is None:
        return redirect(url_for('project.mylist'))

    # decide which cq to use
    cq_abbr = request.cookies.get('cq_abbr')
    if cq_abbr is None:
        cq_abbr = 'default'

    oc_abbr = request.args.get('abbr')
    project = dora.get_project(project_id)

    return render_template(
        template_base + 'extract_by_outcome.html', 
        oc_abbr=oc_abbr,
        cq_abbr=cq_abbr,
        project=project,
        project_json_str=json.dumps(project.as_dict())
    )


@bp.route('/extract_coe')
@login_required
def extract_coe():
    '''
    Extract CoE
    '''
    project_id = request.cookies.get('project_id')
    # project_id = request.args.get('project_id')
    if project_id is None:
        return redirect(url_for('project.mylist'))

    # decide which cq to use
    cq_abbr = request.cookies.get('cq_abbr')
    if cq_abbr is None:
        cq_abbr = 'default'

    oc_abbr = request.args.get('abbr')

    project = dora.get_project(project_id)

    return render_template(
        template_base + 'extract_coe.html', 
        oc_abbr=oc_abbr,
        cq_abbr=cq_abbr,
        project=project,
        project_json_str=json.dumps(project.as_dict())
    )



###########################################################
# APIs for extraction
###########################################################

@bp.route('/get_fill_wp_attrs')
@login_required
def get_fill_wp_attrs():
    '''
    Get working paper auto fill

    The auto fill is a tool copy the text from itable to an outcome.
    So, in the backend, we need to get the followings:

    1. the `from` and `to` pairs for a specific project
    2. the `pids` which are working on
    2. search the itable extraction and find the text
    
    But this is very difficult.
    '''

    return ''



@bp.route('/get_paper')
@login_required
def get_paper():
    project_id = request.args.get('project_id')
    project_id = request.cookies.get('project_id')
    pid = request.args.get('pid')

    paper = dora.get_paper_by_project_id_and_pid(project_id, pid)

    if paper is None:
        ret = {
            'success': False,
            'paper': None
        }
    else:
        json_paper = paper.as_dict()

        ret = {
            'success': True,
            'paper': json_paper
        }
    return jsonify(ret)


@bp.route('/get_papers_by_stage')
@login_required
def get_papers_by_stage():
    project_id = request.args.get('project_id')
    stage = request.args.get('stage')
    papers = dora.get_papers_by_stage(project_id, stage)
    json_papers = [ p.as_very_simple_dict() for p in papers ]

    ret = {
        'success': True,
        'msg': '',
        'papers': json_papers
    }
    return jsonify(ret)



@bp.route('/download_extract_rs_csv')
@login_required
def download_extract_rs_csv():
    '''
    Get the extracted records 
    '''
    extract_id = request.args.get('extract_id')

    if extract_id is None:
        return 'extract_id is required'

    # get the extract by its id
    extract = dora.get_extract(extract_id)

    if extract is None:
        return 'no such extract'

    papers = srv_paper.get_included_papers_by_cq(
        extract.project_id, 
        extract.meta['cq_abbr']
    )

    # make a dictionary for lookup
    paper_dict = {}
    for paper in papers:
        paper_dict[paper.pid] = paper

    # get raw rs
    rscfg = extract.get_raw_rs_cfg(
        paper_dict,
        True
    )

    # just need the rs
    rs = rscfg['rs']

    if len(rs) == 0:
        return ''

    # get the columns
    columns = rs[0].keys()

    print("* download_extract_rs_csv rscfg: %s" % (rs))

    # build df
    import io
    import csv
    output = io.StringIO()

    writer = csv.DictWriter(
        output, 
        fieldnames=columns, 
        delimiter=','
    )
    writer.writeheader()
    writer.writerows(rs)
    txt = output.getvalue()

    return txt


@bp.route('/update_paper_one_selection', methods=['POST'])
@login_required
def update_paper_one_selection():
    '''
    Update just one selection for a paper
    '''
    project_id = request.form.get('project_id')
    cq_abbr = request.form.get('cq_abbr')
    pid = request.form.get('pid')
    abbr = request.form.get('abbr')
    is_selected = request.form.get('is_selected')
    is_selected = True if is_selected.lower() == 'true' else False

    # update status
    paper, extract, piece = dora.update_paper_selection(
        project_id, 
        cq_abbr,
        pid, 
        abbr, 
        is_selected
    )

    msg = 'Updated %s %s %s' % (
        paper.get_short_name(),
        'selected in' if is_selected else 'removed from',
        extract.get_short_title()
    )

    ret = {
        'success': True,
        'msg': msg,
        'data': {
            'cq_abbr': cq_abbr,
            'pid': pid,
            'abbr': abbr,
            'is_selected': is_selected,
            'piece': piece.as_dict()
        }
    }

    return jsonify(ret)


@bp.route('/update_paper_selections', methods=['POST'])
@login_required
def update_paper_selections():
    project_id = request.form.get('project_id')
    cq_abbr = request.form.get('cq_abbr')
    abbrs = request.form.getlist('abbrs[]')
    pid = request.form.get('pid')

    # update the extract with given info
    paper, outcome_selections = dora.update_paper_selections(
        project_id, cq_abbr, pid, abbrs
    )

    # bind the outcome selections to meta
    paper.meta['outcome_selections'] = outcome_selections

    # build the return obj
    ret = {
        'success': True,
        'msg': '',
        'paper': paper.as_dict()
    }
    return jsonify(ret)


@bp.route('/create_extract', methods=['POST'])
@login_required
def create_extract():
    project_id = request.form.get('project_id')
    oc_type = request.form.get('oc_type')
    abbr = request.form.get('abbr')
    meta = json.loads(request.form.get('meta'))
    data = json.loads(request.form.get('data'))

    # check if exists first
    extract = dora.get_extract_by_project_id_and_abbr(
        project_id, abbr
    )
    if extract is not None:
        # if get the exisiting extracts
        ret = {
            'success': False,
            'msg': 'exists extract %s' % abbr,
            'extract': extract.as_dict()
        }
        return jsonify(ret)

    # ok, not exists! create!
    extract = dora.create_extract(
        project_id,
        oc_type,
        abbr,
        meta,
        data
    )

    # build the return obj
    ret = {
        'success': True,
        'msg': '',
        'extract': extract.as_dict()
    }
    return jsonify(ret)


@bp.route('/get_extract_and_papers')
@login_required
def get_extract_and_papers():
    project_id = request.args.get('project_id')
    cq_abbr = request.args.get('cq_abbr')
    abbr = request.args.get('abbr')
    
    # get the exisiting extracts
    extract = dora.get_extract_by_project_id_and_abbr(
        project_id, 
        abbr
    )

    old_data = copy.deepcopy(extract.data)

    if extract is None:
        # this is a new extract
        ret = {
            'success': False,
            'msg': 'not exist extract %s' % abbr
        }
        return jsonify(ret)

    # get papers
    papers = srv_paper.get_included_papers_by_cq(
        project_id, 
        cq_abbr
    )
    
    # update the meta
    extract.update_meta()

    # 2023-01-28: use piece to fill the data
    extract = dora.attach_extract_data(extract)

    # update the extract with papers
    # extract.update_data_by_papers(papers)
    extract_json = extract.as_dict()
    extract_json['old_data'] = old_data

    # make the return object
    ret = {
        'success': True,
        'msg': '',
        'extract': extract_json,
        'papers': [ p.as_very_simple_dict() for p in papers ]
    }
    return jsonify(ret)


@bp.route('/update_extract', methods=['POST'])
@login_required
def update_extract():
    '''
    Deprecated
    Update the extract meta and data
    '''
    project_id = request.form.get('project_id')
    oc_type = request.form.get('oc_type')
    abbr = request.form.get('abbr')

    # the meta of the extract settings
    meta = json.loads(request.form.get('meta'))

    # the data of the extracted infos
    data = json.loads(request.form.get('data'))
    
    # update the extract with given info
    extract = dora.update_extract_meta_and_data(
        project_id, oc_type, abbr, meta, data
    )

    # build the return obj
    ret = {
        'success': True,
        'msg': '',
        'extract': extract.as_dict()
    }
    return jsonify(ret)


@bp.route('/update_extract_meta', methods=['POST'])
@login_required
def update_extract_meta():
    '''
    Update the extract meta
    '''
    project_id = request.form.get('project_id')
    oc_type = request.form.get('oc_type')
    abbr = request.form.get('abbr')
    # the meta of the extract settings
    meta = json.loads(request.form.get('meta'))
    
    # update the extract with given info
    extract = dora.update_extract_meta(
        project_id, oc_type, abbr, meta
    )

    # build the return obj
    ret = {
        'success': True,
        'msg': '',
        'extract': extract.as_dict()
    }
    return jsonify(ret)


@bp.route('/update_extract_data', methods=['POST'])
@login_required
def update_extract_data():
    '''
    Update the extract data
    '''
    project_id = request.form.get('project_id')
    oc_type = request.form.get('oc_type')
    abbr = request.form.get('abbr')
    # the meta of the extract settings
    data = json.loads(request.form.get('data'))
    
    # update the extract with given info
    extract = dora.update_extract_data(
        project_id, oc_type, abbr, data
    )

    # build the return obj
    ret = {
        'success': True,
        'msg': '',
        'extract': extract.as_dict()
    }
    return jsonify(ret)


@bp.route('/update_extract_incr_data', methods=['POST'])
@login_required
def update_extract_incr_data():
    '''
    Update the extract data
    '''
    project_id = request.form.get('project_id')
    oc_type = request.form.get('oc_type')
    extract_id = request.form.get('extract_id')
    flag_skip_is_selected = request.form.get('flag_sis') == 'yes'
    
    # the meta of the extract settings
    data = json.loads(request.form.get('data'))
    
    # update the extract with given info
    extract, pieces = dora.update_extract_incr_data(
        extract_id, 
        data,
        flag_skip_is_selected
    )

    # build the return obj
    ret = {
        'success': True,
        'msg': '',
        'extract': extract.as_simple_dict()
    }
    return jsonify(ret)


@bp.route('/update_extract_coe_meta', methods=['POST'])
@login_required
def update_extract_coe_meta():
    '''
    Update the extract coe data
    '''
    extract_id = request.form.get('extract_id')
    
    # the meta of the extract settings
    coe = json.loads(request.form.get('coe'))
    
    # update the extract with given info
    extract = dora.update_extract_coe_meta(
        extract_id,
        coe
    )

    # build the return obj
    ret = {
        'success': True,
        'msg': '',
        'extract': extract.as_dict()
    }
    return jsonify(ret)


@bp.route('/copy_extract', methods=['POST'])
@login_required
def copy_extract():
    project_id = request.form.get('project_id')
    oc_type = request.form.get('oc_type')
    abbr = request.form.get('abbr')
    # the meta of the extract settings
    meta = json.loads(request.form.get('meta'))
    # the data of the extracted infos
    data = json.loads(request.form.get('data'))

    # the new extract
    new_abbr = request.form.get('new_abbr')
    new_full_name = request.form.get('new_full_name')
    
    # update the extract with given info
    _ = dora.update_extract_meta_and_data(
        project_id, oc_type, abbr, meta, data
    )

    # update the meta
    meta['abbr'] = new_abbr
    meta['full_name'] = new_full_name

    # save the extract with given info
    extract = dora.create_extract(
        project_id, oc_type, new_abbr, meta, data
    )

    # build the return obj
    ret = {
        'success': True,
        'msg': '',
        'extract': extract.as_dict()
    }
    return jsonify(ret)


@bp.route('/delete_extract', methods=['POST'])
@login_required
def delete_extract():
    project_id = request.form.get('project_id')
    oc_type = request.form.get('oc_type')
    abbr = request.form.get('abbr')
    
    # get the exisiting extracts
    _ = dora.delete_extract(project_id, oc_type, abbr)

    # build the return obj
    ret = {
        'success': True,
        'msg': ''
    }
    return jsonify(ret)


@bp.route('/get_pdata_in_extract')
@login_required
def get_pdata_in_extract():
    '''
    Get one paper in an extract by the project_id and the abbr and the pid
    '''
    project_id = request.args.get('project_id')
    abbr = request.args.get('abbr')
    pid = request.args.get('pid')
    
    # get the exisiting extracts
    extract = dora.get_extract_by_project_id_and_abbr(project_id, abbr)

    if extract is None:
        # this is a new extract
        ret = {
            'success': False,
            'abbr': abbr,
            'pid': pid,
            'msg': 'not exist extract %s' % abbr
        }
        return jsonify(ret)

    if pid not in extract.data:
        # this is a missing?
        ret = {
            'success': False,
            'abbr': abbr,
            'pid': pid,
            'msg': 'no paper data in itable'
        }
        return jsonify(ret)

    ret = {
        'success': True,
        'msg': '',
        'extract': extract.as_dict(),
    }

    # just keep the pid in extract
    ret['extract']['data'] = {
        pid: ret['extract']['data'][pid]
    }

    return jsonify(ret)


@bp.route('/get_pdata_in_itable')
@login_required
def get_pdata_in_itable():
    '''
    Get one paper in an itable by the project_id and the cq_abbr and the pid
    '''
    project_id = request.args.get('project_id')
    cq_abbr = request.args.get('cq_abbr')
    pid = request.args.get('pid')
    
    # get the exisiting extracts
    extract = srv_extract.get_itable_by_project_id_and_cq_abbr(
        project_id, cq_abbr
    )

    if extract is None:
        # this is a new extract
        ret = {
            'success': False,
            'abbr': None,
            'cq_abbr': cq_abbr,
            'pid': pid,
            'msg': 'not exist itable in cq %s' % cq_abbr
        }
        return jsonify(ret)

    if pid not in extract.data:
        # this is a missing?
        ret = {
            'success': False,
            'abbr': extract.abbr,
            'cq_abbr': cq_abbr,
            'pid': pid,
            'msg': 'no paper data in itable in cq %s' % cq_abbr
        }
        return jsonify(ret)

    ret = {
        'success': True,
        'msg': '',
        'extract': extract.as_dict(),
    }

    # just keep only ONE pid in extract
    # we don't need to send all results to user
    ret['extract']['data'] = {
        pid: ret['extract']['data'][pid]
    }

    return jsonify(ret)


@bp.route('/get_itable')
@login_required
def get_itable():
    '''
    Get one extract by the project_id and the abbr
    '''
    project_id = request.args.get('project_id')
    cq_abbr = request.args.get('cq_abbr')
    
    # get the exisiting extracts
    extract = dora.get_itable_by_project_id_and_cq(
        project_id, 
        cq_abbr
    )

    if extract is None:
        # this is a new extract
        ret = {
            'success': False,
            'msg': 'not exist itable for cq %s' % cq_abbr
        }
        return jsonify(ret)

    ret = {
        'success': True,
        'msg': '',
        'extract': extract.as_dict()
    }
    return jsonify(ret)


@bp.route('/get_extract_by_id')
@login_required
def get_extract_by_id():
    '''
    Get one extract by the extract_id
    '''
    extract_id = request.args.get('extract_id')
    
    # get the exisiting extracts
    extract = dora.get_extract(
        extract_id
    )

    if extract is None:
        # this is a new extract
        ret = {
            'success': False,
            'msg': 'not exist extract %s' % extract_id
        }
        return jsonify(ret)

    ret = {
        'success': True,
        'msg': '',
        'extract': extract.as_dict()
    }
    return jsonify(ret)


@bp.route('/get_extract')
@login_required
def get_extract():
    '''
    Get one extract by the project_id and the abbr
    '''
    project_id = request.args.get('project_id')
    cq_abbr = request.args.get('cq_abbr')
    abbr = request.args.get('abbr')
    
    # get the exisiting extracts
    extract = dora.get_extract_by_project_id_and_cq_and_abbr(
        project_id, 
        cq_abbr, 
        abbr
    )

    if extract is None:
        # this is a new extract
        ret = {
            'success': False,
            'msg': 'not exist extract %s' % abbr
        }
        return jsonify(ret)

    ret = {
        'success': True,
        'msg': '',
        'extract': extract.as_dict()
    }
    return jsonify(ret)


@bp.route('/get_extracts')
@login_required
def get_extracts():
    '''
    Get all of the extracts by the project_id
    '''
    project_id = request.args.get('project_id')

    if project_id is None:
        ret = {
            'success': False,
            'msg': 'project_id is required'
        }
        return jsonify(ret)

    with_data = request.args.get('with_data')
    
    # decide which cq to use
    # cq_abbr = request.cookies.get('cq_abbr')
    cq_abbr = request.args.get('cq_abbr')

    if cq_abbr is None:
        cq_abbr = 'default'

    if with_data == 'yes':
        with_data = True
    else:
        with_data = False
    
    # get the exisiting extracts
    extracts = dora.get_extracts_by_project_id_and_cq(
        project_id,
        cq_abbr
    )

    for i in range(len(extracts)):
        extracts[i].update_meta()

    # build the return obj
    if with_data:
        ret = {
            'success': True,
            'msg': '',
            'extracts': [ extr.as_dict() for extr in extracts ]
        }
    else:
        ret = {
            'success': True,
            'msg': '',
            'extracts': [ extr.as_simple_dict() for extr in extracts ]
        }
        
    return jsonify(ret)


###############################################################################
# Update the RCT sequence for a project 
###############################################################################

@bp.route('/sort_rct_seq')
@login_required
def sort_rct_seq():
    '''
    Sort the RCT origin or followup
    '''
    project_id = request.cookies.get('project_id')

    papers = dora.sort_paper_rct_seq_in_project(project_id)

    ret = {
        'success': True,
        'msg': 'sorted RCT sequences',
        'papers': [ p.as_very_simple_dict() for p in papers ]
    }
    return jsonify(ret)


###############################################################################
# Importers 
###############################################################################

@bp.route('/import_itable')
@login_required
def import_itable():
    '''
    Import or update the meta for itable

    Including:

    1. meta data for attributes
    2. data of extraction
    3. filters
    '''
    prj = request.args.get('prj')
    cq = request.args.get('cq')
    # itable = import_itable_from_xls(prj, cq)
    itable = None

    # build the return obj
    ret = {
        'success': itable is not None,
        'extract': itable.as_dict() if itable is not None else None
    }
    return jsonify(ret)


@bp.route('/import_softable_pma')
@login_required
def import_softable_pma():
    '''
    Create the meta for itable
    '''
    prj = request.args.get('prj')
    cq = request.args.get('cq')
    extracts = import_softable_pma_from_xls(prj, cq)

    ret = {
        'success': True,
        'extracts': [ ext.as_dict() for ext in extracts ]
    }

    return jsonify(ret)


###############################################################################
# Utils for the softable import
###############################################################################


def import_softable_pma_from_xls(keystr, cq_abbr, fn, group='primary'):
    '''
    Import the softable data from XLS
    '''
    if keystr == 'IO':
        return import_softable_pma_from_xls_for_IO(fn, group=group)

    raise Exception('Not implemented')


def import_softable_nma_from_xls(keystr, cq_abbr):
    '''
    Import the softable data from XLS
    '''
    raise Exception('Not implemented')


def import_softable_pma_from_xls_for_IO(fn, group='primary'):
    '''
    A special tool for importing the data file for IO project

    The data must follow this order:
    
    1. itable data / study chars 
    2. Adverse events / the category
    3. Bronchits / AE lists

    The fn could be any

    '''
    prj = 'IO'
    # ret = get_ae_pma_data(full_fn, is_getting_sms=False)
    project = dora.get_project_by_keystr(prj)
    project_id = project.project_id

    # First, create a row->pmid dictionary
    # Use the second tab
    # fn = 'ALL_DATA.xls'
    full_fn = os.path.join(
        current_app.instance_path, 
        settings.PATH_PUBDATA, 
        prj, fn
    )
    xls = pd.ExcelFile(full_fn)
    print('* load xls %s' % full_fn)
    df = xls.parse(xls.sheet_names[0], skiprows=1)
    idx2pmid = {}
    for idx, row in df.iterrows():
        idx2pmid[idx] = row['PMID']

    # Second, create tab->cate+tab dictionary
    dft = xls.parse(xls.sheet_names[1])
    ae_dict = {}
    ae_list = []
    for col in dft.columns:
        ae_cate = col
        ae_names = dft[col][~dft[col].isna()]
        ae_item = {
            'ae_cate': ae_cate,
            'ae_names': []
        }
        # build ae_name dict
        for ae_name in ae_names:
            # remove the white space
            ae_name = ae_name.strip()
            if ae_name in ae_dict:
                cate1 = ae_dict[ae_name]
                print('! duplicate %s in [%s] and [%s]' % (ae_name, cate1, ae_cate))
                continue
            ae_dict[ae_name] = ae_cate
            ae_item['ae_names'].append(ae_name)

        ae_list.append(ae_item)
            
        print('* parsed ae_cate %s with %s names' % (col, len(ae_names)))
    print('* created ae_dict %s terms' % (len(ae_dict)))

    # Third, loop on tabs
    cols = ['author', 'year', 'GA_Et', 'GA_Nt', 'GA_Ec', 'GA_Nc', 
            'G34_Et', 'G34_Ec', 'G3H_Et', 'G3H_Ec', 'G5N_Et', 'G5N_Ec', 
            'treatment', 'control']

    # each sheet is an AE/OC
    # the data tab starts from 8th
    outcomes = []
    print('* start parsing %s sheets: %s' % (
        len(xls.sheet_names[2:]), 
        xls.sheet_names[2:]
    ))
    for sheet_name in xls.sheet_names[2:]:
        print('* parsing %s' % (sheet_name))
        ae_name = sheet_name

        # create an empty meta
        ae_meta = json.loads(json.dumps(settings.OC_TYPE_TPL['pwma']['default']))
        
        # update the abbr
        ae_meta['abbr'] = util.oc_abbr()

        # update the cate
        ae_meta['category'] = ae_dict[ae_name]

        # update the group
        ae_meta['group'] = group

        # update the full name
        ae_meta['full_name'] = ae_name

        # update the input format for this project?
        ae_meta['input_format'] = 'PRIM_CAT_RAW_G5'

        # update the cate_attrs
        ae_meta['cate_attrs'] = json.loads(json.dumps(settings.INPUT_FORMAT_TPL['pwma']['PRIM_CAT_RAW_G5']))

        # get the data part
        dft = xls.parse(sheet_name, skiprows=1, usecols='A:N', names=cols)
        dft = dft[~dft.author.isna()]
        ae_data = {}
        for idx, row in dft.iterrows():
            if idx in idx2pmid:
                pmid = idx2pmid[idx]
            else:
                print('* ERROR!! Study row %s %s not defined in all studies' % (
                    idx, row[cols[0]]
                ))
                continue

            is_main = False
            if pmid not in ae_data:
                # ok, new record
                ae_data[pmid] = {
                    'is_selected': True,
                    'is_checked': True,
                    'n_arms': 2,
                    'attrs': {
                        'main': {},
                        'other': []
                    }
                }
                is_main = True
            else:
                ae_data[pmid]['n_arms'] += 1
                ae_data[pmid]['attrs']['other'].append({})

            # collect all values in the col
            for col in cols[2:]:
                # the first two cols are not used
                val = row[col]
                
                if pd.isna(val): val = None

                if is_main:
                    ae_data[pmid]['attrs']['main'][col] = val
                else:
                    ae_data[pmid]['attrs']['other'][-1][col] = val

        outcomes.append([
            ae_meta, ae_data
        ])

    # finally, save all
    oc_type = 'pwma'

    extracts = []
    for oc in outcomes:
        extract = dora.create_extract(
            project_id, 
            oc_type, 
            oc[0]['abbr'], 
            oc[0],
            oc[1]
        )
        print('* imported pwma extract %s' % (
            extract.meta['full_name']
        ))
        extracts.append(extract)

    # return!
    return extracts


@bp.route('/get_extract_piece')
@login_required
def get_extract_piece():
    '''
    Get extract piece
    '''
    project_id = request.args.get('project_id')
    extract_id = request.args.get('extract_id')
    pid = request.args.get('pid')
    
    piece = dora.get_piece_by_project_id_and_abbr_and_pid(
        project_id,
        extract_id,
        pid
    )

    if piece is None:
        return jsonify({
            'success': False,
            'data': {
                'piece': None
            }
        })

    return jsonify({
        'success': True,
        'data': {
            'piece': piece.as_dict()
        }
    })


@bp.route('/update_extract_piece', methods=['POST'])
@login_required
def update_extract_piece():
    '''
    Get extract piece
    '''
    piece_json = json.loads(request.form.get('piece'))

    if 'piece_id' in piece_json:
        # which means this is an existing piece
        piece = dora.update_piece_data_by_id(
            piece_json['piece_id'],
            piece_json['data']
        )
    
    else:
        # it's a new piece!
        piece = dora.create_piece(
            piece_json['project_id'],
            piece_json['extract_id'],
            piece_json['pid'],
            piece_json['data']
        )

    return jsonify({
        'success': True,
        'msg': 'Updated extract piece',
        'data': {
            'piece': piece.as_dict()
        }
    })


@bp.route('/get_included_papers_and_selections')
@login_required
def get_included_papers_and_selections():
    '''
    Get the included papers and the decisions of selection for outcomes
    '''
    project_id = request.args.get('project_id')
    cq_abbr = request.args.get('cq_abbr')

    if cq_abbr is None:
        cq_abbr = 'default'
    
    # get this project
    project = dora.get_project(project_id)

    # get all papers
    papers = srv_paper.get_included_papers_by_cq(
        project_id, 
        cq_abbr
    )
        
    # get all extracts
    # itable, pwma, subg, nma
    extracts = dora.get_extracts_by_project_id_and_cq(
        project_id,
        cq_abbr
    )

    papers, extracts = dora.update_papers_outcome_selections(
        project,
        papers,
        extracts
    )

    # extend the paper meta with a new attribute
    # outcome_selections
    # and make a pid -> sequence mapping
    # pid2seq = {}
    # for i, paper in enumerate(papers):
    #     pid2seq[paper.pid] = i
    #     papers[i].meta['outcome_selections'] = []

    # check each extract
    # for extract in extracts:
    #     for pid in extract.data:
    #         if pid in pid2seq:
    #             seq = pid2seq[pid]
    #             if extract.data[pid]['is_selected']:
    #                 # this paper is selected for this outcome
    #                 papers[seq].meta['outcome_selections'].append(
    #                     extract.abbr
    #                 )
    #         else:
    #             # something wrong, this study should be there
    #             # but also maybe excluded
    #             # so, just ignore
    #             pass
    
    json_papers = [ p.as_very_simple_dict() for p in papers ]
    json_extracts = [ extr.as_simple_dict() for extr in extracts ]
    # json_extracts = [ extr.as_simple_dict() for extr in extracts ]

    ret = {
        'success': True,
        'msg': '',
        'papers': json_papers,
        'extracts': json_extracts
    }
    return jsonify(ret)
