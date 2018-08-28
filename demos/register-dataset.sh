#!/bin/sh -e

# Get ascii list of frames with e.g., ls -d -1 $PWD/**/*gwf.  Ideally use DiskCache.
ligo_register_dataset \
    --rse LIGO-CIT \
    --dataset-name test-dataset-4y \
    --debug --verbose \
    --file-list /home/jclark/Projects/ligo-rucio/data/test-filelist.txt
    #--lifetime 600 \
