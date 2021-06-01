#%% load packages and env
import os
import json
import pathlib
import argparse

import logging
logger = logging.getLogger("snapshoter")
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.WARNING, format='%(asctime)s [%(name)s] [%(levelname)s] %(message)s')

from pprint import pprint

# app settings
from lnma import db, create_app
from lnma.models import *
from lnma import dora

# app for using LNMA functions and tables
app = create_app()
db.init_app(app)
app.app_context().push()


def kacha(keystr):
    '''
    Take a snapshot
    '''
    return kacha_IO()


def kacha_IO(output_path):
    '''
    Take a snapshot for project IO
    '''
    rules = [
        ['/pub/IO.html', '/index.html'],
        # for the PRISMA
        ['/pub/prisma_IO.html', '/pub/prisma_IO.html'],
        # for the itable
        ['/pub/itable.html?prj=IO&src=db', '/pub/itable.html'],
        ['/pub/graphdata/IO/ITABLE.json?src=db', '/pub/graphdata/IO/ITABLE.json'],
        # for the pwma plots
        ['/pub/graph_pma_IO.html?prj=IO', '/pub/graph_pma_IO.html'],
        ['/pub/graphdata/IO/GRAPH_PMA.json?src=db', '/pub/graphdata/IO/GRAPH_PMA.json'],
        # for the 
        ['/pub/softable_pma_IO.html?prj=IO', '/pub/softable_pma_IO.html'],
        ['/pub/graphdata/IO/SOFTABLE_PMA.json?src=db', '/pub/graphdata/IO/SOFTABLE_PMA.json'],
    ]

    # the root path for output
    # pathlib.Path(__file__).parent.absolute()

    # download each page / data
    with app.test_client() as client:
        with app.app_context():
            for rule in rules:
                # 
                full_fn = os.path.join(
                    output_path,
                    rule[1]
                )
                make_page(client, rule[0], full_fn)

    print('* done building static pages')


def make_folders(output_path):
    '''
    Make folders for the static in the given output_path
    '''
    # first, the pub
    folders = [
        'pub',
        'pub/graphdata',
        'static',
        'static/img',
        'static/css',
    ]

    for folder in folders:
        full_path = os.path.join(
            output_path, folder
        )
        if os.path.exists(full_path):
            print('* existed folder %s' % full_path)

        else:
            os.makedirs(full_path, exist_ok=True)
            print('* created folder %s' % full_path)

    return 1

    
def make_page(client, url, full_fn, param=None):
    '''
    Make static page from url
    '''
    rv = client.get(url)

    with open(full_fn, 'w') as f:
        f.write(rv.data.decode('utf8'))
    
    print('* made static page %s -> %s' % (
        url, full_fn
    ))

    return 1


if __name__ == "__main__":
    print("* Now you have the app and db to access the env")