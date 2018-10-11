#!/bin/sh -e

# Create RSE
rucio-admin rse add LIGO-CIT-ARCHIVE

# Define copying protocol
#rucio-admin rse delete-protocol --scheme gsiftp  LIGO-CIT-ARCHIVE 
rucio-admin rse add-protocol\
    --prefix /hdfs/frames \
    --hostname ldas-pcdev5.ligo.caltech.edu\
    --domain-json '{"wan": {"read": 1, "write": 0, "delete": 0, "third_party_copy": 1}}' \
    --scheme gsiftp \
    --port 2811 \
    LIGO-CIT-ARCHIVE


# Disk quota
rucio-admin -a root account set-limits root LIGO-CIT-ARCHIVE 1000000000000
