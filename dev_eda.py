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
