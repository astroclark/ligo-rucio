#!/bin/sh -e

# Get ascii list of frames with e.g., ls -d -1 $PWD/**/*gwf.  Ideally use DiskCache.
# Better yet: find $PWD -type f -name *gwf
ligo_register_dataset \
    --rse LIGO-CIT \
    --lifetime 600 \
    --dataset-name test-dataset-1 \
    --debug --verbose \
    --file-list /home/jclark/Projects/ligo-rucio/data/test-filelist.txt
