import os
import json
import random
from re import template
import string
from collections import OrderedDict

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

bp = Blueprint("extractor", __name__, url_prefix="/extractor")
template_base = 'extractor/'

@bp.route('/v1')
@login_required
def v1():
    project_id = request.cookies.get('project_id')

    if project_id is None:
        return redirect(url_for('project.mylist'))

    project = dora.get_project(project_id)

    return render_template(
        'extractor/v1.html',
        project=project,
        project_json_str=json.dumps(project.as_dict())
    )


@bp.route('/manage_outcomes')
@login_required
def manage_outcomes():
    project_id = request.cookies.get('project_id')

    if project_id is None:
        return redirect(url_for('project.mylist'))

    project = dora.get_project(project_id)

    return render_template(
        template_base + 'manage_outcomes.html',
        project=project,
        project_json_str=json.dumps(project.as_dict())
    )


@bp.route('/manage_selections')
@login_required
def manage_selections():
    project_id = request.cookies.get('project_id')

    if project_id is None:
        return redirect(url_for('project.mylist'))

    project = dora.get_project(project_id)

    return render_template(
        template_base + 'manage_selections.html',
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

    project = dora.get_project(project_id)

    return render_template(
        template_base + 'manage_itable.html',
        project=project,
        project_json_str=json.dumps(project.as_dict())
    )


@bp.route('/extract_data')
@login_required
def extract_data():
    '''
    Extract data
    '''
    project_id = request.cookies.get('project_id')
    # project_id = request.args.get('project_id')
    if project_id is None:
        return redirect(url_for('project.mylist'))

    oc_abbr = request.args.get('abbr')
    project = dora.get_project(project_id)

    return render_template(
        template_base + 'extract_data.html', 
        oc_abbr=oc_abbr,
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

    paper = dora.get_paper(project_id, pid)
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


@bp.route('/get_included_papers_and_selections')
@login_required
def get_included_papers_and_selections():
    '''
    Get the included papers and the decisions of selection for outcomes
    '''
    project_id = request.args.get('project_id')
    project_id = request.cookies.get('project_id')

    # get all papers
    papers = dora.get_papers_by_stage(
        project_id, 
        ss_state.SS_STAGE_INCLUDED_SR
    )

    # extend the paper meta with a new attribute
    # outcome_selections
    # and make a pid -> sequence mapping
    pid2seq = {}
    for i, paper in enumerate(papers):
        papers[i].meta['outcome_selections'] = []
        pid2seq[paper.pid] = i
    
    # get all extracts
    # itable, pwma, subg, nma
    extracts = dora.get_extracts_by_project_id(project_id)

    # check each extract
    for extract in extracts:
        for pid in extract.data:
            if pid in pid2seq:
                seq = pid2seq[pid]
                if extract.data[pid]['is_selected']:
                    # this paper is selected for this outcome
                    papers[seq].meta['outcome_selections'].append(
                        extract.abbr
                    )
            else:
                # something wrong, this study should be there
                # but also maybe excluded
                # so, just ignore
                pass
    
    json_papers = [ p.as_very_simple_dict() for p in papers ]
    json_extracts = [ extr.as_dict() for extr in extracts ]
    # json_extracts = [ extr.as_simple_dict() for extr in extracts ]

    ret = {
        'success': True,
        'msg': '',
        'papers': json_papers,
        'extracts': json_extracts
    }
    return jsonify(ret)


@bp.route('/update_paper_selections', methods=['POST'])
@login_required
def update_paper_selections():
    project_id = request.form.get('project_id')
    abbrs = request.form.getlist('abbrs[]')
    pid = request.form.get('pid')

    # update the extract with given info
    paper, outcome_selections = dora.update_paper_selections(
        project_id, pid, abbrs
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
    abbr = request.args.get('abbr')
    
    # get the exisiting extracts
    extract = dora.get_extract_by_project_id_and_abbr(project_id, abbr)

    if extract is None:
        # this is a new extract
        ret = {
            'success': False,
            'msg': 'not exist extract %s' % abbr
        }
        return jsonify(ret)

    # get papers
    stage = ss_state.SS_STAGE_INCLUDED_SR
    papers = dora.get_papers_by_stage(project_id, stage)
    
    # update the extract with papers
    extract.update_data_by_papers(papers)

    # make the return object
    ret = {
        'success': True,
        'msg': '',
        'extract': extract.as_dict(),
        'papers': [ p.as_very_simple_dict() for p in papers ]
    }
    return jsonify(ret)


@bp.route('/update_extract', methods=['POST'])
@login_required
def update_extract():
    '''
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
    abbr = request.form.get('abbr')
    
    # the meta of the extract settings
    data = json.loads(request.form.get('data'))
    
    # update the extract with given info
    extract = dora.update_extract_incr_data(
        project_id, oc_type, abbr, data
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


@bp.route('/get_extract')
@login_required
def get_extract():
    '''
    Get one extract by the project_id and the abbr
    '''
    project_id = request.args.get('project_id')
    abbr = request.args.get('abbr')
    
    # get the exisiting extracts
    extract = dora.get_extract_by_project_id_and_abbr(project_id, abbr)

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
    with_data = request.args.get('with_data')

    if with_data == 'yes':
        with_data = True
    else:
        with_data = False
    
    # get the exisiting extracts
    extracts = dora.get_extracts_by_project_id(project_id)

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
    itable = import_itable_from_xls(prj)

    # build the return obj
    ret = {
        'success': True,
        'extract': itable.as_dict()
    }
    return jsonify(ret)


@bp.route('/import_softable_pma')
@login_required
def import_softable_pma():
    '''
    Create the meta for itable
    '''
    prj = request.args.get('prj')
    extracts = import_softable_pma_from_xls(prj)

    ret = {
        'success': True,
        'extracts': [ ext.as_dict() for ext in extracts ]
    }

    return jsonify(ret)


###############################################################################
# Utils for the itable import
###############################################################################

def import_itable_from_xls(keystr):
    '''
    Import itable all data from xls file

    Including:

    1. meta data for attributes
    2. data of extraction
    3. filters
    '''
    project = dora.get_project_by_keystr(keystr)

    # if project is None:
    #     project_id = request.cookies.get('project_id')
    #     project = dora.get_project(project_id)

    if project is None:
        return jsonify({
            'success': False,
            'msg': 'NO SUCH PROJECT %s' % keystr
        })
    
    project_id = project.project_id
    oc_type = 'itable'
    abbr = 'itable'

    # get the exisiting extracts
    extract = dora.get_extract_by_project_id_and_abbr(
        project.project_id, abbr
    )

    # if not exist, create a new one which is empty
    if extract is None:
        extract = dora.create_extract(
            project_id, oc_type, abbr, 
            settings.OC_TYPE_TPL['itable']['default'], 
            {}
        )

    # get the itable data
    cad, cate_attrs, i2a, data = get_itable_from_itable_data_xls(project.keystr)

    # update the meta
    meta = extract.meta
    meta['cate_attrs'] = cate_attrs

    # get the filters
    filters = get_itable_filters_from_xls(project.keystr)
    meta['filters'] = filters

    # update the extract
    itable = dora.update_extract_meta_and_data(
        project_id, oc_type, abbr, meta, data
    )

    return itable


def get_itable_from_itable_data_xls(keystr):
    '''
    Get the itable extract from ITABLE_ATTR_DATA.xlsx
    '''

    # get the ca list first
    ca_dict, ca_list, i2a = get_cate_attr_subs_from_itable_data_xls(keystr)

    import pandas as pd

    fn = 'ITABLE_ATTR_DATA.xlsx'
    full_fn = os.path.join(
        current_app.instance_path, 
        settings.PATH_PUBDATA, 
        keystr, 
        fn
    )
    if not os.path.exists(full_fn):
        # try the xls file
        full_fn = full_fn[:-1]

    # read the first sheet, but skip the first two rows
    xls = pd.ExcelFile(full_fn)
    first_sheet_name = xls.sheet_names[0]
    df = xls.parse(first_sheet_name, skiprows=1)

    cols = df.columns
    n_cols = len(df.columns)

    # a pmid based dictionary
    data = {}

    # begin loop 
    for _, row in df.iterrows():
        # find the pmid first
        if 'PMID' in row:
            pmid = row['PMID']
        else:
            pmid = row['PubMed ID']

        # must make sure the pmid is a string
        pmid = '%s' % pmid
        # the pmid may contain blank
        pmid = pmid.strip()

        # check if this pmid exists
        is_main = False
        if pmid not in data:
            # ok, this is a new study
            # by default not selected and not checked
            # 
            # `main` is for the main records
            # `other` is for other arms, by default, other is empty
            data[pmid] = {
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
            # which means this row is an multi arm
            # add a new object in other
            data[pmid]['n_arms'] += 1
            data[pmid]['attrs']['other'].append({})

        # check each column
        for idx in range(n_cols):
            col = cols[idx]

            # skip the pmid column
            # since we already use this column as the key
            if col.upper() == 'PMID': continue

            # get the value in this column
            val = row[col]

            # try to clear the blanks
            try: val = val.strip()
            except: pass
            
            # for NaN value
            if pd.isna(val): val = None

            abbr = i2a[idx]

            if is_main:
                data[pmid]['attrs']['main'][abbr] = val
            else:
                # check if this value is same in the main track
                if val == data[pmid]['attrs']['main'][abbr]: 
                    # for the same value, also set ...
                    data[pmid]['attrs']['other'][-1][abbr] = val
                else:
                    # just save the different values
                    data[pmid]['attrs']['other'][-1][abbr] = val

    return ca_dict, ca_list, i2a, data


def get_cate_attr_subs_from_itable_data_xls(keystr):
    '''
    Get the cate, attr, and subs from
    '''
    import pandas as pd

    fn = 'ITABLE_ATTR_DATA.xlsx'
    full_fn = os.path.join(
        current_app.instance_path, 
        settings.PATH_PUBDATA, 
        keystr, 
        fn
    )

    if not os.path.exists(full_fn):
        # try the xls file
        full_fn = full_fn[:-1]

    # read the first sheet
    xls = pd.ExcelFile(full_fn)
    first_sheet_name = xls.sheet_names[0]
    df = xls.parse(first_sheet_name, header=None, nrows=2)

    # df = pd.read_excel(full_fn)

    # convert to other shape
    dft = df.T
    df_attrs = dft.rename(columns={0: 'cate', 1: 'attr'})

    # not conver to tree format
    cate_attr_dict = OrderedDict()
    idx2abbr = {}

    for idx, row in df_attrs.iterrows():
        vtype = 'text'
        print(row)
        # found cate!
        cate = row['cate'].strip()
        
        # put this cate if not exists
        if cate not in cate_attr_dict:
            cate_attr_dict[cate] = {
                'abbr': _gen_abbr_12(),
                'name': cate,
                'attrs': {}
            }

        attr = row['attr'].strip()
        # split the name into different parts
        attr_subs = attr.split('|')
        if len(attr_subs) > 1:
            attr = attr_subs[0].strip()
            sub = attr_subs[1].strip()
        else:
            attr = attr
            sub = None

        # put this attr if not exists
        if attr not in cate_attr_dict[cate]['attrs']:
            cate_attr_dict[cate]['attrs'][attr] = {
                'abbr': _gen_abbr_12(),
                'name': attr,
                'subs': None
            }
        
        # put this sub
        if sub is not None:
            if cate_attr_dict[cate]['attrs'][attr]['subs'] is None:
                cate_attr_dict[cate]['attrs'][attr]['subs'] = [{
                    'abbr': _gen_abbr_12(),
                    'name': sub
                }]
            else:
                cate_attr_dict[cate]['attrs'][attr]['subs'].append({
                    'abbr': _gen_abbr_12(),
                    'name': sub
                })
            # point the idx to the last sub in current attr
            idx2abbr[idx] = cate_attr_dict[cate]['attrs'][attr]['subs'][-1]['abbr']
        else:
            # point the idx to the attr
            idx2abbr[idx] = cate_attr_dict[cate]['attrs'][attr]['abbr']
    
    # convert the dict to list
    cate_attr_list = []
    for _i in cate_attr_dict:
        cate = cate_attr_dict[_i]
        # put this cate
        _cate = {
            'abbr': cate['abbr'],
            'name': cate['name'],
            'attrs': []
        }

        for _j in cate['attrs']:
            attr = cate['attrs'][_j]
            # put this attr
            _attr = {
                'abbr': attr['abbr'],
                'name': attr['name'],
                'subs': attr['subs']
            }
            _cate['attrs'].append(_attr)

        cate_attr_list.append(_cate)

    return cate_attr_dict, cate_attr_list, idx2abbr


def get_itable_filters_from_xls(keystr):
    '''
    Get the filters from ITABLE_FILTER.xlsx
    '''
    import pandas as pd

    fn = 'ITABLE_FILTERS.xlsx'
    full_fn = os.path.join(
        current_app.instance_path, 
        settings.PATH_PUBDATA, 
        keystr, fn
    )
    if not os.path.exists(full_fn):
        # try the xls file
        full_fn = full_fn[:-1]

    # load the data file
    xls = pd.ExcelFile(full_fn)
    # load the Filters tab
    sheet_name = 'Filters'
    dft = xls.parse(sheet_name)

    # build Filters data
    ft_list = []
    for col in dft.columns[1:]:
        display_name = col
        tmp = dft[col].tolist()
        # the first line of dft is the column name / attribute name
        ft_attr = tmp[0]
        # the second line of dft is the filter type: radio or select
        ft_type = tmp[1].strip().lower()
        # get those rows not NaN, which means containing option
        ft_opts = dft[col][~dft[col].isna()].tolist()[3:]
        # get the default label
        ft_def_opt_label = tmp[2].strip()

        # set the default option
        ft_item = {
            'display_name': display_name,
            'type': ft_type,
            'attr': ft_attr,
            'value': 0,
            'values': [{
                "display_name": ft_def_opt_label,
                "value": 0,
                "sql_cond": "{$col} is not NULL",
                "default": True
            }]
        }
        # build ae_name dict
        for i, ft_opt in enumerate(ft_opts):
            ft_opt = str(ft_opt)
            # remove the white space
            ft_opt = ft_opt.strip()
            ft_item['values'].append({
                "display_name": ft_opt,
                "value": i+1,
                "sql_cond": "{$col} like '%%%s%%'" % ft_opt,
                "default": False
            })

        ft_list.append(ft_item)
            
        print('* parsed ft_attr %s with %s options' % (ft_attr, len(ft_opts)))
    print('* created ft_list %s filters' % (len(ft_list)))

    return ft_list


###############################################################################
# Utils for the softable import
###############################################################################


def import_softable_pma_from_xls(keystr, fn, group='primary'):
    '''
    Import the softable data from XLS
    '''
    if keystr == 'IO':
        return import_softable_pma_from_xls_for_IO(fn, group=group)

    raise Exception('Not implemented')


def import_softable_nma_from_xls(keystr):
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
        ae_meta['abbr'] = util.mk_oc_abbr()

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


def _gen_abbr_12():
    '''
    Generate an abbr 12-digits
    '''
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(12))
