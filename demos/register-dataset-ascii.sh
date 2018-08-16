#!/bin/bash
rucio_repo=/home/jclark/Projects/ligo-rucio
source ${rucio_repo}/client/etc/rucio-user-env.sh

./mini_dataset.py \
    --rse LIGO-CIT \
    --dataset-name test-dataset-0 \
    --debug --verbose \
    --file-list /home/jclark/Projects/ligo-rucio/data/test-dataset-0.dat
