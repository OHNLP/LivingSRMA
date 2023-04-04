# #%% load packages and env
# import os
# import json
# import requests
# import argparse

# import logging
# logger = logging.getLogger("watcher")
# logger.setLevel(logging.INFO)
# logging.basicConfig(level=logging.WARNING, format='%(asctime)s [%(name)s] [%(levelname)s] %(message)s')

# from sqlalchemy import and_, or_, not_
# from tqdm import tqdm

# # for looping the watcher
# from timeloop import Timeloop
# from datetime import timedelta

# # for checking email updates
# from imbox import Imbox

# # app settings
# from lnma import db, create_app
# from lnma.models import *
# from lnma import dora
# from lnma import util
# from lnma import ss_state

# # app for using LNMA functions and tables
# app = create_app()
# db.init_app(app)
# app.app_context().push()

# # get username and password for the watcher email
# WATCHER_EMAIL_USERNAME = app.config['WATCHER_EMAIL_USERNAME']
# WATCHER_EMAIL_PASSWORD = app.config['WATCHER_EMAIL_PASSWORD']


# def _update_papers_in_project(prj_updates):
#     # get all keystrs
#     project_keystrs = prj_updates.keys()

#     # create / update the list of project
#     for keystr in project_keystrs:
#         pmids = prj_updates[keystr]['pmids']
#         project_id = prj_updates[keystr]['project'].project_id

#         new_pmids = []
#         for pmid in pmids:
#             if dora.is_existed_paper(project_id, pmid):
#                 prj_updates[keystr]['cnt']['existed'].append(pmid)
#             else:
#                 new_pmids.append(pmid)

#         if len(new_pmids) == 0:
#             # no new papers!
#             logger.info('found %s pmdis + 0 new studies for project [%s]' % ( len(pmids), keystr))
#             continue

#         # get data of these new studies 
#         data = util.e_fetch(new_pmids)

#         # create paper in database
#         created_pmids = []
#         for pmid in data['result']['uids']:
#             created_pmids.append(pmid)
#             # ok, save these new papers
#             paper = data['result'][pmid]
#             title = paper['title']
#             pub_date = paper['sortpubdate'].split(' ')[0]
#             authors = ', '.join([ a['name'] for a in paper['authors'] ])
#             journal = paper['source']
#             abstract = paper['abstract']

#             paper = dora.create_paper(project_id, pmid, 'pmid',
#                 title, abstract, pub_date, authors, journal, 
#                 ss_state.SS_ST_AUTO_EMAIL
#             )
#             prj_updates[keystr]['cnt']['created'].append(pmid)

#         # for those not founded in pmid
#         notfound_pmids = list(set(new_pmids).difference(created_pmids))
#         for pmid in notfound_pmids:
#             paper = dora.create_paper_if_not_exist(project_id, pmid, 'pmid',
#                 ss_st=ss_state.SS_ST_AUTO_EMAIL,
#                 ss_rs=ss_state.SS_RS_EXCLUDED_NOTFOUND
#             )
#             prj_updates[keystr]['cnt']['notfound'].append(pmid)

#         logger.info('found %s studies for project [%s], existed: %s, created: %s, not found %s' % (\
#             len(pmids), keystr, 
#             len(prj_updates[keystr]['cnt']['existed']), 
#             len(prj_updates[keystr]['cnt']['created']),
#             len(prj_updates[keystr]['cnt']['notfound']),
#         ))

#     return prj_updates


# def _update_papers_in_project_v2(prj_updates):
#     # get all keystrs
#     project_keystrs = prj_updates.keys()

#     # create / update the list of project
#     for keystr in project_keystrs:
#         papers = prj_updates[keystr]['papers']
#         project_id = prj_updates[keystr]['project'].project_id

#         new_papers = []
#         for paper in papers:
#             pid = paper['UI']

#             if dora.is_existed_paper(project_id, pid):
#                 prj_updates[keystr]['cnt']['existed'].append(pid)
#             else:
#                 new_papers.append(paper)

#         if len(new_papers) == 0:
#             # no new papers!
#             logger.info('found %s pmdis + 0 new studies for project [%s]' % ( len(papers), keystr))
#             continue

#         # create paper in database
#         created_paperss = []
#         for paper in new_papers:
#             created_paperss.append(paper)

#             # ok, save these new papers
#             pid = paper['UI']
#             title = paper['TI'] if 'TI' in paper else ''
#             abstract = paper['AB'] if 'AB' in paper else ''
#             authors = ', '.join(paper['AU']) if 'AU' in paper else ''
#             pid_type = paper['DB'].upper() if 'DB' in paper else 'OVID'

