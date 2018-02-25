#!/bin/bash
export RUCIO_HOME=${PWD}
export RUCIO_ACCOUNT=root

start_time=1126259457
end_time=$((${start_time}+5000))

./insert_lvc_dataset.py \
    --dataset H1_HOFT_C02-${start_time}_${end_time} \
    --scope ER8 \
    --datafind-server datafind.ligo.org:443 \
    --rse LIGOTEST \
    --verbose \
    --gps-start-time ${start_time} \
    --gps-end-time ${end_time} \
    --frame-type H1_HOFT_C02
