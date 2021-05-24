import sys
sys.path.append('..')

import typing
from termcolor import cprint
from nubia import command, argument, context
from prettytable import PrettyTable

# app settings
from lnma import db, create_app
from lnma.models import *
from lnma import dora
from lnma import ss_state

# app for using LNMA functions and tables
app = create_app()
db.init_app(app)
app.app_context().push()


@command
class Screener:
    """
    Screener related commands
    """
        
    @command
    @argument("keystr", type=str, description="The keystr for a project")
    @argument("pids", description="The list of pids, comma seperated")
    @argument("ssrs", type=str, description="Stage? e2,e22,f1,f3")
    @argument("are_you_sure", type=str, description="yes for final confirmation")
    def ss(self, keystr:str, pids:typing.List[str], ssrs:str, are_you_sure:str):
        '''
        Set stage (SS_RS) to the given pids
        '''
        if are_you_sure != 'yes':
            print('* setup cancelled')
            return 

        # check the ss rs
        if ssrs not in ['e2', 'e22', 'f1', 'f3']:
            print('* the input stage is invalid')
            return 

        # get the stage
        stage = ss_state.SS_RS2STAGE[ssrs]

        # ok, check each one
        for pid in pids:
            # remove the blank
            pid = pid.strip()

            # first, get this paper
            paper = dora.get_paper_by_keystr_and_pid(keystr, pid)

            # if not exists??
            if paper is None:
                print('* MISSING paper %s' % pid)
                continue

            # create a detail for this operation
            detail_dict = util.get_decision_detail_dict(
                ss_state.SS_REASON_CHECKED_BY_ADMIN,
                stage
            )

            # ok, save
            p = dora.set_paper_pr_rs_with_details(
                paper.paper_id, 
                pr=ss_state.SS_PR_CHECKED_BY_ADMIN,
                rs=ssrs,
                detail_dict=detail_dict)
            
            print('* updated paper rs=%s to %s' % (p.ss_rs, p.pid))

        print('* setup all pids!')

