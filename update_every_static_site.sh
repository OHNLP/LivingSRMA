#!/bin/bash

echo "* update CAT project standalone website"
./make_prj_static_pub.sh CAT

echo "* update RCC project standalone website"
./make_prj_static_pub.sh RCC

echo "* update ALL projects public website"
./make_all_static_pub.sh

echo "* commit changes to lnma_pub repository"
cd ../lnma_pub
git add -A

NOW=`date`
git commit -m "auto update at ${NOW}"
git push

NOW=`date`
echo "* done at ${NOW}"
