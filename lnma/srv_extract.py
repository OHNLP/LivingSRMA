import time
from unicodedata import category

import numpy as np
from numpy.lib.function_base import extract
import pandas as pd
from tqdm import tqdm 

from sqlalchemy import and_, or_, not_
from sqlalchemy.orm.attributes import flag_modified

from lnma import settings
from lnma import util
from lnma import dora
from lnma import ss_state
from lnma.models import *

from lnma import db


def get_itable_by_keystr_and_cq_abbr(keystr, cq_abbr):
    '''
    Get the specific CQ itable in a project
    '''
    project = dora.get_project_by_keystr(keystr)

    if project is None:
        return None

    extract = Extract.query.filter(and_(
        Extract.project_id == project.project_id,
        Extract.meta['cq_abbr'] == cq_abbr,
        Extract.oc_type == 'itable'
    )).first()

    return extract


def get_itable_by_project_id_and_cq_abbr(project_id, cq_abbr):
    '''
    Get the specific CQ itable in a project
    '''
    extract = Extract.query.filter(and_(
        Extract.project_id == project_id,
        Extract.meta['cq_abbr'] == cq_abbr,
        Extract.oc_type == 'itable'
    )).first()

    return extract


def get_extracts_by_cate_and_name(keystr, cq_abbr, oc_type, group, category, full_name):
    '''
    Get extract by cate and name for detect duplicate purpose
    '''
    # first, get this paper
    project = dora.get_project_by_keystr(keystr)

    # second, check this
    sql = """
    select extract_id
    from extracts
    where project_id = '{project_id}'
        and oc_type = 'nma'
        and JSON_EXTRACT(meta, '$.cq_abbr') = '{cq_abbr}'
        and JSON_EXTRACT(meta, '$.group') = '{group}'
        and JSON_EXTRACT(meta, '$.category') = '{category}'
        and JSON_EXTRACT(meta, '$.full_name') = '{full_name}'
    """.format(
        project_id=project.project_id,
        cq_abbr=cq_abbr,
        oc_type=oc_type,
        group=group,
        category=category,
        full_name=full_name
    )
    # print('* execute sql: %s' % sql)
    rs = db.session.execute(sql).fetchall()

    exts = []
    for r in rs:
        exts.append(
            dora.get_extract(r['extract_id'])
        )

    return exts
    

def create_extract(keystr, cq_abbr, oc_type, group, category, full_name, other_meta={}):
    '''
    Create an extract with some infos
    '''

    # first, get this project
    project = dora.get_project_by_keystr(keystr)

    oc_abbr = util.mk_oc_abbr()
    default_meta = copy.deepcopy(settings.OC_TYPE_TPL[oc_type]['default'])

    # set some value to meta
    default_meta['abbr'] = oc_abbr
    default_meta['cq_abbr'] = cq_abbr
    default_meta['oc_type'] = oc_type
    default_meta['group'] = group
    default_meta['category'] = category
    default_meta['full_name'] = full_name

    # copy other values
    for key in other_meta:
        default_meta[key] = other_meta[key]

    # need to fix the cate
    default_meta['cate_attrs'] = copy.deepcopy(
        settings.INPUT_FORMAT_TPL[oc_type][default_meta['input_format']]
    )

    ext = dora.create_extract(
        project_id=project.project_id,
        oc_type=oc_type,
        abbr=oc_abbr,
        meta=default_meta,
        data={}
    )

    return ext


def import_extracts_from_xls(full_path, keystr, cq_abbr, oc_type):
    '''
    Import extracts to database
    '''
    # load data
    xls = pd.ExcelFile(full_path)

    # build AE Category data
    first_sheet_name = xls.sheet_names[0]
    dft = xls.parse(first_sheet_name)
    dft = dft[~dft['full_name'].isna()]
    
    print(dft.head())

    # columns we could use 
    for idx, row in dft.iterrows():
        tab_name = row['name'].strip()
        data_type = row['data_type'].strip()
        print('*'*60)
        
        meta = dict(
            cq_abbr = cq_abbr,
            oc_type = oc_type,
            group = row['analysis_title'].strip(),
            category = row['category'].strip(),
            full_name = row['full_name'].strip(),
            which_is_better = row['which_is_better'].strip(),
            fixed_or_random = row['fixed_or_random'].strip(),
            analysis_method = row['method'].strip(),
            measure_of_effect = row['measure'].strip(),
            included_in_plots = row['included_in_plots'].strip(),
            included_in_sof = row['included_in_sof'].strip(),
            included_in_em = row['included_in_em'].strip(),
            input_format = {'pre':'NMA_PRE_SMLU', 'raw':'NMA_RAW_ET'}[data_type]
        )

        # check exist
        exts = get_extracts_by_cate_and_name(
            keystr, 
            cq_abbr,
            oc_type,
            meta['group'],
            meta['category'],
            meta['full_name']
        )

        if len(exts) != 0:
            # remove these
            for ext in exts:
                dora.delete_extract(
                    ext.project_id,
                    ext.oc_type,
                    ext.abbr
                )
                print('* removed ext %s' % ext.abbr)
        
        ext = create_extract(
            keystr, 
            cq_abbr,
            oc_type,
            meta['group'],
            meta['category'],
            meta['full_name'],
            meta
        )
        print('* created ext %s' % ext.abbr)

        # print('* tab: %s' % (tab_name))

    return dft

###########################################################
# Utils for management
###########################################################

def reset_extracts_includes(keystr, cq_abbr, include_in, yes_or_no):
    '''
    Reset all extracts' include in 
    '''
    extracts = dora.get_extracts_by_keystr_and_cq(keystr, cq_abbr)

    for ext in tqdm(extracts):
        if include_in == 'plots':
            ext.meta['included_in_plots'] = yes_or_no            
            flag_modified(ext, 'meta')
            db.session.add(ext)
            db.session.commit()

        elif include_in == 'sof':
            ext.meta['included_in_sof'] = yes_or_no
            flag_modified(ext, 'meta')
            db.session.add(ext)
            db.session.commit()

        else:
            pass

    print('* done reset')