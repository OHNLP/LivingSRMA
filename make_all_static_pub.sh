#!/bin/bash

URL_BASE='http://localhost:8088/pub'
PUB_BASE='../lnma_pub'
FOLDER_BASE="$PUB_BASE/ALLPRJS"
mkdir -p $FOLDER_BASE


# check sub folders
mkdir -p $FOLDER_BASE/pub
mkdir -p $FOLDER_BASE/static/lib
mkdir -p $FOLDER_BASE/pub/graphdata
echo "* checked output folders in $FOLDER_BASE"


# get the index
curl "$URL_BASE/" -o "$FOLDER_BASE/index.html"


# get the shared module
curl "$URL_BASE/prisma.html" -o "$FOLDER_BASE/pub/prisma.html"
curl "$URL_BASE/itable.html" -o "$FOLDER_BASE/pub/itable.html"
curl "$URL_BASE/slide.html" -o "$FOLDER_BASE/pub/slide.html"
curl "$URL_BASE/graph_v1.html" -o "$FOLDER_BASE/pub/graph_v1.html"
curl "$URL_BASE/graph_v2.html" -o "$FOLDER_BASE/pub/graph_v2.html"
curl "$URL_BASE/graph_v2_1.html" -o "$FOLDER_BASE/pub/graph_v2_1.html"
curl "$URL_BASE/graph_v3.html" -o "$FOLDER_BASE/pub/graph_v3.html"
echo '* downloaed shared module'


# get the CAT related
PRJ='CAT'
mkdir -p $FOLDER_BASE/pub/graphdata/$PRJ
curl "$URL_BASE/$PRJ.html" -o "$FOLDER_BASE/$PRJ.html"
curl "$URL_BASE/graphdata/$PRJ/ITABLE.json" -o "$FOLDER_BASE/pub/graphdata/$PRJ/ITABLE.json"
echo "* downloaed $PRJ.html"


# get the RCC related
PRJ='RCC'
mkdir -p $FOLDER_BASE/pub/graphdata/$PRJ
curl "$URL_BASE/$PRJ.html" -o "$FOLDER_BASE/$PRJ.html"
curl "$URL_BASE/graphdata/$PRJ/ITABLE.json" -o "$FOLDER_BASE/pub/graphdata/$PRJ/ITABLE.json"
echo "* downloaed $PRJ.html"


# copy libs
cp -r ./lnma/static/lib/alasql $FOLDER_BASE/static/lib/
cp -r ./lnma/static/lib/d3 $FOLDER_BASE/static/lib/
cp -r ./lnma/static/lib/echarts $FOLDER_BASE/static/lib/
cp -r ./lnma/static/lib/element-ui $FOLDER_BASE/static/lib/
cp -r ./lnma/static/lib/file-saver $FOLDER_BASE/static/lib/
cp -r ./lnma/static/lib/font-awesome $FOLDER_BASE/static/lib/
cp -r ./lnma/static/lib/jquery $FOLDER_BASE/static/lib/
cp -r ./lnma/static/lib/jquery-ui $FOLDER_BASE/static/lib/
cp -r ./lnma/static/lib/vue.js $FOLDER_BASE/static/lib/
echo '* copied all packages'


# copy image
cp -r ./lnma/static/img $FOLDER_BASE/static/
echo '* copied all images'


# copy data
cp -r ./instance/pubdata/* $FOLDER_BASE/pub/graphdata/
echo '* copied all graph data'