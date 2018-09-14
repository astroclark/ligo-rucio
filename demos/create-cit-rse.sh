#!/bin/sh -e

# Create RSE
rucio-admin rse add LIGO-CIT

# Define copying protocol
rucio-admin rse add-protocol\
    --prefix /home/rucio \
    --hostname ldas-pcdev2.ligo.caltech.edu\
    --domain-json '{"wan": {"read": 1, "write": 1, "delete": 1, "third_party_copy": 1}}' \
    --scheme gsiftp \
    --port 2811 \
    LIGO-CIT


# FTS configuration
rucio-admin rse set-attribute --rse LIGO-CIT --key fts --value https://fts.mwt2.org:8446
rucio-admin rse set-attribute --rse LIGO-CIT --key fts_testing --value https://fts.mwt2.org:8446

# Disk quota
rucio-admin -a root account set-limits root LIGO-CIT 1000000000000

# Make this part of the LIGO lab network
rucio-admin rse set-attribute --rse LIGO-CIT --key ligo_lab --value True

