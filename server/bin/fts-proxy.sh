#!/bin/sh -e
#
# fts-proxy.sh
#
# james alexander clark <james.clark@.ligo.org>
#
# Create an x509 proxy from the host's igtf grid certificate and delegate
# against the osg fts server at https://fts.mwt2.org:8446.  Run this script (as
# root) as a cronjob to maintain an FTS-delegated proxy for rucio operations.
#
## Configuration
ftsproxylog=/var/log/rucio/fts-proxy.log
proxytool=/usr/bin/grid-proxy-init
hostcert=/etc/grid-security/hostcert.pem
hostkey=/etc/grid-security/hostkey.pem
x509proxy=/opt/rucio/etc/web/x509up
ftsdelegate=/usr/bin/fts-delegation-init
ftsserver=https://fts.mwt2.org:8446

## Logging info
dtstamp="`date +%F-%A-%H.%M.%S `"
echo -e "\n\n---- ${dtstamp} ----" >> ${ftsproxylog}

## Create proxy
${proxytool} -cert ${hostcert} -key ${hostkey} -out  ${x509proxy} -debug >> ${ftsproxylog} 2>&1

## Delgate proxy
${ftsdelegate} -v -s ${ftsserver} --proxy ${x509proxy} >> ${ftsproxylog} 2>&1
