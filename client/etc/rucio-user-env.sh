#!/bin/sh
# source /home/jclark/opt/lscsoft/pycbc/etc/pycbc-user-env.sh
# source /home/jclark/opt/lscsoft/pycbc-glue/etc/glue-user-env.sh
source ${HOME}/virtualenvs/ligo-rucio/bin/activate
export RUCIO_HOME=/home/jclark/Projects/ligo-rucio/client
export RUCIO_ACCOUNT=jclark
export PYTHONPATH=/home/jclark/Projects/ligo-rucio/ligo_lfn2pfn:${PYTHONPATH}
