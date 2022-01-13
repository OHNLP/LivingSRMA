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
    

    @command
    @argument("keystr", type=str, description="The keystr for a project")
    @argument("full_path", type=str, description="The full path to the data file")
    @argument("data_type", type=str, description="Which data type: endnote, ovid?")
    @argument("act", type=str, description="What to do: check, save?")
    @argument("show_detail", type=str, description="Show detail? yes or no")
    def add_by_file(self, keystr:str, full_path:str, data_type=str, 
        act=str, show_detail=str):
        '''
        Add new studies by given data file
        '''
        if data_type not in ['endnote', 'ovid']:
            print("* not supported data_type=%s" % data_type)
            return

        # check only?
        if act == 'check':
            ret = srv_paper.check_existed_paper_by_file(
                keystr, data_type, full_path
            )
            # let's output the result
            print('* - Total records: %s' % (ret['cnt']['total']))
            print('* - Existed: %s' % (ret['cnt']['existed']))
            print('* - New: %s' % (ret['cnt']['new']))

            if show_detail == 'yes':
                # show all existed
                print('* ----- EXISTED -----')
                for p in ret['papers']['existed']:
                    print('* - {0: <10} [{1:0>5}] {2: <40}'.format(
                        p['p']['pid'],
                        p['seq'],
                        p['p']['title']
                    ))
                
                # show all new
                print('* ----- NEW PPS -----')
                for p in ret['papers']['new']:
                    print('* - {0: <10} [NEW] {1: <40}'.format(
                        p['p']['pid'],
                        p['p']['title']
                    ))

        elif act == 'save':
            ret = srv_paper.save_paper_by_jsonpapers
        
        print('* done add by file!')

