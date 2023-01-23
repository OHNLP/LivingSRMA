#%% load packages and env
import os
import json

import sys
sys.path.append("..") 

import requests
import argparse

import logging
logger = logging.getLogger("scheduler")
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.WARNING, format='%(asctime)s [%(name)s] [%(levelname)s] %(message)s')

# for looping the watcher
from timeloop import Timeloop
from datetime import timedelta

# the watchers
import ovid_email_watcher

# the timeloop for all events
watcher_tl = Timeloop()

# the email watcher
@watcher_tl.job(interval=timedelta(days=1))
def check_ovid_email():
    ovid_email_watcher.check_updates()

# the pubmed watcher
# @watcher_tl.job(interval=timedelta(hours=1))
# def tl_lookup_pubmed():
#     lookup_pubmed()

def run():
    # define the parse for argument
    parser = argparse.ArgumentParser('LNMA Scheduler for Watchers')
    parser.add_argument("-loop", type=str, 
        choices=['yes', 'no'], default='no',
        help="Run watcher in loop mode or not")
    parser.add_argument("--act", type=str, 
        choices=['check_email', 'check_pubmed', 'all'],
        help="Run which action when not loop")
    parser.add_argument("--prj", type=str, default='all',
        help="The prj keystr, e.g., IO, RCC, CAT, etc.")
    parser.add_argument("--skip_n_days", type=int, default=None,
        help="skip the emails of N days before")

    args = parser.parse_args()

    # no loop, just run once
    if args.loop == 'no':
        # check emails for specified project(s)
        if args.act == 'check_pubmed':
            pass

        # check emails for specified project(s)
        elif args.act == 'check_email':
            if args.prj == 'all':
                ovid_email_watcher.check_updates(
                    args.skip_n_days
                )
            else:
                ovid_email_watcher.check_update_by_prj_keystr(
                    args.prj,
                    args.skip_n_days
                )
                
        # do all checking for specified project(s)
        elif args.act == 'all':
            if args.prj == 'all':
                ovid_email_watcher.check_updates(
                    args.skip_n_days
                )
            else:
                ovid_email_watcher.check_update_by_prj_keystr(
                    args.prj,
                    args.skip_n_days
                )

        # something wrong?
        else:
            parser.print_help()
            exit

    elif args.loop == 'yes':
        # wow! start loop!
        watcher_tl.start(block=True)

    else:
        parser.print_help()


if __name__ == "__main__":
    run()