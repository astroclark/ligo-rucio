#!/bin/sh -e
git commit -a -m "Incremental change in testing"
git push
#ssh james.clark@rucio.ligo.caltech.edu update-repo.sh
ssh james.clark@rucio.ligo.caltech.edu "pushd ligo-rucio && git pull && popd"
gsissh ldas-pcdev6.ligo.caltech.edu "pushd Projects/ligo-rucio && git pull && popd"

