#!/bin/sh -e
rucio -v upload \
  --scope TEST --rse LIGO-CIT \
  --name H-H1_HOFT_C02-1137242112-4096.gwf\
  --protocol gsiftp \
  /home/jclark/Projects/ligo-rucio/data/TEST/hoft_C02/H1/H-H1_HOFT_C02-11372/H-H1_HOFT_C02-1137242112-4096.gwf
  #--pfn gsiftp://ldas-pcdev2.ligo.caltech.edu:2811/home/jclark/Projects/ligo-rucio/data/TEST/test.gwf \
  #--no-register 
