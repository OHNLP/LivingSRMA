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
class Db:
    """
    Database related commands
    """

    @command
    def project(self):
        """
        Show project information?
        """
        print('project?')

    
    @command
    def user(self):
        """
        Show user information?
        """
        print('user?')
