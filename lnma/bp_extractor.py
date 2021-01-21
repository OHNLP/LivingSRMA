import os
import json
import random
import string
from collections import OrderedDict

from flask import request
from flask import flash
from flask import render_template
from flask import Blueprint
from flask import current_app
from flask import jsonify

from flask_login import login_required
from flask_login import current_user

from lnma import dora
from lnma import ss_state
from lnma import settings

bp = Blueprint("extractor", __name__, url_prefix="/extractor")

@bp.route('/v1')
@login_required
def v1():
    return render_template('extractor/v1.html')


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

    # merge the return obj
    # make a ref in the extract for frontend display
    # make sure every selected paper is listed in extract.data
    pids = set([])
    for paper in papers:
        pid = paper.pid
        # record this pid for next step
        pids.add(pid)

        # check if this pid exists in extract
        if pid in extract.data:
            # nothing to do if has added
            continue

        # if not exist, add this paper
        extract.data[pid] = {
            'selected': False,
            'has_checked': False,
            'attrs': {}
        }
        # put the attrs
        if abbr == 'itable':
            extract.data[pid]['attrs'] = {
                'main': {},
                'other': []
            }
            # itable has a different rule
            for cate in extract.meta['cate_attrs']:
                for attr in cate['attrs']:
                    attr_abbr = attr['abbr']
                    if attr['subs'] is None:
                        extract.data[pid]['attrs']['main'][attr_abbr] = ''
                    else:
                        # have multiple subs
                        for sub in attr['subs']:
                            sub_abbr = sub['abbr']
                            extract.data[pid]['attrs']['main'][sub_abbr] = ''
        else:
            for attr in extract.meta['attrs']:
                extract.data[pid]['attrs'][attr] = ''

    # reverse search, unselect those are not in papers
    for pid in extract.data:
        if pid in pids:
            # which means this pid is in the SR stage
            continue

        # if not, just unselect this paper
        # don't delete
        extract.data[pid]['selected'] = False
        
    ret = {
        'success': True,
        'msg': '',
        'extract': extract.as_dict(),
        'papers': [ p.as_simple_dict() for p in papers ]
    }
    return jsonify(ret)


@bp.route('/update_extract_meta', methods=['POST'])
@login_required
def update_extract_meta():
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


@bp.route('/update_extract', methods=['POST'])
@login_required
def update_extract():
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
    
    # get the exisiting extracts
    extracts = dora.get_extracts_by_project_id(project_id)

    # build the return obj
    ret = {
        'success': True,
        'msg': '',
        'extracts': [ extr.as_dict() for extr in extracts ]
    }
    return jsonify(ret)


@bp.route('/test')
@login_required
def test():
    '''
    Test function
    '''
    project_id = request.args.get('project_id')
    
    # get the exisiting extracts
    cad, cal, i2a, data = get_itable_from_itable_data_xls('IOTOX')

    # build the return obj
    ret = {
        'success': True,
        'meta': cal,
        'data': data
    }
    return jsonify(ret)


@bp.route('/import_itable_meta_and_data_from_xls')
@login_required
def import_itable_meta_and_data_from_xls():
    '''
    Create the meta for itable
    '''
    # project_id = request.args.get('project_id')
    project_id = request.cookies.get('project_id')
    project = dora.get_project(project_id)

    oc_type = 'itable'
    abbr = 'itable'

    # get the exisiting extracts
    extract = dora.get_extract_by_project_id_and_abbr(
        project.project_id, abbr
    )
    cad, cate_attrs, i2a, data = get_itable_from_itable_data_xls(project.keystr)

    # update the meta
    meta = extract.meta
    meta['cate_attrs'] = cate_attrs

    # update the extract
    extract = dora.update_extract_meta_and_data(project_id, oc_type, abbr, meta, data)

    # build the return obj
    ret = {
        'success': True,
        'extract': extract.as_dict()
    }
    return jsonify(ret)



###############################################################################
# Utils for the extraction
###############################################################################
def get_itable_from_itable_data_xls(keystr):
    '''
    Get the itable extract from ITABLE_ATTR_DATA.xlsx
    '''

    # get the ca list first
    ca_dict, ca_list, i2a = get_cate_attr_subs_from_itable_data_xls(keystr)

    import pandas as pd

    fn = 'ITABLE_ATTR_DATA.xlsx'
    full_fn = os.path.join(current_app.instance_path, settings.PATH_PUBDATA, keystr, fn)

    # read the first sheet, but skip the first two rows
    xls = pd.ExcelFile(full_fn)
    first_sheet_name = xls.sheet_names[0]
    df = xls.parse(first_sheet_name, skiprows=1)

    cols = df.columns
    n_cols = len(df.columns)

    data = {}
    # begin loop 
    for _, row in df.iterrows():
        # find the pmid first
        pmid = row['PMID']

        # check if this pmid exists
        is_main = False
        if pmid not in data:
            # ok, this is a new study
            # by default not selected and not checked
            # 
            # `main` is for the main records
            # `other` is for other arms, by default, other is empty
            data[pmid] = {
                'selected': False,
                'has_checked': False,
                'attrs': {
                    'main': {},
                    'other': []
                }
            }
            is_main = True
        else:
            # which means this row is an multi arm
            # add a new object in other
            data[pmid]['other'].append({})

        # check each column
        for idx in range(n_cols):
            col = cols[idx]

            # skip the pmid column
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
                    pass
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
    full_fn = os.path.join(current_app.instance_path, settings.PATH_PUBDATA, keystr, fn)

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


def _gen_abbr_12():
    '''
    Generate an abbr 12-digits
    '''
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(12))
