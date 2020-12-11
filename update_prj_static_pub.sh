#!/bin/bash
PRJ=$1
echo "* update ${PRJ} project standalone website"
./make_prj_static_pub.sh $PRJ

echo "* commit changes to lnma_pub repository"
cd ../lnma_pub
git add -A

NOW=`date`
git commit -m "auto update ${PRJ} at ${NOW}"
git push

NOW=`date`
echo "* done at ${NOW}"
