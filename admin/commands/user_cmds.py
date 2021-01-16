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
class User:
    """
    User related commands
    """

    @command
    def list(self):
        '''
        List the users in the system
        '''
        users = dora.list_all_users()
        table = PrettyTable([
            'First Name', 'Last Name', 'Email/uid'
        ])
        for user in users:
            table.add_row([
                user.first_name, user.last_name, user.uid
            ])
        print(table)


    @command
    @argument("email", type=str, description="The email address of this user")
    @argument("first_name", type=str, description="The first name of this user")
    @argument("last_name", type=str, description="The last name of this user")
    @argument("password", type=str, description="The raw password")
    async def create(self, email:str, first_name:str, last_name:str, password:str):
        """
        Create a new user if not exists
        """
        is_exist, user = dora.create_user_if_not_exist(
            email, 
            first_name,
            last_name,
            password
        )
        if is_exist:
            cprint('* existed user [%s] (%s %s), skipped' % (
                user.uid, user.first_name, user.last_name), 'red')
        else:
            cprint('* created user [%s] (%s %s)' % (
                user.uid, user.first_name, user.last_name), 'green')


    @command
    @argument("email", type=str, description="The email address of this user")
    @argument("password", type=str, description="The raw password")
    async def pswd(self, email:str, password:str):
        """
        Reset password for a user
        """
        is_exist, user = dora.is_existed_user(email)
        if is_exist:
            dora.reset_user_password(email, password)
            cprint('* reseted password for user [%s]' % (
                user.uid), 'green')
        else:
            cprint('* not found user [%s]' % (
                user.uid), 'red')

    
    @command
    @argument("uid", type=str, description="The uid of the user")
    @argument("keystr", type=str, description="The unique project keystr")
    def assign_project(self, uid:str, keystr:str):
        """
        Assign user to a project
        """
        is_in, user, project = dora.add_user_to_project_by_keystr_if_not_in(uid, keystr)

        if is_in is None:
            cprint('* wrong user [%s] or project [%s]' % (
                uid, keystr
            ), 'white', 'on_red')
        elif is_in:
            cprint('* existed user [%s] in project [%s | %s]' % (
                uid, project.keystr, project.title
            ), 'red')
        else:
            cprint('* added user [%s] to project [%s | %s]' % (
                uid, project.keystr, project.title
            ), 'green')


    @command
    @argument("uid", type=str, description="The uid of the user")
    @argument("keystr", type=str, description="The unique project keystr")
    def unlink_project(self, uid:str, keystr:str):
        """
        unlink user from a project
        """
        is_in, user, project = dora.remove_user_from_project_by_keystr_if_in (uid, keystr)

        if is_in is None:
            cprint('* wrong user [%s] or project [%s]' % (
                uid, keystr
            ), 'white', 'on_red')
        elif is_in:
            cprint('* removed user [%s] in project [%s | %s]' % (
                uid, project.keystr, project.title
            ), 'red')
        else:
            cprint('* what user [%s] to project [%s | %s]' % (
                uid, project.keystr, project.title
            ), 'green')
