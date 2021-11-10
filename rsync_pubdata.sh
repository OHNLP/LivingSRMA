#!/bin/bash
PRJ=$1
CQ=$2

if test -z "$PRJ"; then
    echo "* project short name is needed!"
    exit 1
else
    echo "* project: $PRJ"
fi

if test -z "$CQ"; then
    echo "* cq short name is needed!"
    exit 1
else
    echo "* cq: $CQ"
fi

echo "* uploading the data file for $PRJ/$CQ"

# upload now!
rsync -r instance/pubdata/$PRJ/$CQ/* lnmasrv:/home/m210842/sites/lnma/instance/pubdata/$PRJ/$CQ/

echo "* done!"