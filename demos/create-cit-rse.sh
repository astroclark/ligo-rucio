#!/bin/sh -e

# Create RSE
rucio-admin rse add LIGO-CIT-HDFS

# Define copying protocol
rucio-admin rse add-protocol\
    --prefix /hdfs/user/rucio \
    --hostname ldas-pcdev6.caltech.edu\
    --domain-json '{"wan": {"read": 1, "write": 1, "delete": 1, "third_party_copy": 1}}' \
    --scheme gsiftp \
    --port 2811 \
    LIGO-CIT-HDFS


# FTS configuration
rucio-admin rse set-attribute --rse LIGO-CIT-HDFS --key fts --value https://fts.mwt2.org:8446
rucio-admin rse set-attribute --rse LIGO-CIT-HDFS --key fts_testing --value https://fts.mwt2.org:8446

# Disk quota
rucio-admin -a root account set-limits root LIGO-CIT-HDFS 1000000000000

# Make this part of the LIGO lab network
rucio-admin rse set-attribute --rse LIGO-CIT-HDFS --key ligo_lab --value True
rucio-admin rse set-attribute --rse LIGO-CIT-HDFS --key hdfs --value True

