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
from lnma import srv_extract

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
    @argument("keystr", type=str, description="The keystr for a project")
    @argument("new_keystr", type=str, description="The title for a project")
    def set_keystr(self, keystr:str, new_keystr:str):
        '''
        Set new keystr for a project
        '''
        if new_keystr.strip() == '':
            print('* new_keystr can not be empty')
            return 

        srv_project.set_project_keystr_by_keystr(keystr, new_keystr)

        print('* Set the new_keystr to %s -> %s' % (
            keystr, new_keystr
        ))


    @command
    @argument("keystr", type=str, description="The keystr for a project")
    @argument("title", type=str, description="The title for a project")
    def set_title(self, keystr:str, title:str):
        '''
        Set title for a project
        '''
        if title.strip() == '':
            print('* Title can not be empty')
            return 

        srv_project.set_project_title_by_keystr(keystr, title)

        print('* Set the title to %s: %s' % (
            keystr, title
        ))
    

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
    def delete_all_papers(self, keystr:str, are_you_sure:str):
        '''
        Delete all papers in a project
        '''
        if are_you_sure != 'yes':
            print('* deletion cancelled')
            return 

        srv_project.delete_all_papers_by_keystr(keystr)

        print('* deleted all papers!')


    @command
    @argument("keystr", type=str, description="The keystr for a project")
    @argument("cq_abbr", type=str, description="The cq_abbr for a clinical question")
    @argument("oc_type", type=str, description="The oc type, nma or pwma or itable or all")
    @argument("are_you_sure", type=str, description="yes for final confirmation")
    def delete_all_extracts(self, keystr:str, cq_abbr:str, oc_type:str, are_you_sure:str):
        '''
        Delete all extracts in a project
        '''
        if are_you_sure != 'yes':
            print('* deletion cancelled')
            return

        if oc_type not in ['nma', 'pwma', 'itable', 'all']:
            print('* which oc type?')
            return

        srv_project.delete_all_extracts_by_keystr(keystr, cq_abbr, oc_type)

        print('* deleted all extracts!')


    @command
    @argument("keystr", type=str, description="The keystr for a project")
    @argument("fn", type=str, description="The file name of the data file")
    @argument("data_format", type=str, description="The format, endnote_xml or ovid_xml")
    @argument("are_you_sure", type=str, description="yes for final confirmation")
    def import_studies(self, keystr:str, fn:str, data_format:str, are_you_sure:str):
        '''
        Import the studies from given file
        '''
        if are_you_sure != 'yes':
            print('* import cancelled')
            return 

        if data_format == 'endnote_xml':
            is_success, papers = srv_import.import_endnote_xml(fn, keystr)

        elif data_format == 'ovid_xml':
            pass

        elif data_format == 'pmid_csv':
            pass

        else:
            print('* unknown data_format %s, import cancelled' % data_format)
            return 

        print('* imported %s papers!' % (
            len(papers)
        ))


    @command
    @argument("keystr", type=str, description="The keystr for a project")
    @argument("cq_abbr", type=str, description="The cq_abbr for a clinical question")
    @argument("full_path", type=str, description="The full path to the data file")
    @argument("oc_type", type=str, description="The oc type, nma or pwma")
    @argument("are_you_sure", type=str, description="yes for final confirmation")
    def import_extracts(self, 
        keystr:str, 
        cq_abbr:str, 
        full_path:str, 
        oc_type:str, 
        are_you_sure:str
    ):
        '''
        Import the extacts data from Excel file
        '''
        if are_you_sure != 'yes':
            print('* import cancelled')
            return 
        
        if oc_type not in ['nma', 'pwma']:
            print("* not supported oc_type=%s" % oc_type)
            return

        srv_extract.import_extracts_from_xls(
            full_path,
            keystr,
            cq_abbr,
            oc_type,
        )

        print('* done import extracts')
    

    # @command
    # @argument("keystr", type=str, description="The keystr for a project")
    # @argument("cq_abbr", type=str, description="The cq_abbr for a clinical question")
    # @argument("fn", type=str, description="The file name of the data file")
    # @argument("group", type=str, description="The default analysis group for a project")
    # @argument("are_you_sure", type=str, description="yes for final confirmation")
    # def import_softable_pma(self, keystr:str, cq_abbr:str, fn:str, group:str, are_you_sure:str):
    #     '''
    #     Import the SOFTABLE PWMA data from Excel file
    #     '''
    #     if are_you_sure != 'yes':
    #         print('* import cancelled')
    #         return 

    #     # extracts = bp_extractor.import_softable_pma_from_xls(keystr, cq_abbr, fn, group)

    #     # print('* imported %s extracts!' % (
    #     #     len(extracts)
    #     # ))
    #     print('* not fully implemented yet')


    @command
    @argument("keystr", type=str, description="The keystr for a project")
    @argument("cq_abbr", type=str, description="The cq_abbr for a clinical question")
    @argument("full_fn_itable", type=str, description="The full file name of the data file")
    @argument("full_fn_filter", type=str, description="The full file name of the data file")
    @argument("are_you_sure", type=str, description="yes for final confirmation")
    def import_itable(self, keystr:str, cq_abbr:str, full_fn_itable:str, full_fn_filter:str, are_you_sure:str):
        '''
        Import and itable data from Excel file
        '''
        if are_you_sure != 'yes':
            print('* import cancelled')
            return 

        itable = srv_extract.import_itable_from_xls(
            keystr, 
            cq_abbr, 
            full_fn_itable,
            full_fn_filter
        )

        if itable is None:
            print('* something wrong when importing %s' % (
                keystr
            ))
        else:
            print('* imported %s studies in itable!' % (
                len(itable.data)
            ))
    

    @command
    @argument("keystr", type=str, description="The keystr for a project")
    @argument("are_you_sure", type=str, description="yes for final confirmation")
    def update_pub_date(self, keystr:str, are_you_sure:str):
        '''
        Update the pub_date for those included in SR
        '''
        if are_you_sure != 'yes':
            print('* update cancelled')
            return 

        srv_paper.update_all_srma_paper_pub_date(keystr)

        print('* updated pub date!')