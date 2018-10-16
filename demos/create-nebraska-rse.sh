#!/bin/sh -e

# Create RSE
rucio-admin rse add UNL

# Define copying protocol
rucio-admin rse add-protocol\
    --prefix  /user/ligo/rucio/evaluation \
    --hostname gsiftp://red-gridftp.unl.edu:2811\
    --domain-json '{"wan": {"read": 1, "write": 1, "delete": 1, "third_party_copy": 1}}' \
    --scheme gsiftp \
    --port 2811 \
    UNL


# Disk quota
rucio-admin -a root account set-limits root UNL 1000000000000


