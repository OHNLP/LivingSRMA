#!/bin/bash

URL_BASE='http://localhost:8088'
PUB_BASE='../living-evidence'

# get the index
curl "$URL_BASE/pub/hub.html" -o "$PUB_BASE/index.html"
echo '* copied hub as landing page'

# copy libs
mkdir -p $PUB_BASE/static
cp -r ./lnma/static/* $PUB_BASE/static
echo '* copied static files'