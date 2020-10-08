#!/bin/bash
PRJ=$1

if test -z "$PRJ"; then
    echo "* project short name is needed!"
    exit 1
else
    echo "* prepare the standalone webpage for $PRJ"
fi

scp -r instance/pubdata/$PRJ lnmasrv:/home/m210842/sites/lnma/instance/pubdata/$PRJ