#!/bin/sh -e

# Create RSE
rucio-admin rse add LIGO-CIT-ARCHIVE

# Define copying protocol
rucio-admin rse add-protocol\
    --prefix /hdfs/frames \
    --hostname ldas-pcdev2.ligo.caltech.edu\
    --domain-json '{"wan": {"read": 1, "write": 0, "delete": 0, "third_party_copy": 1}}' \
    --scheme gsiftp \
    --port 2811 \
    LIGO-CIT-ARCHIVE


# FTS configuration
rucio-admin rse set-attribute --rse LIGO-CIT-ARCHIVE --key fts --value https://fts.mwt2.org:8446
rucio-admin rse set-attribute --rse LIGO-CIT-ARCHIVE --key fts_testing --value https://fts.mwt2.org:8446

# Disk quota
rucio-admin -a root account set-limits root LIGO-CIT-ARCHIVE 1000000000000

# Make this part of the LIGO lab network
rucio-admin rse set-attribute --rse LIGO-CIT-ARCHIVE --key archive --value True

