#%% load packages and env
import os
import json
import random
import requests
import argparse

import logging
logger = logging.getLogger("watcher")
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.WARNING, format='%(asctime)s [%(name)s] [%(levelname)s] %(message)s')

from sqlalchemy import and_, or_, not_
from tqdm import tqdm
from pprint import pprint

# for looping the watcher
from timeloop import Timeloop
from datetime import timedelta

# for checking email updates
from imbox import Imbox

# app settings
from lnma import db, create_app, srv_extract, srv_paper, srv_project
from lnma.models import *
from lnma import dora
from lnma import util
from lnma import ss_state

# app for using LNMA functions and tables
app = create_app()
db.init_app(app)
app.app_context().push()


def test_pred():
    project_id = '119bdd6a-2ae9-11eb-8100-bf78cc92e08e'
    pids = ['32966830']

    for pid in pids:
        pred = dora.update_paper_rct_result(project_id, pid)
        pprint(pred)
    

def test():
    srv_project.delete_all_extracts_by_keystr(
        'RCC',
        'default',
        'nma'
    )
    srv_extract.import_extracts_from_xls(
        '/tmp/mrcc-nma.xlsx',
        'RCC',
        'default',
        'nma',
    )


def test2():
    ret = srv_paper.check_existed_paper_by_file(
        'IO',
        'ovid',
        # '/tmp/IO-0110-149.xml'
        '/tmp/IO-0107-1336.xml'
    )
    print(ret['cnt'])
    # print('is_valid_pmid:', util.is_valid_pmid('12345678'))
    # print('is_valid_pmid:', util.is_valid_pmid('223456783212323212'))


def test3():
    srv_extract.import_extracts_from_xls(
        '/tmp/pma.xlsx',
        'RCC',
        'default',
        'pwma',
    )

def test2():
    ext_ids = srv_extract.get_extracts_by_cate_and_name(
        'RCC',
        'default',
        'nma',
        'default',
        'PFS'
    )
    print(ext_ids)

    ext = srv_extract.create_extract(
        'RCC',
        'default',
        'nma',
        'primary',
        'default',
        'Big Name Here %s' % random.randint(0, 1000),
        other_meta={

        }
    )

    print(ext.as_very_simple_dict())


if __name__ == "__main__":
    print("* Now you have the app and db to access the env")
    test()