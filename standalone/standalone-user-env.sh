#!/bin/sh
export RUCIO_SRC=/home/jclark/src/rucio
export RUCIO_HOME=${RUCIO_SRC}/etc/docker/standalone/files/rucio/
export FTS3_HOME=${RUCIO_SRC}/etc/docker/standalone/files/fts3/
export X509_CERT_DIR=${RUCIO_SRC}/etc/docker/standalone/files/grid-security/
export X509_USER_PROXY=/tmp/x509up_u$(id -u)
