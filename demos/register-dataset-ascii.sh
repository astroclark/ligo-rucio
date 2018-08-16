#!/bin/bash
rucio_repo=/home/jclark/Projects/ligo-rucio
source ${rucio_repo}/client/etc/rucio-user-env.sh

${rucio_repo}/demos/register-dataset-ascii.py \
    --rse LIGO-CIT \
    --dataset-name test-dataset-0 \
    --debug --verbose \
    --dry-run \
    --file-list /home/jclark/Projects/ligo-rucio/data/test-dataset-0.dat
