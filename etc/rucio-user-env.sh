export RUCIO_HOME=/home/jclark/Projects/ligo-rucio
export RUCIO_ACCOUNT=root
source /home/jclark/opt/lscsoft/pycbc/etc/pycbc-user-env.sh
source /home/jclark/opt/lscsoft/pycbc-glue/etc/glue-user-env.sh
export PYTHONPATH=${PYTHONPATH}:${RUCIO_HOME}/lib
