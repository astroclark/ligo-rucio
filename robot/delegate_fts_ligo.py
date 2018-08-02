#!/usr/bin/env python
"""cat /opt/rucio/delegate_fts.py"""
import commands
import os
import pprint
import requests
import sys
import time

from dateutil import parser


requests.packages.urllib3.disable_warnings()
PROXY = '/opt/rucio/ligo/robot-x509'

status, subject = commands.getstatusoutput('grid-proxy-info -file {} -subject'.format(PROXY))
if status:
    sys.exit(1)

print PROXY
print subject

FTS_SERVER = 'https://fts3-test.gridpp.rl.ac.uk:8446'
print FTS_SERVER

w = requests.get('%s/whoami' % FTS_SERVER, verify=False, cert=PROXY).json()
pprint.pprint(w)

b = requests.get('%s/delegation/%s' % (FTS_SERVER, w['delegation_id']), verify=False, cert=PROXY).json()
pprint.pprint(b)
bt = parser.parse('1970-01-01 00:00:01')
if b is not None:
    bt = parser.parse(b['termination_time'])
at = parser.parse('1970-01-01 00:00:00')


while at < bt:
    with open('/tmp/fts3request_rfc.pem', 'w') as fd:
        fd.write(requests.get('%s/delegation/%s/request' % (FTS_SERVER, w['delegation_id']), verify=False, cert=PROXY).text)

    commands.getstatusoutput('/bin/echo -n > /etc/pki/CA/index.txt')
    commands.getstatusoutput('/bin/echo "00" > /etc/pki/CA/serial')
    commands.getstatusoutput('/usr/bin/printf "[rfc_voms]\nkeyUsage=critical,digitalSignature,keyEncipherment,keyAgreement\nproxyCertInfo = critical,language:Inherit all\n" > /tmp/rfc_voms_extensions')
    commands.getstatusoutput('/usr/bin/openssl ca -in /tmp/fts3request_rfc.pem -preserveDN -days 365 -cert %s -keyfile %s -md sha256 -out /tmp/fts3proxy_rfc.pem -subj "%s" -policy policy_anything -batch -extensions rfc_voms -extfile /tmp/rfc_voms_extensions' % (PROXY, PROXY, subject))
    commands.getstatusoutput('/bin/cat /tmp/fts3proxy_rfc.pem %s > /tmp/fts3full_rfc.pem' % PROXY)

    print requests.put('%s/delegation/%s/credential' % (FTS_SERVER, w['delegation_id']), verify=False, cert=PROXY, data=open('/tmp/fts3full_rfc.pem', 'r')).text
    a = requests.get('%s/delegation/%s' % (FTS_SERVER, w['delegation_id']), verify=False, cert=PROXY).json()
    pprint.pprint(a)
    if a is not None:
        at = parser.parse(a['termination_time'])

    os.unlink('/tmp/fts3request_rfc.pem')
    os.unlink('/tmp/fts3proxy_rfc.pem')
    os.unlink('/tmp/fts3full_rfc.pem')

    if at < bt:
        print 'retrying'
        time.sleep(1)
