#!/bin/sh -e

# Create RSE
rucio-admin rse add TEST-LIGO-CIT 

# Define copying protocol
rucio-admin rse add-protocol\
    --prefix  /mnt/rucio/tests \
    --hostname ldas-pcdev6.ligo.caltech.edu \
    --domain-json '{"wan": {"read": 1, "write": 1, "delete": 1, "third_party_copy": 1}}' \
    --scheme gsiftp \
    --port 2811 \
    TEST-LIGO-CIT


# Disk quota
rucio-admin account set-limits root TEST-LIGO-CIT 1000000000000


