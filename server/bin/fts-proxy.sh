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
ftsdelegate=/bin/fts-rest-delegate
ftsserver=https://fts.mwt2.org:8446

## Logging info
dtstamp="`date +%F-%A-%H.%M.%S `"
echo -e "\n\n---- ${dtstamp} ----" >> ${ftsproxylog}

## Create robot proxy
#${proxytool} -cert ${hostcert} -key ${hostkey} -out  ${x509proxy} -debug >> ${ftsproxylog} 2>&1

## Temporary: Use LIGO user proxy. Send a reminder mail if this is about to expire
proxytimeleft=$(grid-proxy-info -f ${x509proxy} -timeleft)
proxytimelefthour=$(python -c 'print "%.1f" % (float('${proxytimeleft}')/3600.0)')
echo "Proxy valid for ${proxytimelefthour} hours" >> ${ftsproxylog} 2>&1
if (( proxytimeleft < 3600 ))
  then
    echo "Proxy valid <  1 Hour, emailing a reminder" >> ${ftsproxylog} 2>&1
    ligo-proxy-init james.clark
    echo -e "Subject: [rucio] Refresh Proxy\nRegenerate your x509 user proxy on rucio.ligo.caltech.edu (in ${x509proxy})" > /tmp/email.txt
    sendmail james.clark@ligo.org < /tmp/email.txt
    rm /tmp/email.txt
  else
    echo "Proxy valid > 1 Hour, no renewal necessary" >> ${ftsproxylog} 2>&1
fi

## Delgate proxy
echo "Delegating: " >> ${ftsproxylog} 2>&1
echo "${ftsdelegate} -v -s ${ftsserver} --cert ${x509proxy} --key ${x509proxy}"  >> ${ftsproxylog} 2>&1
${ftsdelegate} -v -s ${ftsserver} --cert ${x509proxy} --key ${x509proxy}  >> ${ftsproxylog} 2>&1

