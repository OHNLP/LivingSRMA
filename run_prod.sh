#!/bin/bash

export FLASK_APP=lnma
export FLASK_ENV=production
export GUNICORN_TIMEOUT=120

# create the tmp folder for files
mkdir -p /dev/shm/lnma

# run!
gunicorn \
    -b localhost:60088 \
    --timeout $GUNICORN_TIMEOUT \
    -w 4 lnma.wsgi:app