#/bin/sh -e
rucio-admin rse add-distance --distance 1 --ranking 1 LIGO-CIT LIGO-WA
rucio-admin rse add-distance --distance 1 --ranking 1 LIGO-WA LIGO-CIT

