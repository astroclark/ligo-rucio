#!/bin/sh -e


# Redefine copying protocol
rucio-admin rse delete-protocol \
    --hostname ldas-pcdev2-wa.ligo.caltech.edu\
    --scheme gsiftp \
    LIGO-WA-HDFS


# Redefine copying protocol
rucio-admin rse add-protocol \
    --prefix /hdfs/rucio \
    --hostname ldas-pcdev2.ligo-wa.caltech.edu\
    --domain-json '{"wan": {"read": 1, "write": 1, "delete": 1, "third_party_copy": 1}}' \
    --scheme gsiftp \
    --port 2811 \
    LIGO-WA-HDFS
