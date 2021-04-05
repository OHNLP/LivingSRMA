import os
import json
import random
from re import template
import string
from collections import OrderedDict

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
    return render_template(
        template_base + 'manage_itable.html'
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
    json_extracts = [ extr.as_simple_dict() for extr in extracts ]

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
            'is_selected': False,
            'is_checked': False,
            'n_arms': 2,
            'attrs': {}
        }

        extract.data[pid]['attrs'] = {
            'main': {},
            'other': []
        }
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
        # else:
        #     for attr in extract.meta['attrs']:
        #         extract.data[pid]['attrs']['main'][attr] = ''

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



###############################################################################
# Importers 
###############################################################################

@bp.route('/import_itable_meta_and_data_from_xls')
@login_required
def import_itable_meta_and_data_from_xls():
    '''
    Create the meta for itable
    '''
    prj = request.args.get('prj')
    project = dora.get_project_by_keystr(prj)

    if project is None:
        project_id = request.cookies.get('project_id')
        project = dora.get_project(project_id)

    if project is None:
        return jsonify({
            'success': False,
            'msg': 'NO SUCH PROJECT'
        })
    prj = project.keystr

    project_id = project.project_id
    oc_type = 'itable'
    abbr = 'itable'

    # get the exisiting extracts
    extract = dora.get_extract_by_project_id_and_abbr(
        project.project_id, abbr
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
    extract = dora.update_extract_meta_and_data(project_id, oc_type, abbr, meta, data)

    # build the return obj
    ret = {
        'success': True,
        'extract': extract.as_dict()
    }
    return jsonify(ret)


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
# Speciall importer for IO project due to the 
###############################################################################

@bp.route('/import_IO_aes_from_xls')
@login_required
def import_IO_aes_from_xls():
    '''
    Create the meta for itable
    '''
    import pandas as pd
    prj = 'IO'
    fn = 'ALL_DATA.xlsx'
    full_fn = os.path.join(current_app.instance_path, settings.PATH_PUBDATA, prj, fn)
    # ret = get_ae_pma_data(full_fn, is_getting_sms=False)

    # First, create a row->pmid dictionary
    xls = pd.ExcelFile(full_fn)
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
            'drug_used', 'malignancy']

    # each sheet is an AE/OC
    outcomes = []
    for sheet_name in xls.sheet_names[2:]:
        ae_name = sheet_name

        # create an empty meta
        ae_meta = json.loads(json.dumps(settings.OC_TYPE_TPL['pwma']['default']))
        
        # update the abbr
        ae_meta['abbr'] = util.mk_oc_abbr()

        # update the cate
        ae_meta['category'] = ae_dict[ae_name]

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
            pmid = idx2pmid[idx]
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
    project_id = request.cookies.get('project_id')
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

        extracts.append(extract)

    # return!

    ret = {
        'success': True,
        'n_extracts': len(extracts),
        'extracts': [ ext.as_dict() for ext in extracts ]
    }

    return jsonify(ret)


###############################################################################
# Utils for the extraction
###############################################################################

def get_itable_filters_from_xls(keystr):
    '''
    Get the filters from ITABLE_FILTER.xlsx
    '''
    import pandas as pd

    fn = 'ITABLE_FILTERS.xlsx'
    full_fn = os.path.join(current_app.instance_path, settings.PATH_PUBDATA, keystr, fn)
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
        if 'PMID' in row:
            pmid = row['PMID']
        else:
            pmid = row['PubMed ID']

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
