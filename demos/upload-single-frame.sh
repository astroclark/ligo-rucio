#!/bin/bash
RUCIO_ACCOUNT=jclark rucio -v upload \
    /hdfs/frames/ER8/hoft_C02/H1/H-H1_HOFT_C02-11262/H-H1_HOFT_C02-1126256640-4096.gwf \
    --rse LIGOTEST --scope ER8 \
    --name H-H1_HOFT_C02-1126256640-4096.gwf
