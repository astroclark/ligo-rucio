#/bin/sh -e
rucio-admin rse add-distance --distance 1 --ranking 1 LIGO-CIT LIGO-LHO
rucio-admin rse add-distance --distance 1 --ranking 1 LIGO-LHO LIGO-CIT
rucio-admin rse add-distance --distance 1 --ranking 1 LIGO-CIT-ARCHIVE LIGO-LHO
rucio-admin rse add-distance --distance 1 --ranking 1 LIGO-LHO LIGO-CIT-ARCHIVE
rucio-admin rse add-distance --distance 1 --ranking 1 LIGO-CIT LIGO-CIT-ARCHIVE
rucio-admin rse add-distance --distance 1 --ranking 1 LIGO-CIT-ARCHIVE LIGO-CIT

