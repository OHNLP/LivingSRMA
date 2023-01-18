"""
Deduplicate related functions
"""
import os
import json
from datetime import datetime
from tqdm import tqdm

from lnma import settings
from lnma import srv_paper
from lnma import dora

from flask import current_app
from lnma import celery_app

def get_fn_job(keystr):
    '''
    Get the file name for job description
    '''
    full_fn_job = os.path.join(
        current_app.instance_path, 
        settings.PATH_DEDUPLICATE, 
        keystr,
        'job.json'
    )

    return full_fn_job


def get_fn_rst(keystr):
    '''
    Get the file name for results
    '''
    full_fn_job = os.path.join(
        current_app.instance_path, 
        settings.PATH_DEDUPLICATE, 
        keystr,
        'rst.json'
    )

    return full_fn_job


def update_job(keystr, n_completed, status='RUNNING'):
    '''
    Update the job status and numbers
    '''
    # load the job
    full_fn_job = get_fn_job(keystr)
    job = json.load(open(full_fn_job))

    # update number
    job['n_completed'] = n_completed
    job['status'] = status
    job['date_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if status == 'COMPLETED':
        job['date_completed'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # save it
    save_job_file(keystr, job)


def save_job_file(keystr, job):
    '''
    Save the job file
    '''
    # make the folder
    job_path = os.path.join(
        current_app.instance_path, 
        settings.PATH_DEDUPLICATE, 
        keystr
    )
    if os.path.exists(job_path):
        pass
    else:
        os.makedirs(job_path)
        print('* created directory %s' % job_path)

    full_fn_job = get_fn_job(keystr)

    # save it!
    with open(full_fn_job, 'w') as f:
        json.dump(job, f)
    
    return full_fn_job


def save_rst_file(keystr, rst):
    '''
    Save the result file
    '''
    # make the folder
    job_path = os.path.join(
        current_app.instance_path, 
        settings.PATH_DEDUPLICATE, 
        keystr
    )
    if os.path.exists(job_path):
        pass
    else:
        os.makedirs(job_path)
        print('* created directory %s' % job_path)

    full_fn_rst = get_fn_rst(keystr)

    # save it!
    with open(full_fn_rst, 'w') as f:
        json.dump(rst, f, default=str)
    
    return full_fn_rst


def make_job(keystr, n_papers, status='RUNNING'):
    '''
    Make the job
    '''
    # create the job json
    job = {
        'n_papers': n_papers,
        'n_completed': 0,
        'keystr': keystr,
        'status': status,
        'date_created': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'date_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'date_completed': 'TBD',
    }

    # just run the deduplicate task in background
    async_start_deduplicate.delay(keystr)

    # save it
    save_job_file(keystr, job)
    print('* made the deduplicate search job %s' % keystr)
    return job


@celery_app.task()
def async_start_deduplicate(keystr):
    '''
    Get deduplicated papers
    '''
    project = dora.get_project_by_keystr(keystr)
    print('* got the [%s] project information' % keystr)

    papers = dora.get_papers_by_keystr(keystr)
    print('* got %s papers for project [%s]' % (
        len(papers), keystr
    ))

    title_dict = {}
    # for saving duplicates
    for p1_idx, p1 in enumerate(tqdm(papers)):
        p1_title = p1.title.lower()

        if p1_title in title_dict:
            # this title has been duplicated with existing record
            title_dict[p1_title].append(p1)
        else:
            # this title is a new record
            title_dict[p1_title] = [p1]
        
        # update progress
        if p1_idx % 10 == 0:
            update_job(keystr, p1_idx+1)
    
    print('* parsed %s titles in %s papers for deduplication' % (
        len(title_dict),
        len(papers)
    ))

    update_job(keystr, p1_idx+1, 'COMPLETED')

    # extract the duplicates only
    dup_dict = {}
    stat = {
        "n_both_excluded": 0,
    }
    for title in title_dict:
        if len(title_dict[title]) == 1:
            # which means this is not a duplicate
            pass
        else:
            dup_dict[title] = []
            # update the selection
            for p in title_dict[title]:
                dup_dict[title].append(p.pid)
                
            # and do some quick statistics

    # save the results
    save_rst_file(keystr, {
        'stat': stat,
        'dup_dict': dup_dict
    })

    return dup_dict


