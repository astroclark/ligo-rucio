#!/bin/bash
export RUCIO_HOME=${PWD}
./insert_lvc_dataset.py \
    --rse LIGOTEST \
    --verbose \
    --gps-start-time 1126259457 \
    --gps-end-time 1126259467 \
    --frame-type H1_HOFT_C02
