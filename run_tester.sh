#!/bin/bash

export FLASK_APP=lnma
export FLASK_ENV=development
export LNMA_DEVEL_SERVER=localhost

# create the tmp folder for files
ipython -i dev_tester.py