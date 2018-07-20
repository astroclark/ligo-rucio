#!/bin/bash

rucio-admin rse add LIGOTESTCIT

rucio-admin rse add-protocol\
    --prefix /home/jclark/Projects/ligo-rucio \
    --domain-json '{"wan": {"read": 1, "write": 1, "delete": 1, "third_party_copy": 1}}' \
    --scheme gsiftp \
    --hostname ldas-pcdev2.ligo.caltech.edu\
    --port 2811 \
    LIGOTESTCIT
