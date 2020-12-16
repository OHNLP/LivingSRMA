#%% load packages and env
import os
import re

import sys
sys.path.append("..") 

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
from lnma import ss_state

# for the RCT 
from lnma.util import pred_rct

# app for using LNMA functions and tables
app = create_app()
db.init_app(app)
app.app_context().push()

# get username and password for the watcher email
WATCHER_EMAIL_USERNAME = app.config['WATCHER_EMAIL_USERNAME']
WATCHER_EMAIL_PASSWORD = app.config['WATCHER_EMAIL_PASSWORD']

PAPER_EMAIL_KEY = '_UPDATE'

def check_updates():
    '''Check the updates of all projects
    '''
    projects = Project.query.filter(and_(
        Project.is_deleted == 'no'
    )).all()
    
    for project in projects:
        _check_update_by_project(project)

    return 0


def check_update_by_prj_keystr(prj_keystr):
    '''Check update by project keystr
    '''
    project = Project.query.filter(and_(
        Project.is_deleted == 'no',
        Project.keystr == prj_keystr
    )).first()

    if project is None:
        # TODO what???
        pass

    ret = _check_update_by_project(project)
    return ret


def _get_all_paper_emails_from_inbox():
    '''
    Get all paper emails from in the inbox
    '''
    # first, open the imbox
    myimbox = Imbox('imap.gmail.com',
        username=WATCHER_EMAIL_USERNAME,
        password=WATCHER_EMAIL_PASSWORD,
        ssl=True,
        ssl_context=None,
        starttls=False)

    # get all the mails
    all_inbox_messages = myimbox.messages()
    logger.info('found %s emails in total!' % len(all_inbox_messages))

    # check the latest mails
    cnt = {
        'paper': 0,
        'other': 0
    }

    emails = []
    # check all the mails and summarize the information
    for i in tqdm(range(1, len(all_inbox_messages)+1)):
        # get the latest one first
        uid, mail = all_inbox_messages[-i]

        # check the email date, ignore old emails
        # TODO: also check the title

        # check this email belong to which project or not
        if PAPER_EMAIL_KEY in mail.subject:
            
            cnt['paper'] += 1
            # check the content of this email
            content = ''.join(mail.body['plain'])

            paper_email = {
                'subject': mail.subject,
                'content': content
            }
            
            emails.append(paper_email)
        else:
            # skip this email?
            cnt['other'] += 1
            pass

    logger.info('found %s paper email, %s other emails' % (
        cnt['paper'], cnt['other']
    ))

    return emails


