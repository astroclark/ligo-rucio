#!/bin/sh -e

rucio-admin rse add LIGO-CIT

rucio-admin rse add-protocol\
    --prefix /home/jclark/Projects/ligo-rucio/data \
    --domain-json '{"wan": {"read": 1, "write": 1, "delete": 1, "third_party_copy": 1}}' \
    --scheme gsiftp \
    --hostname ldas-pcdev2.ligo.caltech.edu\
    --port 2811 \
    LIGO-CIT
