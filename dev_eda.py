#%% import LNMA packages
import os
import json
import random

import pandas as pd
from sqlalchemy import and_, or_, not_
from tqdm import tqdm
from pprint import pprint

from lnma import db, create_app, srv_extract, srv_paper, srv_project
from lnma.models import *
from lnma import dora
from lnma import util
from lnma import ss_state
from lnma.analyzer import rpy2_nma_analyzer

# app for using LNMA functions and tables
app = create_app()
db.init_app(app)
app.app_context().push()

print('* inited basic env for LNMA EDA')

#%% load all papers
papers = dora.get_papers_by_keystr('IO')
print('* got all %s papers for IO' % (len(papers)))

#%% load the itable
project = dora.get_project_by_keystr('IO')

# get all extracts of the default
cq_abbr = 'default'
extracts = dora.get_extracts_by_project_id_and_cq(
    project.project_id,
    cq_abbr
)
print('* got %s extracts for [%s]' % (
    len(extracts),
    cq_abbr
))

# there could be multiple itable defined in a project based on CQ
# so, this time we just check the `default` CQ
itable = dora.get_itable_by_project_id_and_cq(
    project.project_id, 
    cq_abbr
)
print('* got the project and itable [%s]' % (
    itable.abbr
))

#%% check if there is any ds_ids in meta
cnt_y = 0
cnt_n = 0
for p in papers:
    if 'ds_id' in p.meta:
        cnt_y += 1
    else:
        cnt_n += 1

print('* ds_id IS  in %s/%s papers' % (cnt_y, len(papers)))
print('* ds_id NOT in %s/%s papers' % (cnt_n, len(papers)))

#%% get all duplicates
all_dups = srv_paper.get_duplicated_papers('IO')
print('* done searching')


#%% find how many records have been added to itable
n_itable = 0
for pid in itable.data:
    ext = itable.data[pid]

    if ext['is_checked']:
        n_itable += 1
print('* found %s papers are selected for the itable' % ( n_itable ))

#%% read the xlsx
df = pd.read_excel(
    '/tmp/ROB2_IRPG_beta_v8.xlsm',
    sheet_name='Results',
    header=1,
    index_col=None
)
print('* loaded %s rows' % (len(df)))

#%% define the mapping
col2attr = [
    # domain 1
    ['1.1', 'COE_RCT_ROB_D1_Q1'],
    ['1.2', 'COE_RCT_ROB_D1_Q2'],
    ['1.3', 'COE_RCT_ROB_D1_Q3'],
    ['Note for 1.1&1.2', 'COE_RCT_ROB_D1_C1'],
    ['Note for 1.1&1.2', 'COE_RCT_ROB_D1_C2'],
    ['Note for 1.3', 'COE_RCT_ROB_D1_C3'],
    ['1.0 Algorithm result', 'COE_RCT_ROB_D1_AR'],
    ["1.0 Assessor's Judgement", 'COE_RCT_ROB_D1_RJ'],

    # domain 2
    ['2.1', 'COE_RCT_ROB_D2_Q1'],
    ['2.2', 'COE_RCT_ROB_D2_Q2'],
    ['2.3', 'COE_RCT_ROB_D2_Q3'],
    ['2.4', 'COE_RCT_ROB_D2_Q4'],
    ['2.5', 'COE_RCT_ROB_D2_Q5'],
    ['2.6', 'COE_RCT_ROB_D2_Q6'],
    ['2.7', 'COE_RCT_ROB_D2_Q7'],
    ['Note for 2.1&2.2', 'COE_RCT_ROB_D2_C1'],
    ['Note for 2.1&2.2', 'COE_RCT_ROB_D2_C2'],
    ['Note for 2.3', 'COE_RCT_ROB_D2_C3'],
    ['Note for 2.4', 'COE_RCT_ROB_D2_C4'],
    ['Note for 2.5', 'COE_RCT_ROB_D2_C5'],
    ['Note for 2.6', 'COE_RCT_ROB_D2_C6'],
    ['Note for 2.7', 'COE_RCT_ROB_D2_C7'],
    ['2.0 Algorithm result', 'COE_RCT_ROB_D2_AR'],
    ["2.0 Assessor's Judgement", 'COE_RCT_ROB_D2_RJ'],

    # domain 3
    ['3.1', 'COE_RCT_ROB_D3_Q1'],
    ['3.2', 'COE_RCT_ROB_D3_Q2'],
    ['3.3', 'COE_RCT_ROB_D3_Q3'],
    ['3.4', 'COE_RCT_ROB_D3_Q4'],
    ['Note for 3.1', 'COE_RCT_ROB_D3_C1'],
    ['Note for 3.2', 'COE_RCT_ROB_D3_C2'],
    ['Note for 3.3&3.4', 'COE_RCT_ROB_D3_C3'],
    ['Note for 3.3&3.4', 'COE_RCT_ROB_D3_C4'],
    ["3.0 Algorithm result", 'COE_RCT_ROB_D3_AR'],
    ["3.0 Assessor's judgement", 'COE_RCT_ROB_D3_RJ'],

    # domain 4
    ['4.1', 'COE_RCT_ROB_D4_Q1'],
    ['4.2', 'COE_RCT_ROB_D4_Q2'],
    ['4.3', 'COE_RCT_ROB_D4_Q3'],
    ['4.4', 'COE_RCT_ROB_D4_Q4'],
    ['4.5', 'COE_RCT_ROB_D4_Q5'],
    ['Note for 4.1', 'COE_RCT_ROB_D4_C1'],
    ['Note for 4.2', 'COE_RCT_ROB_D4_C2'],
    ['Note for 4.3', 'COE_RCT_ROB_D4_C3'],
    ['Note for 4.4&4.5', 'COE_RCT_ROB_D4_C4'],
    ['Note for 4.4&4.5', 'COE_RCT_ROB_D4_C5'],
    ["4.0 Algorithm result", 'COE_RCT_ROB_D4_AR'],
    ["4.0 Assessor's Judgement", 'COE_RCT_ROB_D4_RJ'],

    # domain 5
    ['5.1', 'COE_RCT_ROB_D5_Q1'],
    ['5.2', 'COE_RCT_ROB_D5_Q2'],
    ['5.3', 'COE_RCT_ROB_D5_Q3'],
    ['Note for 5.1', 'COE_RCT_ROB_D5_C1'],
    ['Note for 5.2', 'COE_RCT_ROB_D5_C2'],
    ['Note for 5.3', 'COE_RCT_ROB_D5_C3'],
    ["5.0 Algorithm result", 'COE_RCT_ROB_D5_AR'],
    ["5.0 Assessor's Judgement", 'COE_RCT_ROB_D5_RJ'],

    # overall
    ["Algorithm's overall Judgement", 'COE_RCT_ROB_OVERALL_AR'],
    ["Assessor's overall Judgement", 'COE_RCT_ROB_OVERALL_RJ'],
]

