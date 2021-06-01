#%% load packages and env
import os
import json
import pathlib
import shutil
import argparse

import logging
logger = logging.getLogger("snapshoter")
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.WARNING, format='%(asctime)s [%(name)s] [%(levelname)s] %(message)s')

# app settings
from lnma import db, create_app
from lnma.models import *

# app for using LNMA functions and tables
app = create_app()
db.init_app(app)
app.app_context().push()


def kacha(keystr, output_path):
    '''
    Take a snapshot
    '''
    # first of all, remove the old kacha?
    shutil.rmtree(
        os.path.join(
            output_path, keystr
        )
    )
    
    if keystr == 'IO':
        kacha_IO(output_path)
    
    else:
        pass

    return 1


def kacha_IO(output_path):
    '''
    Take a snapshot for project IO
    '''
    keystr = 'IO'

    # first, make the folders
    make_folders(keystr, output_path)

    # second, copy static files
    copy_static_files(keystr, output_path, [
        'lib/d3'
    ])
    
    # third, copy the graph data
    copy_graphdata_files(keystr, output_path, [
        'img',
        'CONCEPT_IMAGE.svg'
    ])

    rules = [
        ['/pub/IO.html', 'index.html'],
        # for the PRISMA
        ['/pub/prisma_IO.html', 'pub/prisma_IO.html'],
        ['/pub/graphdata/%s/PRISMA.json?src=db' % (keystr), 'pub/graphdata/%s/PRISMA.json' % (keystr)],

        # for the itable
        ['/pub/itable.html?prj=%s&src=db' % (keystr), 'pub/itable.html'],
        ['/pub/graphdata/%s/ITABLE.json?src=db' % (keystr), 'pub/graphdata/%s/ITABLE.json' % (keystr)],

        # for the pwma plots
        ['/pub/graph_pma_IO.html?prj=%s' % (keystr), 'pub/graph_pma_IO.html'],
        ['/pub/graphdata/%s/GRAPH_PMA.json?src=db' % (keystr), 'pub/graphdata/%s/GRAPH_PMA.json' % (keystr)],

        # for the pwma softable
        ['/pub/softable_pma_IO.html?prj=%s' % (keystr), 'pub/softable_pma_IO.html'],
        ['/pub/graphdata/%s/SOFTABLE_PMA.json?src=db' % (keystr), 'pub/graphdata/%s/SOFTABLE_PMA.json' % (keystr)],

        # for the latest update
        ['/pub/graphdata/%s/LATEST.json' % (keystr), 'pub/graphdata/%s/LATEST.json' % (keystr)]

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
                    keystr,
                    rule[1]
                )
                make_page(client, rule[0], full_fn)

    print('* done building static pages')


def copy_static_files(keystr, output_path, libs=None):
    '''
    Copy the static files
    '''
    # get the current path of this file
    cur_path = pathlib.Path(__file__).parent.absolute()

    # get the source static path
    static_path = os.path.join(
        cur_path, 'lnma', 'static'
    )

    # get the destination path
    _output_path = os.path.join(
        output_path, keystr, 'static'
    )

    # copy these two folders
    folders = ['css', 'img']

    # add some libs
    if libs is not None:
        folders = folders + libs

    for folder in folders:
        shutil.copytree(
            os.path.join(static_path, folder),
            os.path.join(_output_path, folder)
        )
        print('* copied static %s' % folder)

    return 1


def copy_graphdata_files(keystr, output_path, paths):
    '''
    Copy the graphdata files
    '''
    # get the current path of this file
    cur_path = pathlib.Path(__file__).parent.absolute()

    # get the source graphdata path
    graphdata_path = os.path.join(
        cur_path, 'instance', 'pubdata', keystr
    )
    print('* got graphdata_path: %s' % graphdata_path)

    # get the destination path
    _output_path = os.path.join(
        output_path, keystr, 'pub', 'graphdata', keystr
    )
    print('* got _output_path: %s' % _output_path)

    for path in paths:
        src_path = os.path.join(graphdata_path, path)
        dst_path = os.path.join(_output_path, path)

        if os.path.isdir(src_path):
            shutil.copytree(src_path, dst_path)

        elif os.path.isfile(src_path):
            shutil.copyfile(src_path, dst_path)

        else:
            raise Exception('Error when copying %s' % src_path)

        print('* copied graphdata %s' % path)

    return 1


def make_folders(keystr, output_path):
    '''
    Make folders for the static in the given output_path
    '''
    # first, the pub
    folders = [
        '',
        'pub',
        'pub/graphdata',
        'pub/graphdata/' + keystr
    ]

    for folder in folders:
        full_path = os.path.join(
            output_path, keystr, folder
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
    parser = argparse.ArgumentParser('LNMA Snapshoter')
    parser.add_argument("--keystr", type=str,
        help="The keystr for the project. Use `all` for all projects"
    )
    parser.add_argument("--output", type=str,
        help="The output path for the static website"
    )

    args = parser.parse_args()

    if args.keystr == 'all':
        pass

    else:
        kacha(args.keystr, args.output)

    print('* done snapshot!')