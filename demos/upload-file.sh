#!/bin/sh -e

# residuals frames
h1=/home/sudarshan.ghonge/Projects/TGR/GW150914/IMRPhenomPv2/residual_frame/H-H1_HOFT_RES-1126259454-16.gwf
l1=/home/sudarshan.ghonge/Projects/TGR/GW150914/IMRPhenomPv2/residual_frame/L-L1_HOFT_RES-1126259454-16.gwf

rucio -v upload \
    --summary \
    --scope RESIDUALS --rse LIGO-CIT \
    --protocol gsiftp \
    ${h1} ${l1}
  #--name H-H1_HOFT_C02-1137242112-4096.gwf\
  #--pfn gsiftp://ldas-pcdev2.ligo.caltech.edu:2811/home/jclark/Projects/ligo-rucio/data/TEST/test.gwf \
  #--no-register 
