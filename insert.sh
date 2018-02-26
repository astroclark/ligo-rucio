#!/bin/bash
export RUCIO_HOME=${PWD}
export RUCIO_ACCOUNT=root

# Get current pycbc
source ${PWD}/etc/rucio-user-env.sh

# Times taken from:
# https://wiki.ligo.org/LSC/JRPComm/EngRun8

start_time=1126623617 # start of O1 
#end_time=$((${start_time}+5000))
end_time=1134057617 # end of O1

./insert_lvc_dataset.py \
    --log-file H1_HOFT_C02-${start_time}_${end_time}.log \
    --dataset H1_HOFT_C02-${start_time}_${end_time} \
    --scope O1 \
    --datafind-server datafind.ligo.org:443 \
    --rse LIGOTEST \
    --debug \
    --gps-start-time ${start_time} \
    --gps-end-time ${end_time} \
    --frame-type H1_HOFT_C02
