#!/bin/bash

#DOCKERIMAGE=gitlab-registry.cern.ch/rucio01/rucio/mysql_server 
DOCKERIMAGE=rucio/rucio-server:release-1.16.1

docker run --privileged \
    --name rucio-server \
    -v /etc/hostname:/etc/hostname -v \
    /var/log/httpd:/var/log/httpd -v \
    /etc/grid-security/hostcert.pem:/etc/grid-security/hostcert.pem \
    -v /etc/grid-security/hostkey.pem:/etc/grid-security/hostkey.pem \
    -v /sys/fs/cgroup:/sys/fs/cgroup:ro -v /opt/rucio/etc:/opt/rucio/etc \
    -v /etc/grid-security:/etc/grid-security -v /etc/pki:/etc/pki \
    -d -p 443:443 ${DOCKERIMAGE}

