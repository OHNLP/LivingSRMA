#!/bin/bash

export FLASK_APP=lnma
export FLASK_ENV=development

# create the tmp folder for files
mkdir -p /dev/shm/lnma

# run!
flask run -h 0.0.0.0 -p 8088