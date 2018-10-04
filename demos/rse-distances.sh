#/bin/sh -e
rucio-admin rse add-distance --distance 1 --ranking 1 LIGO-CIT LIGO-WA
rucio-admin rse add-distance --distance 1 --ranking 1 LIGO-WA LIGO-CIT
rucio-admin rse add-distance --distance 1 --ranking 1 LIGO-CIT-ARCHIVE LIGO-WA
rucio-admin rse add-distance --distance 1 --ranking 1 LIGO-WA LIGO-CIT-ARCHIVE
rucio-admin rse add-distance --distance 1 --ranking 1 LIGO-CIT LIGO-CIT-ARCHIVE
rucio-admin rse add-distance --distance 1 --ranking 1 LIGO-CIT-ARCHIVE LIGO-CIT

