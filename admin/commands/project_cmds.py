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
class Project:
    """
    Project related commands
    """

    @command
    def list(self):
        '''
        List the projects in the system
        '''
        projects = dora.list_all_projects()
        table = PrettyTable([
            'Keystr', 'Title', 'Members'
        ])
        for project in projects:
            table.add_row([
                project.keystr, project.title,
                ','.join(map(lambda u: u.first_name, project.related_users))
            ])
        print(table)


    @command
    @argument("keystr", type=str, description="The keystr for a project")
    @argument("are_you_sure", type=str, description="yes for final confirmation")

    def delete_all_extracts(self, keystr:str, are_you_sure:str):
        '''
        Delete all extracts for a project
        '''
        if are_you_sure != 'yes':
            print('* deletion cancelled')
            return 

        projects = dora.list_all_projects()
        dora.delete_all_extracts_by_keystr(keystr)

        print('* deleted all extracts!')
