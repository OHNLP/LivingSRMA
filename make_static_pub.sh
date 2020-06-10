#!/bin/bash

URL_BASE='http://localhost:60088'
FOLDER_BASE='../pub'

# get the index
curl "$URL_BASE/pub/" -o "$FOLDER_BASE/index.html"

# get the RCC
curl "$URL_BASE/prisma.html" -o "$FOLDER_BASE/templates/study_prisma_diagram.html"
curl "$URL_BASE/study_char_table.html" -o "$FOLDER_BASE/templates/study_char_table.html"
curl "$URL_BASE/study_outcome_graph.html" -o "$FOLDER_BASE/templates/study_outcome_graph.html"
echo '* downloaed 4 pages'

# get the CAT related
curl "$URL_BASE/pub/slide.html" -o "$"

# copy libs
mkdir -p $FOLDER_BASE/static/lib
cp -r ./web/static/lib/alasql $FOLDER_BASE/static/lib/
cp -r ./web/static/lib/chance.js $FOLDER_BASE/static/lib/
cp -r ./web/static/lib/d3 $FOLDER_BASE/static/lib/
cp -r ./web/static/lib/echarts $FOLDER_BASE/static/lib/
cp -r ./web/static/lib/element-ui $FOLDER_BASE/static/lib/
cp -r ./web/static/lib/file-saver $FOLDER_BASE/static/lib/
cp -r ./web/static/lib/font-awesome $FOLDER_BASE/static/lib/
cp -r ./web/static/lib/jquery $FOLDER_BASE/static/lib/
cp -r ./web/static/lib/jquery-ui $FOLDER_BASE/static/lib/
cp -r ./web/static/lib/papaparse $FOLDER_BASE/static/lib/
cp -r ./web/static/lib/vue.js $FOLDER_BASE/static/lib/
echo '* copied all packages'

# copy image
cp -r ./web/static/img $FOLDER_BASE/static/
echo '* copied all images'

# copy data
mkdir -p $FOLDER_BASE/graphdata
cp -r ./lnma-data/* $FOLDER_BASE/graphdata/
echo '* copied all graph data'