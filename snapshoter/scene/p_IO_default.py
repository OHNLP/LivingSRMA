import os

from . import make_page
from . import make_folders
from . import copy_static_files
from . import copy_graphdata_files

# app settings
from lnma import db, create_app
from lnma.models import *

# app for using LNMA functions and tables
app = create_app()
db.init_app(app)
app.app_context().push()


def kacha(output_path):
    '''
    Take a snapshot for project IO
    '''
    keystr = 'IO'
    cq_abbr = 'default'

    # first, make the folders
    make_folders(keystr, cq_abbr, output_path)

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
        # the basic page
        ['/pub/IO/default/index.html', 'index.html'],

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