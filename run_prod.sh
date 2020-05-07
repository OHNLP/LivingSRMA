#!/bin/bash

export FLASK_APP=lnma
export FLASK_ENV=production

gunicorn -b localhost:60088 -w 4 lnma.wsgi:app