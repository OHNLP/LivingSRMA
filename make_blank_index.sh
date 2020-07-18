#!/bin/bash

URL_BASE='http://localhost:8088/pub'
PUB_BASE='../lnma_pub'
FOLDER_BASE="$PUB_BASE/BLANKINDEX"

# make folder base
mkdir -p $FOLDER_BASE
echo "* created FOLDER_BASE: $FOLDER_BASE"

# get the index
curl "$URL_BASE/blankindex" -o "$FOLDER_BASE/index.html"
echo '* copied blank index page'