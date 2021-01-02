#!/bin/bash

URL_BASE='http://localhost:8088/pub'
PRJ=$1

if test -z "$PRJ"; then
    echo "* project short name is needed!"
    exit 1
else
    echo "* prepare the standalone webpage for $PRJ"
fi

PUB_BASE='../lnma_pub'
FOLDER_BASE="$PUB_BASE/$PRJ"

# make folder base
mkdir -p $FOLDER_BASE
echo "* created FOLDER_BASE: $FOLDER_BASE"

# check sub folders
mkdir -p $FOLDER_BASE/pub
mkdir -p $FOLDER_BASE/static
mkdir -p $FOLDER_BASE/pub/graphdata
echo "* checked output folders in $FOLDER_BASE"

# copy static content
cp -r ./lnma/static/* $FOLDER_BASE/static/
echo '* copied all static content'

# get the sub index for this project
curl "$URL_BASE/subindex/$PRJ" -o "$FOLDER_BASE/index.html"

# get the shared module
curl "$URL_BASE/prisma.html" -o "$FOLDER_BASE/pub/prisma.html"
curl "$URL_BASE/prisma_v2.html" -o "$FOLDER_BASE/pub/prisma_v2.html"
curl "$URL_BASE/prisma_v3.html" -o "$FOLDER_BASE/pub/prisma_v3.html"
curl "$URL_BASE/itable.html" -o "$FOLDER_BASE/pub/itable.html"
curl "$URL_BASE/slide.html" -o "$FOLDER_BASE/pub/slide.html"
curl "$URL_BASE/graph_v1.html" -o "$FOLDER_BASE/pub/graph_v1.html"
curl "$URL_BASE/graph_v2.html" -o "$FOLDER_BASE/pub/graph_v2.html"
curl "$URL_BASE/graph_v2_1.html" -o "$FOLDER_BASE/pub/graph_v2_1.html"
curl "$URL_BASE/graph_v3.html" -o "$FOLDER_BASE/pub/graph_v3.html"
curl "$URL_BASE/graph_RCC.html" -o "$FOLDER_BASE/pub/graph_RCC.html"
curl "$URL_BASE/softable_pma.html" -o "$FOLDER_BASE/pub/softable_pma.html"
curl "$URL_BASE/softable_nma.html" -o "$FOLDER_BASE/pub/softable_nma.html"
curl "$URL_BASE/softable_pma_v2.html" -o "$FOLDER_BASE/pub/softable_pma_v2.html"
curl "$URL_BASE/softable_nma_v2.html" -o "$FOLDER_BASE/pub/softable_nma_v2.html"
curl "$URL_BASE/evmap.html" -o "$FOLDER_BASE/pub/evmap.html"
curl "$URL_BASE/evmap_tr.html" -o "$FOLDER_BASE/pub/evmap_tr.html"
curl "$URL_BASE/evmap_tr_v2.html" -o "$FOLDER_BASE/pub/evmap_tr_v2.html"
echo "* downloaed shared module for project $PRJ"

# get the project page
mkdir -p $FOLDER_BASE/pub/graphdata/$PRJ
curl "$URL_BASE/$PRJ.html" -o "$FOLDER_BASE/$PRJ.html"
echo "* downloaed $PRJ.html"

# copy pubdata
cp -r ./instance/pubdata/$PRJ/* $FOLDER_BASE/pub/graphdata/$PRJ/
echo '* copied all graph data'

# get the data files
curl "$URL_BASE/graphdata/$PRJ/ITABLE.json" -o "$FOLDER_BASE/pub/graphdata/$PRJ/ITABLE.json"
curl "$URL_BASE/graphdata/$PRJ/ITABLE_CFG.json" -o "$FOLDER_BASE/pub/graphdata/$PRJ/ITABLE_CFG.json"
curl "$URL_BASE/graphdata/$PRJ/PRISMA.json" -o "$FOLDER_BASE/pub/graphdata/$PRJ/PRISMA.json"
curl "$URL_BASE/graphdata/$PRJ/SOFTABLE_PMA.json?v=2" -o "$FOLDER_BASE/pub/graphdata/$PRJ/SOFTABLE_PMA.json"
# curl "$URL_BASE/graphdata/$PRJ/SOFTABLE_NMA.json" -o "$FOLDER_BASE/pub/graphdata/$PRJ/SOFTABLE_NMA.json"
# curl "$URL_BASE/graphdata/$PRJ/EVMAP.json" -o "$FOLDER_BASE/pub/graphdata/$PRJ/EVMAP.json"
# echo "* download the data jsons"

echo "* completed $PRJ static website" 