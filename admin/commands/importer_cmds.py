import sys
sys.path.append('..')

import typing
from termcolor import cprint
from nubia import command, argument, context
from prettytable import PrettyTable

# app settings
from lnma import db, create_app, srv_paper, srv_project
from lnma.models import *
from lnma import dora
from lnma import ss_state

from lnma import bp_extractor
from lnma import srv_import

# app for using LNMA functions and tables
app = create_app()
db.init_app(app)
app.app_context().push()


@command
class Importer:
    """
    Importer related commands
    """

    @command
    @argument("keystr", type=str, description="The keystr for a project")
    @argument("pmid", type=str, description="The pmid for a paper")
    @argument("nct", type=str, description="The NCT number for a paper")
    def add_by_pmid(self, keystr:str, pmid:str, nct=None):
        '''
        Add a new PMID to paper
        '''
        if pmid.strip() == '':
            print('* pmid can not be empty')
            return 

        is_success, paper = srv_import.import_by_pmid(keystr, pmid, nct)

        if is_success:
            print('* added to %s a new pmid %s [%s]' % (
                keystr, pmid, paper.title
            ))
        else:
            print('* Error when add this paper')