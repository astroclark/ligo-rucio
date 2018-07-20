#!/bin/sh
#source ./standalone-user-env.sh
docker-compose --file ${RUCIO_SRC}/etc/docker/standalone/docker-compose.yml up -d
