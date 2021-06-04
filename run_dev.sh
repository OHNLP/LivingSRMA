#!/bin/bash

export FLASK_APP=lnma
export FLASK_ENV=development
export LNMA_DEVEL_SERVER=localhost

# create the tmp folder for files
mkdir -p /dev/shm/lnma

# run!
flask run -h 0.0.0.0 -p 8088