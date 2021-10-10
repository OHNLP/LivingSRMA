#!/bin/bash

export FLASK_APP=lnma
export FLASK_ENV=development
export LNMA_DEVEL_SERVER=localhost
export WERKZEUG_DEBUG_PIN='off'

# create the tmp folder for files
mkdir -p /dev/shm/lnma

# run!
flask run -h 0.0.0.0 -p 8088