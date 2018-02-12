#!/bin/bash
export RUCIO_HOME=${PWD}
./insert_lvc_dataset.py \
    --dataset H1_HOFT_C02-1126259457_1126259467 \
    --scope ER8 \
    --datafind-server datafind.ligo.org:443 \
    --rse LIGOTEST \
    --verbose \
    --gps-start-time 1126259457 \
    --gps-end-time 1126259467 \
    --frame-type H1_HOFT_C02