#%% helpers
def find_papers_by_nct(nct, papers):
    ps = []
    for p in papers:
        if p.meta['rct_id'] == nct:
            ps.append(p)
    return ps

def cnvt_val(val):
    s = '%s' % val

    # fix nan value
    if s == 'nan': s = ''

    # convert labels, other just return itself
    s = {
        'Low': 'L',
        'Some concerns': 'M',
        'High': 'H',
    }.get(s, s)

    return s

print('* defined helper functions')

#%% parse each row and get record
n_nct_papers = 0
n_not_found_paper = 0
n_missing_piece = 0

unique_vals = set([])
for _, row in df.iterrows():
    nct_id = row['Unique ID']

    # ensure no extra space
    nct_id = nct_id.strip()

    if not nct_id.startswith('NCT'): 
        print('* skipping %s' % nct_id)
        continue

    # print('* parsing %s' % nct_id)
    # get the paper
    ps = find_papers_by_nct(nct_id, papers)

    if len(ps) == 0:
        print('* cannot find trial %s' % nct_id)
        continue
    
    # now need to check the paper in itable
    for p in ps:
        n_nct_papers += 1
        
        # first, find this paper in itable
        piece = dora.get_piece_by_project_id_and_abbr_and_pid(
            project.project_id,
            itable.extract_id,
            p.pid
        )

        if piece is None:
            # hmmm, this piece doesn't exist yet???
            piece_data = util.mk_piece_data(
                False, 
                False,
                2,
                itable.meta['cate_attrs']
            )
            piece = dora.create_piece(
                project.project_id,
                itable.extract_id,
                p.pid,
                piece_data
            )
            n_missing_piece += 1

        #########################################################
        # ok, this paper is found in itable, we can update it now
        #########################################################
        # for col_attr in col2attr:
        #     col = col_attr[0]
        #     attr = col_attr[1]

        #     # get the value from XLS
        #     val_raw = row[col]

        #     # convert the value to itable format
        #     val_itb = cnvt_val(val_raw)


print('* got %s paper ids' % (n_nct_papers))
print('* missing %s paper ids' % (n_missing_piece))
print('* unique_vals: %s' % unique_vals)


#%% make a SQL for get paper_selections
sql_get_paper_selection = """
select pid, extract_id
from pieces
where project_id='{project_id}'
  and json_extract(data, "$.is_selected") = TRUE
""".format(project_id='60c0524c-3f41-11eb-b67e-000d3a9afec0')

rs = db.session.execute(
    sql_get_paper_selection
).fetchall()

print('* got %s lines' % (len(rs)))