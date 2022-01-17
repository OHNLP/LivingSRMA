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


def kacha(keystr, cq_abbr, output_path):
    '''
    Take a snapshot for general project
    '''
    # keystr = 'IO'
    # cq_abbr = 'default'

    # first, make the folders
    make_folders(keystr, cq_abbr, output_path)

    pcq_output_path = os.path.join(
        output_path, keystr, cq_abbr
    )

    # second, copy static files
    copy_static_files(keystr, pcq_output_path, [
        'lib/d3'
    ])
    
    # third, copy the graph data
    copy_graphdata_files(keystr, pcq_output_path, [
        'img',
        'CONCEPT_IMAGE.svg'
    ])

    rules = [
        # the basic home page
        ['HOMEPAGE [%s.%s]' % (keystr, cq_abbr), '/pub/%s/%s/index.html' % (keystr, cq_abbr), 'index.html'],

        # for the PRISMA
        ['PRISMA PAGE', '/pub/prisma.html', 'pub/prisma.html'],
        ['PRISMA.json', '/pub/graphdata/%s/PRISMA.json?src=db&cq=%s' % (keystr, cq_abbr), 'pub/graphdata/%s/PRISMA.json' % (keystr)],

        # for the itable
        ['ITABLE PAGE', '/pub/itable.html?prj=%s&src=db' % (keystr), 'pub/itable.html'],
        ['ITABLE.json', '/pub/graphdata/%s/ITABLE.json?src=db&cq=%s' % (keystr, cq_abbr), 'pub/graphdata/%s/ITABLE.json' % (keystr)],

        # for the pwma plots
        ['PWMA PLOTS PAGE', '/pub/graph_pma.html?prj=%s&cq=%s' % (keystr, cq_abbr), 'pub/graph_pma.html'],
        ['PWMA PLOTS DATA', '/pub/graphdata/%s/GRAPH_PMA.json?src=db&cq=%s' % (keystr, cq_abbr), 'pub/graphdata/%s/GRAPH_PMA.json' % (keystr)],

        # for the pwma softable
        ['PWMA SOFTABLE PAGE', '/pub/softable_pma.html?prj=%s&cq=%s' % (keystr, cq_abbr), 'pub/softable_pma.html'],
        ['PWMA SOFTABLE DATA', '/pub/graphdata/%s/SOFTABLE_PMA.json?src=db&cq=%s' % (keystr, cq_abbr), 'pub/graphdata/%s/SOFTABLE_PMA.json' % (keystr)],

        # for the nma plots
        ['NMA PLOTS PAGE', '/pub/graph_nma.html?prj=%s&cq=%s' % (keystr, cq_abbr), 'pub/graph_nma.html'],
        ['NMA PLOTS DATA', '/pub/graphdata/%s/GRAPH_NMA.json?src=db&cq=%s' % (keystr, cq_abbr), 'pub/graphdata/%s/GRAPH_NMA.json' % (keystr)],

        # for the nma softable
        ['NMA SOFTABLE PAGE', '/pub/softable_nma.html?prj=%s&cq=%s' % (keystr, cq_abbr), 'pub/softable_pma.html'],
        ['NMA SOFTABLE DATA', '/pub/graphdata/%s/SOFTABLE_NMA.json?src=db&cq=%s' % (keystr, cq_abbr), 'pub/graphdata/%s/SOFTABLE_NMA.json' % (keystr)],

        # for the latest update
        ['LATEST DATE', '/pub/graphdata/%s/LATEST.json' % (keystr), 'pub/graphdata/%s/LATEST.json' % (keystr)]

    ]

    # the root path for output
    # pathlib.Path(__file__).parent.absolute()

    # download each page / data
    with app.test_client() as client:
        with app.app_context():
            for rule in rules:
                print('* MAKING - %s' % rule[0])
                # create the file name for this rule
                full_fn = os.path.join(
                    pcq_output_path,
                    rule[2]
                )

                # make page or download the data for this rule
                make_page(client, rule[1], full_fn)

    print('* done building static pages')