#             if pid_type.startswith('EMBASE'):
#                 pid_type = 'EMBASE'
#                 pub_date = paper['DP'] if 'DP' in paper else ''
#                 journal = paper['JA'] if 'JA' in paper else ''
#             elif pid_type.startswith('OVID MEDLINE'):
#                 pid_type = 'OVID MEDLINE'
#                 pub_date = paper['EP'] if 'EP' in paper else ''
#                 journal = paper['AS'] if 'AS' in paper else ''
#             else:
#                 pid_type = 'OVID'
#                 pub_date = paper['EP'] if 'EP' in paper else ''
#                 journal = paper['AS'] if 'AS' in paper else ''
        
#             paper_db = dora.create_paper(project_id, pid, pid_type,
#                 title, abstract, pub_date, authors, journal, {'paper': paper},
#                 ss_state.SS_ST_AUTO_EMAIL, None, None
#             )
#             prj_updates[keystr]['cnt']['created'].append(pid)

#         logger.info('found %s studies for project [%s], existed: %s, created: %s' % (\
#             len(papers), keystr, 
#             len(prj_updates[keystr]['cnt']['existed']), 
#             len(prj_updates[keystr]['cnt']['created']),
#         ))

#     return prj_updates


# def lookup_email(username, password):
#     '''Check if there is updates in email
#     '''
#     # get the project shortnames
#     projects = Project.query.filter(and_(
#         Project.is_deleted == 'no'
#     )).all()

#     # keep the keystr list and dictionary
#     project_keystrs = []
#     prj_updates = {}

#     for project in projects:
#         project_keystrs.append(project.keystr)
#         prj_updates[project.keystr] = {
#             'keyword': '%s_UPDATE' % project.keystr,
#             'project': project,
#             'pmids': [],
#             'cnt': {
#                 'existed': [],
#                 'notfound': [],
#                 'created': [],
#             }
#         }
#         logger.info('inited the keywords and pmid list for project %s' % project.keystr)

#     logger.info('found %s projects to be updated' % (len(project_keystrs)))

#     # open the email inbox
#     myimbox = Imbox('imap.gmail.com',
#         username=username,
#         password=password,
#         ssl=True,
#         ssl_context=None,
#         starttls=False)

#     # get all the mails
#     all_inbox_messages = myimbox.messages()
#     logger.info('found %s emails!' % len(all_inbox_messages))

#     # check the latest mails
#     cnt = {
#         'ovid_update': 0,
#         'other': 0
#     }

#     for i in tqdm(range(1, len(all_inbox_messages)+1)):
#         # get the latest one first
#         uid, mail = all_inbox_messages[-i]

#         # check the email date, ignore old emails

#         # check this email belong to which project or not
#         for prj in project_keystrs:
#             keyword = prj_updates[prj]['keyword']

#             if keyword in mail.subject:
#                 cnt['ovid_update'] += 1
#                 # check the content of this email
#                 content = '\n'.join(mail.body['plain'])

#                 # split into lines
#                 lines = content.split('\n')

#                 # check each line
#                 for line in lines:
#                     if line.startswith('UI  -') or \
#                        line.startswith('UI -') or \
#                        line.startswith('UI-'): 
#                         # this line is about the pmid!
#                         pmid = line.split('-')[1].strip()

#                         # add new pmid to project update list
#                         prj_updates[prj]['pmids'].append(pmid)

#                         logger.debug('found and added %s for prject [%s] in %s' % (pmid, prj, line))

#                     else:
#                         pass
#             else:
#                 cnt['other'] += 1
#                 logger.debug('ignored unrelated email %s' % mail.subject)

#     logger.info('parsed %s from OVID updates, %s other emails' % (
#         cnt['ovid_update'], cnt['other']
#     ))

#     # create or update
#     prj_updates = _update_papers_in_project(prj_updates)

#     # updated, generate a report for this run
#     report = ''

#     logger.info('* done lookup email!')


# def lookup_email_v2(username, password):
#     '''Check if there is updates in email and parse the email content
#     '''
#     # get the project shortnames
#     projects = Project.query.filter(and_(
#         Project.is_deleted == 'no'
#     )).all()

#     # keep the keystr list and dictionary
#     project_keystrs = []
#     prj_updates = {}

#     for project in projects:
#         project_keystrs.append(project.keystr)
#         prj_updates[project.keystr] = {
#             'keyword': '%s_UPDATE' % project.keystr,
#             'project': project,
#             'papers': [],
#             'cnt': {
#                 'existed': [],
#                 'notfound': [],
#                 'created': [],
#             }
#         }
#         logger.info('inited the keywords and pmid list for project %s' % project.keystr)

#     logger.info('found %s projects to be updated' % (len(project_keystrs)))

