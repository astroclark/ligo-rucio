#!/bin/sh -e

# Get ascii list of frames with e.g., ls -d -1 $PWD/**/*gwf.  Ideally use DiskCache.
# Better yet: find $PWD -type f -name *gwf
ligo_register_dataset \
    --rse LIGO-CIT \
    --scope TEST \
    --dataset-name L-L1_HOFT_C00-11370b \
    --debug --verbose \
    --file-list /home/jclark/Projects/ligo-rucio/data/L-L1_HOFT_C00-11370.txt
