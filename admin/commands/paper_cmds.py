import sys
sys.path.append('..')
import textwrap

from termcolor import colored, cprint
from nubia import command, argument, context
from prettytable import PrettyTable

# app settings
from lnma import db, create_app, srv_paper
from lnma.models import *
from lnma import dora
from lnma import ss_state

# app for using LNMA functions and tables
app = create_app()
db.init_app(app)
app.app_context().push()


@command
class Paper:
    """
    Paper related commands
    """
    @command
    @argument("keystr", type=str, description="The keystr for a project")
    @argument("seq_num", type=int, description="The sequence number of the paper in project")
    async def check_rct(self, keystr:str, seq_num:int):
        """
        Check the RCT for a paper
        """
        paper = dora.update_paper_rct_result_by_keystr_and_seq_num(keystr, seq_num)
        if paper.meta['pred'][0]['is_rct']:
            cprint('* Paper [%s][%s] is RCT!' % (
                seq_num, paper.title[:40]), 'green')
        else:
            cprint('* Paper [%s][%s] is NOT RCT!' % (
                seq_num, paper.title[:40]), 'red')
    

    @command
    @argument("keystr", type=str, description="The keystr for a project")
    @argument("seq_num", type=int, description="The sequence number of the paper in project")
    async def check_ext(self, keystr:str, seq_num:int):
        """
        Check the extraction for a paper
        """
        has_used_in_extracts = srv_paper.check_usage_in_extracts(
            keystr, seq_num
        )

        print('* checked')


    # @command
    # @argument("keystr", type=str, description="The keystr for a project")
    # @argument("seq_num", type=int, description="The sequence number of the paper in project")
    # @argument("is_del", type=str, description="[y]es/[n]o?")
    # async def mark_del(self, keystr:str, seq_num:int, is_del:str):
    #     """
    #     Mark is_delete to a paper
    #     """
    #     is_deleted = is_del == 'y'
    #     paper = dora.set_paper_is_deleted_by_keystr_and_seq_num(keystr, seq_num, is_deleted)
    #     if paper.is_deleted == 'yes':
    #         cprint('* Paper [%s][%s] is deleted!' % (
    #             seq_num, paper.title[:40]), 'red')
    #     else:
    #         cprint('* Paper [%s][%s] is still there!' % (
    #             seq_num, paper.title[:40]), 'green')


    @command
    @argument("keystr", type=str, description="The keystr for a project")
    @argument("seq_num", type=int, description="The sequence number of the paper in project")
    @argument("force", type=str, description="Force delete even if used in extracts?")
    @argument("are_you_sure", type=str, description="yes for final confirmation")
    async def delete(self, keystr:str, seq_num:int, are_you_sure:str, force:str='no'):
        """
        Delete a paper from DB
        """
        if are_you_sure != 'yes':
            print('* delete cancelled')
            return 

        if force == 'yes':
            is_stop_when_used = False
        else:
            is_stop_when_used = True

        success = srv_paper.delete_paper_from_db_by_seq_num(
            keystr,
            seq_num,
            is_stop_when_used
        )

        if success:
            print('* deleted!')

        else:
            print('* failed to delete')


    @command
    @argument("keystr", type=str, description="The keystr for a project")
    @argument("seq_num", type=int, description="The paper sequence number in this project")
    def get(self, keystr:str, seq_num:int):
        '''
        Get a paper by keystr and seq
        '''
        paper = dora.get_paper_by_keystr_and_seq(keystr, seq_num)

        if paper is None:
            cprint('* wrong keystr [%s] or wrong seq_num [%s]' % (
                keystr, seq_num
            ))
            return

        table = PrettyTable([
            'Attr', 'Details'
        ])
        table.align['Attr'] = 'l'
        table.align['Details'] = 'l'
        
        # the first row is basic information
        table.add_row([
            'Basic Info.',
            "%s | %s (%s) | %s | %s" % (
                paper.seq_num, 
                paper.pid,
                paper.pid_type,
                paper.journal,
                paper.pub_date
            )
        ])

        # this row is the RCT info
        txt_is_rct = colored('NO', 'red')
        if paper.meta['pred'][0]['is_rct']:
            txt_is_rct = colored('YES', 'white', 'on_green')

        # the txt of rct_id
        txt_rct_id = ''
        if paper.meta['rct_id'] != '':
            txt_rct_id = colored(paper.meta['rct_id'], 'white', 'on_green')

        table.add_row([
            'RCT Info.',
            "Is RCT: %s | # RCT: %s" % (
                txt_is_rct, txt_rct_id
            )
        ])

        # the text of tags
        txt_tags = ''
        if 'tags' in paper.meta:
            txt_tags = ' | '.join(paper.meta['tags'])

        table.add_row([
            'Tags',
            txt_tags
        ])

        # the second row is the authors, limit the width the display
        table.add_row([
            'Authors',
            textwrap.shorten(paper.authors, 80, placeholder='...')
        ])

        # this row is the title
        table.add_row([
            'Paper Title',
            textwrap.shorten(paper.title, 80, placeholder='...')
        ])

        # this row is the title
        table.add_row([
            'Abstract',
            textwrap.fill(
                textwrap.shorten(paper.abstract, 320, placeholder='...'),
                80
            )
        ])

        print(table)


    @command
    @argument("keystr", type=str, description="The keystr for a project")
    @argument("seq_num", type=int, description="The paper sequence number in this project")
    @argument("val", type=str, description="The ss_st val, a12 for auto, a24 for manual")
    def set_ss_st(self, keystr:str, seq_num:int, val:str):
        '''
        Set the ss_st for a specific paper
        '''
        paper = dora.get_paper_by_keystr_and_seq(keystr, seq_num)

        if paper is None:
            cprint('* wrong keystr [%s] or wrong seq_num [%s]' % (
                keystr, seq_num
            ))
            return

        if val not in ['a12', 'a24']:
            cprint('* wrong ss_st val [%s]' % (
                val
            ))
            return

        iss, _p = srv_paper.set_paper_ss_st(
            paper.paper_id,
            val
        )
        print('* set %s.%s.ss_st -> %s' % (
            keystr, seq_num, _p.ss_st
        ))

        print('* done')
            