#     # open the email inbox
#     myimbox = Imbox('imap.gmail.com',
#         username=username,
#         password=password,
#         ssl=True,
#         ssl_context=None,
#         starttls=False)

#     # get all the mails
#     all_inbox_messages = myimbox.messages()
#     logger.info('found %s emails!' % len(all_inbox_messages))

#     # check the latest mails
#     cnt = {
#         'ovid_update': 0,
#         'other': 0
#     }

#     for i in tqdm(range(1, len(all_inbox_messages)+1)):
#         # get the latest one first
#         uid, mail = all_inbox_messages[-i]

#         # check the email date, ignore old emails
#         # TODO: also check the title

#         # check this email belong to which project or not
#         is_other_email = True
#         for prj in project_keystrs:
#             keyword = prj_updates[prj]['keyword']

#             if keyword in mail.subject:
#                 is_study_update_email = False
#                 cnt['ovid_update'] += 1
#                 # check the content of this email
#                 content = ''.join(mail.body['plain'])

#                 # get the articles from email content
#                 papers = util.ovid_parser(content)
#                 logger.debug('found and %s papers for prject [%s] in %s' % (len(papers), prj, mail.subject))

#                 # put these papers in update list
#                 prj_updates[prj]['papers'] += papers

#                 # once find project, skip other
#                 # so, we have a hypothesis here, that one email belong and only belong to one project if related.
#                 break

#         if is_other_email:
#             cnt['other'] += 1
#             logger.debug('ignored unrelated email %s' % mail.subject)

#     logger.info('parsed %s from OVID updates, %s other emails' % (
#         cnt['ovid_update'], cnt['other']
#     ))

#     # create or update
#     prj_updates = _update_papers_in_project_v2(prj_updates)

#     # updated, generate a report for this run
#     report = ''

#     logger.info('* done lookup email!')


# def lookup_pubmed():
#     '''Check if there is updates in pubmed
#     '''
#     # get the project shortnames
#     projects = Project.query.filter(and_(
#         Project.is_deleted == 'no'
#     )).all()

#     # prepare the dictionary for updates
#     project_keystrs = []
#     prj_updates = {}

#     for project in projects:
#         project_keystrs.append(project.keystr)
#         prj_updates[project.keystr] = {
#             'keyword': '%s_UPDATE' % project.keystr,
#             'project': project,
#             'query': project.settings['query'],
#             'pmids': [],
#             'cnt': {
#                 'existed': [],
#                 'notfound': [],
#                 'created': [],
#             }
#         }
#         logger.info('inited the keywords and for project [%s]' % project.keystr)

#     logger.info('found %s projects to be updated' % (len(prj_updates)))

#     # loop on project to get the pmids
#     for keystr in project_keystrs:
#         project_id = prj_updates[keystr]['project'].project_id
#         # get the query
#         query = prj_updates[keystr]['query']

#         # get data from pubmed
#         data = util.e_search(query)
#         logger.info('searched "%s" for project [%s]' % (query, project.keystr))

#         # get all pmids
#         pmids = data['esearchresult']['idlist']
#         prj_updates[keystr]['pmids'] = pmids

#     # create or update
#     prj_updates = _update_papers_in_project(prj_updates)

#     # updated, generate a report for this run
#     report = ''

#     # check each update
#     logger.info('* done lookup pubmed!')


# # define the loop
# watcher_tl = Timeloop()

# # the email watcher
# @watcher_tl.job(interval=timedelta(days=1))
# def tl_lookup_email():
#     lookup_email(WATCHER_EMAIL_USERNAME, WATCHER_EMAIL_PASSWORD)

# # the pubmed watcher
# @watcher_tl.job(interval=timedelta(hours=1))
# def tl_lookup_pubmed():
#     lookup_pubmed()


# # define the parse for argument
# parser = argparse.ArgumentParser('LNMA Watcher')
# parser.add_argument("--loop", type=str, 
#     choices=['yes', 'no'], default='yes',
#     help="Run watcher in loop mode or not")
# parser.add_argument("--act", type=str, 
#     choices=['all', 'lookup_pubmed', 'lookup_email'], default='all',
#     help="Run which action when not loop")

# args = parser.parse_args()

# if args.loop == 'no':
#     if args.act == 'lookup_pubmed':
#         lookup_pubmed()
#     elif args.act == 'lookup_email':
#         lookup_email_v2(WATCHER_EMAIL_USERNAME, WATCHER_EMAIL_PASSWORD)
#     elif args.act == 'all':
#         lookup_pubmed()
#         lookup_email(WATCHER_EMAIL_USERNAME, WATCHER_EMAIL_PASSWORD)
#     else:
#         parser.print_help()
#         exit
# elif args.loop == 'yes':
#     # wow! start loop!
#     watcher_tl.start(block=True)

