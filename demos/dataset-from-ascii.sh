#!/bin/bash
# Get current pycbc
source ${PWD}/etc/rucio-user-env.sh


./mini_dataset.py \
    --rse LIGO-CIT \
    --dataset-name test-dataset-0 \
    --debug --verbose \
    --file-list data-insertion/test-dataset-0.dat