def _check_update_by_project(project):
    '''Check the updates of a specified project
    '''
    # the keyword in subject is always XXX_UPDATE
    # where the XXX is the project id
    prj_subject_keyword = '%s_UPDATE' % project.keystr.upper()

    # first, open the imbox
    myimbox = Imbox('imap.gmail.com',
        username=WATCHER_EMAIL_USERNAME,
        password=WATCHER_EMAIL_PASSWORD,
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
    prj_update = {
        'keyword': prj_subject_keyword,
        'project': project,
        'papers': [],
        'cnt': {
            'existed': [],
            'notfound': [],
            'created': [],
        }
    }

    logger.info('parsing %s emails ...' % len(all_inbox_messages))

    # check all the mails and summarize the information
    for i in tqdm(range(1, len(all_inbox_messages)+1)):
        # get the latest one first
        uid, mail = all_inbox_messages[-i]

        # check the email date, ignore old emails
        # TODO: also check the title

        # check this email belong to which project or not
        is_other_email = True

        if prj_subject_keyword in mail.subject:
            is_other_email = False
            cnt['ovid_update'] += 1
            # check the content of this email
            content = ''.join(mail.body['plain'])

            # get the articles from email content
            papers = ovid_parser(content)
            logger.debug('found and %s papers for prject [%s] in %s' % \
                (len(papers), project.keystr, mail.subject))

            # put these papers in update list
            prj_update['papers'] += papers
            
        else:
            # skip this email?
            pass

        if is_other_email:
            cnt['other'] += 1
            logger.debug('ignored unrelated email %s' % mail.subject)

    logger.info('found %s email of %s papers related to project [%s], %s other emails' % (
        cnt['ovid_update'], len(prj_update['papers']), project.keystr, cnt['other']
    ))

    # reduce the duplicate paper in the updates
    unique_pid_dict = {}
    for paper in prj_update['papers']:
        if 'UI' in paper:
            pid = paper['UI']
            if pid in unique_pid_dict:
                pass
            else:
                unique_pid_dict[pid] = paper
        else:
            # if no UI in paper, this is not a paper
            pass

    unique_papers = unique_pid_dict.values()
    logger.info('removed the duplicate records %s -> %s' % (
        len(prj_update['papers']),
        len(unique_papers)
    ))
    
    # update the prj_update
    prj_update['papers'] = unique_papers

    # create or update
    prj_updated = _update_papers_in_project(prj_update)

    # updated, generate a report for this run
    logger.info('done check email for project [%s]!' % project.keystr)

    return prj_updated


def _update_papers_in_project(prj_update):
    '''Update the project papers in the prj_update:

    prj_update = {
        'keyword': prj_subject_keyword,
        'project': prj,
        'papers': [],
        'cnt': {
            'existed': [],
            'notfound': [],
            'created': [],
        }
    }

    '''
    # create / update the list of project
    papers = prj_update['papers']
    project_id = prj_update['project'].project_id

    new_papers = []
    for paper in tqdm(papers):
        if 'UI' in paper:
            pid = paper['UI']
            is_existed, _paper = dora.is_existed_paper(project_id, pid)
            if is_existed:
                prj_update['cnt']['existed'].append(pid)
            else:
                new_papers.append(paper)
        else:
            # UI not in paper, which means this is not a paper?
            pass

    if len(new_papers) == 0:
        # no new papers!
        logger.info('found 0 new paper for project [%s]' % ( prj_update['project'].keystr ))
        return 0
    else:
        logger.info('found %s new papers for project [%s]!' % (
            len(new_papers), prj_update['project'].keystr
        ))

    # create paper in database
    created_papers = []
    for paper in tqdm(new_papers):
        created_papers.append(paper)

        # ok, save these new papers
        pid = paper['UI']
        title = paper['TI'] if 'TI' in paper else ''
        abstract = paper['AB'] if 'AB' in paper else ''
        authors = ', '.join(paper['AU']) if 'AU' in paper else ''
        pid_type = paper['DB'].upper() if 'DB' in paper else 'OVID'

        if pid_type.startswith('EMBASE'):
            pid_type = 'EMBASE'
            pub_date = paper['DP'] if 'DP' in paper else ''
            journal = paper['JA'] if 'JA' in paper else ''
        elif pid_type.startswith('OVID MEDLINE'):
            pid_type = 'OVID MEDLINE'
            pub_date = paper['EP'] if 'EP' in paper else ''
            journal = paper['AS'] if 'AS' in paper else ''
        else:
            pid_type = 'OVID'
            pub_date = paper['EP'] if 'EP' in paper else ''
            journal = paper['AS'] if 'AS' in paper else ''
    
        paper_db = dora.create_paper(project_id, pid, pid_type,
            title, abstract, pub_date, authors, journal, {'paper': paper},
            ss_state.SS_ST_AUTO_EMAIL, None, None, None
        )
        
        # update the RCT info
        dora.update_paper_rct_result(paper_db.project_id, paper_db.pid)

        # 
        prj_update['cnt']['created'].append(pid)

    logger.info('done %s papers for project [%s], existed: %s, created: %s' % (\
        len(papers), prj_update['keyword'], 
        len(prj_update['cnt']['existed']), 
        len(prj_update['cnt']['created']),
    ))

    return len(created_papers)


def ovid_parser(txt):
    '''Parse the email content from OVID 
    '''
    # open('tmp.txt', 'w').write(txt)

    lines = txt.split('\n')
    ptn_attr = r'^\s*([A-Z]{2})\s+-\s(.*)'
    ptn_attr_ext = r'^\s+(.*)'
    ptn_new_art = r'^\s*\<(\d+)\>'

    arts = []

    # temporal variable
    art = {}
    attr = ''

    for line in lines:
        # try attr pattern first, it's the most common pattern
        m = re.findall(ptn_attr, line)
        if len(m) > 0:
            # which means it's a new attribute
            # for example
            # > re.findall(ptn_attr, 'DB  - Ovid MEDLINE(R) Revisions')
            # > [('DB', 'Ovid MEDLINE(R) Revisions')]
            attr = m[0][0]
            val = m[0][1].strip()

            # auto seg by UI
            if attr == 'UI' and 'UI' in art:
                arts.append(art)
                art = {}

            # append this attr
            if attr not in art: art[attr] = []

            # put this value into art object
            art[attr].append(val)

            # once match a pattern, no need to check other patterns
            continue

        # try next pattern
        m = re.findall(ptn_attr_ext, line)
        if len(m) > 0:
            # this means this line is an extension of previous attr
            val = m[0]
            # use previous attr, the attr should exist
            if attr == '':
                pass
            else:
                art[attr].append(val)

                # once match a pattern, no need to check other patterns
                continue

        # try next pattern
        m = re.findall(ptn_new_art, line)
        if len(m) > 0:
            # this means this line starts a new article
            if art == {}:
                pass
            else:
                arts.append(art)
                art = {}
            
            # once match a pattern, no need to check other patterns
            continue
    
    # usually, the last art need to be appended manually
    if art != {}:
        arts.append(art)

    # now need to merge
    for art in arts:
        for k in art:
            if len(art[k]) == 1:
                art[k] = art[k][0]
            else:
                if k in ('AU', 'FA', 'ID'): continue
                elif k == 'AB': art[k] = '\n'.join(art[k])
                else: art[k] = ' '.join(art[k])
    return arts
