#!/bin/sh
source ${HOME}/virtualenvs/ligo-rucio/bin/activate
export RUCIO_HOME=/home/jclark/Projects/ligo-rucio/client
export RUCIO_ACCOUNT=jclark
ligo-proxy-init james.clark
export X509_USER_PROXY=$(grid-proxy-info -path)
