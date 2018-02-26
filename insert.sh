#!/bin/bash
export RUCIO_HOME=${PWD}
export RUCIO_ACCOUNT=root

# Times taken from:
# https://wiki.ligo.org/LSC/JRPComm/EngRun8

start_time=1126623617 # start of O1 
#end_time=$((${start_time}+5000))
end_time=1134057617

./insert_lvc_dataset.py \
    --dry-run
    --dataset H1_HOFT_C02-${start_time}_${end_time} \
    --scope ER8 \
    --datafind-server datafind.ligo.org:443 \
    --rse LIGOTEST \
    --debug \
    --gps-start-time ${start_time} \
    --gps-end-time ${end_time} \
    --frame-type H1_HOFT_C02
