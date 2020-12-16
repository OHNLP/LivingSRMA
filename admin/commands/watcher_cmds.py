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

# watcher 
from watcher import ovid_email_watcher

@command
class Watcher:
    """
    Watcher related commands
    """

    @command
    def email(self):
        '''
        Check the email updates
        '''
        ovid_email_watcher.check_updates()

