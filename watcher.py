#%% load packages and env
import os
import json
import requests
import argparse

import logging
logger = logging.getLogger("watcher")
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.WARNING, format='%(asctime)s [%(name)s] [%(levelname)s] %(message)s')

from sqlalchemy import and_, or_, not_
from tqdm import tqdm

# for looping the watcher
from timeloop import Timeloop
from datetime import timedelta

# for checking email updates
from imbox import Imbox

# app settings
from lnma import db, create_app
from lnma.models import *
from lnma import dora
from lnma import util
from lnma import ss_state

# app for using LNMA functions and tables
app = create_app()
db.init_app(app)
app.app_context().push()

# get username and password for the watcher email
WATCHER_EMAIL_USERNAME = app.config['WATCHER_EMAIL_USERNAME']
WATCHER_EMAIL_PASSWORD = app.config['WATCHER_EMAIL_PASSWORD']


def lookup_email(username, password):
    '''Check if there is updates in email
    '''
    # get the project shortnames
    projects = Project.query.filter(and_(
        Project.is_deleted == 'no'
    )).all()

    # keep the keystr list and dictionary
    project_keystrs = []
    prj_updates = {}

    for project in projects:
        project_keystrs.append(project.keystr)
        prj_updates[project.keystr] = {
            'keyword': '%s_UPDATE' % project.keystr,
            'project': project,
            'pmids': [],
            'cnt': {
                'existed': [],
                'notfound': [],
                'created': [],
            }
        }
        logger.info('inited the keywords and pmid list for project %s' % project.keystr)

    logger.info('found %s projects to be updated' % (len(project_keystrs)))

    # open the email inbox
    myimbox = Imbox('imap.gmail.com',
        username=username,
        password=password,
        ssl=True,
        ssl_context=None,
        starttls=False)

    # get all the mails
    all_inbox_messages = myimbox.messages()
    logger.info('found %s emails!' % len(all_inbox_messages))

    # check the latest mails
    cnt = {
        'ovid_update': 0,
        'other': 0
    }

    for i in tqdm(range(1, len(all_inbox_messages)+1)):
        # get the latest one first
        uid, mail = all_inbox_messages[-i]

        # check the email date, ignore old emails

        # check this email belong to which project or not
        for prj in project_keystrs:
            keyword = prj_updates[prj]['keyword']

            if keyword in mail.subject:
                cnt['ovid_update'] += 1
                # check the content of this email
                content = '\n'.join(mail.body['plain'])

                # split into lines
                lines = content.split('\n')

                # check each line
                for line in lines:
                    if line.startswith('UI  -') or \
                       line.startswith('UI -') or \
                       line.startswith('UI-'): 
                        # this line is about the pmid!
                        pmid = line.split('-')[1].strip()

                        # add new pmid to project update list
                        prj_updates[prj]['pmids'].append(pmid)

                        logger.debug('found and added %s for prject [%s] in %s' % (pmid, prj, line))

                    else:
                        pass
            else:
                cnt['other'] += 1
                logger.debug('ignored unrelated email %s' % mail.subject)

    logger.info('parsed %s from OVID updates, %s other emails' % (
        cnt['ovid_update'], cnt['other']
    ))

    # create / update the list of project
    for prj in project_keystrs:
        pmids = prj_updates[prj]['pmids']
        project_id = prj_updates[prj]['project'].project_id

        new_pmids = []
        for pmid in pmids:
            if dora.is_existed_paper(project_id, pmid):
                prj_updates[prj]['cnt']['existed'].append(pmid)
            else:
                new_pmids.append(pmid)

        if len(new_pmids) == 0:
            # no new papers!
            logger.info('found %s pmdis + 0 new studies for project %s' % ( len(pmids), prj))
            continue

        # get data of these new studies 
        data = util.e_fetch(new_pmids)

        # create paper in database
        created_pmids = []
        for pmid in data['result']['uids']:
            created_pmids.append(pmid)
            # ok, save these new papers
            paper = data['result'][pmid]
            title = paper['title']
            pub_date = paper['sortpubdate'].split(' ')[0]
            authors = ', '.join([ a['name'] for a in paper['authors'] ])
            journal = paper['source']
            abstract = paper['abstract']

            paper = dora.create_paper(project_id, pmid, 'pmid',
                title, abstract, pub_date, authors, journal, 
                ss_state.SS_ST_AUTO_EMAIL
            )
            prj_updates[prj]['cnt']['created'].append(pmid)

        # for those not founded in pmid
        notfound_pmids = list(set(new_pmids).difference(created_pmids))
        for pmid in notfound_pmids:
            paper = dora.create_paper_if_not_exist(project_id, pmid, 'pmid',
                ss_st=ss_state.SS_ST_AUTO_EMAIL,
                ss_rs=ss_state.SS_RS_EXCLUDED_NOTFOUND
            )
            prj_updates[prj]['cnt']['notfound'].append(pmid)

        logger.info('found %s studies for project %s, existed: %s, created: %s, not found %s' % (\
            len(pmids), prj, 
            len(prj_updates[prj]['cnt']['existed']), 
            len(prj_updates[prj]['cnt']['created']),
            len(prj_updates[prj]['cnt']['notfound']),
        ))

        # for the rest of pmids, use esummary to find again?
        

    # updated, generate a report for this run
    report = ''

    logger.info('* done lookup email!')


def lookup_pubmed():
    '''Check if there is updates in pubmed
    '''
    logger.info('* done lookup pubmed!')


# define the loop
watcher_tl = Timeloop()

# the email watcher
@watcher_tl.job(interval=timedelta(days=1))
def tl_lookup_email():
    lookup_email(WATCHER_EMAIL_USERNAME, WATCHER_EMAIL_PASSWORD)

# the pubmed watcher
@watcher_tl.job(interval=timedelta(hours=1))
def tl_lookup_pubmed():
    lookup_pubmed()


# define the parse for argument
parser = argparse.ArgumentParser('LNMA Watcher')
parser.add_argument("--loop", type=str, 
    choices=['yes', 'no'], default='yes',
    help="Run watcher in loop mode or not")
parser.add_argument("--act", type=str, 
    choices=['all', 'lookup_pubmed', 'lookup_email'], default='all',
    help="Run which action when not loop")

args = parser.parse_args()

if args.loop == 'no':
    if args.act == 'lookup_pubmed':
        lookup_pubmed()
    elif args.act == 'lookup_email':
        lookup_email(WATCHER_EMAIL_USERNAME, WATCHER_EMAIL_PASSWORD)
    elif args.act == 'all':
        lookup_pubmed()
        lookup_email(WATCHER_EMAIL_USERNAME, WATCHER_EMAIL_PASSWORD)
    else:
        parser.print_help()
        exit
elif args.loop == 'yes':
    # wow! start loop!
    watcher_tl.start(block=True)