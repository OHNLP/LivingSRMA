#%% load packages and env
import os
import json
import requests

import logging
logger = logging.getLogger("watcher")
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.WARNING, format='%(asctime)s %(levelname)s %(name)s: %(message)s')

from sqlalchemy import and_, or_, not_

from lnma import db, create_app
from lnma.models import *
from lnma import dora

# app for using LNMA functions and tables
app = create_app()
db.init_app(app)
app.app_context().push()


#%% check updates

# query = 'renal cell cancer AND "last 2 years"[Date - Create]'
# j = search(query)


#%% try mailbox

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
            'created': []
        }
    }
    logger.info('inited the keywords and pmid list for project %s' % project.keystr)

logger.info('found %s projects to be updated' % (len(project_keystrs)))


from imbox import Imbox

myimbox = Imbox('imap.gmail.com',
    username='lisrbot2020@gmail.com',
    password='uxeldnwjfpvfjccq',
    ssl=True,
    ssl_context=None,
    starttls=False)

# get all the mails
all_inbox_messages = myimbox.messages()

# check the latest mails
for i in range(1, len(all_inbox_messages)+1):
    # get the latest one first
    uid, mail = all_inbox_messages[-i]

    # check this email belong to which project or not
    for prj in project_keystrs:
        keyword = prj_updates[prj]['keyword']

        if keyword in mail.subject:
            # check the content of this email
            content = '\n'.join(mail.body['plain'])

            # split into lines
            lines = content.split('\n')

            # check each line
            for line in lines:
                if line.startswith('UI  -'): 
                    # this line is about the pmid!
                    pmid = line.split('-')[1].strip()

                    # add new pmid to project update list
                    prj_updates[prj]['pmids'].append(pmid)

                    logger.debug('found and added %s for prject [%s] in %s' % (pmid, prj, line))

                else:
                    pass
        else:
            logger.debug('ignored unrelated email %s' % mail.subject)

# create / update the list of project
for prj in project_keystrs:
    pmids = prj_updates[prj]['pmids']
    project_id = prj_updates[prj]['project'].project_id

    for pmid in pmids:
        ret = dora.create_paper_if_not_exist(project_id, pmid)

        if ret is None:
            prj_updates[prj]['cnt']['existed'].append(pmid)
        else:
            prj_updates[prj]['cnt']['created'].append(pmid)

    logger.info('checked %s studies for project %s, existed: %s, created: %s' % \
        (len(pmids), prj, 
        len(prj_updates[prj]['cnt']['existed']), 
        len(prj_updates[prj]['cnt']['created'])))

# updated, generate a report for this run
report = ''
