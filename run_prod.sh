#!/bin/bash

export FLASK_APP=lnma
export FLASK_ENV=production

# create the tmp folder for files
mkdir -p /dev/shm/lnma

# run!
gunicorn -b localhost:60088 -w 4 lnma.wsgi:app