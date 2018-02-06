#!/usr/bin/env python
#
# insert_lvc_dataset.py
#
# Copyright (C) 2018  James Alexander Clark <james.clark@ligo.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""
Command line tool to register LIGO/Virgo datasets into rucio.

Queries a datafind server to locate a list of local frame files of a given type
(e.g., H1_HOFT_C00) in some time span.

Rucio scope is determined by run (engineering/observing run).
"""


import os,sys
import warnings
import argparse
from pycbc.frame import frame_paths
#   import rucio.rse.rsemanager as rsemgr
#   from rucio.client.didclient import DIDClient
#   from rucio.client.replicaclient import ReplicaClient
#   from rucio.common.exception import DataIdentifierAlreadyExists
#   from rucio.common.exception import RucioException
#   from rucio.common.exception import FileAlreadyExists

from gfal2 import Gfal2Context, GError
from rucio.client.replicaclient import ReplicaClient
import rucio.rse.rsemanager as rsemgr

# FIXME: These times are non-exhaustive and inexact
DATA_RUNS={
        'ER8':(1123858817,1126623617),
        'O1':(1126623617,1137254417),
        'ER9':(1152136817,1152169157),
        'O2':(1164499217,1187654418)
        }

try:
    LIGO_DATAFIND_SERVER=os.environ['LIGO_DATAFIND_SERVER']
except:
    LIGO_DATAFIND_SERVER="datafind.ligo.org:443"

#   def rucio2ligo(dids):
#       """
#       Construct the expected path to frames, given a Rucio DID
#
#       Path should be <run>/<type>/<ifo>/<site>-<type>-<day>
#
#       E.g., ER8/H1_HOFT_C00/H1/H-H1_HOFT_C00-1126
#       """
#
#       if not hasattr(dids,"__iter__"):
#           dids = [dids]
#
#       frame_pfns = []
#       for did in dids:
#           run=did.split(":")[0]
#           name=did.split(":")[1]
#           ftype=name.split("-")[1]
#           ifo=ftype[0]
#           day=name.split('-')[2][:4]
#           frame_pfns.append(os.path.join(frame_path,run,ftype,ifo,day,name))
#       return frame_pfns

def parse_cmdline():

    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument("--rse", type=str, default=None, required=True,
            help="""Rucio storage element to host frames""")

    parser.add_argument("--dry-run", default=False, action="store_true",
            help="""Find frames, construct replica list but don't actually
            upload to rucio""") 

    parser.add_argument("--verbose", default=False, action="store_true",
            help="""Print extra info""")

    parser.add_argument("--gps-start-time", metavar="GPSSTART", type=int,
            help="GPS start time of segment (e.g., 1126259457)",
            required=True)

    parser.add_argument("--gps-end-time", metavar="GPSEND", type=int,
            help="GPS end time of segments (e.g., 1126259467)",
            required=True)

    parser.add_argument("--open-data", default=False, action="store_true",
            help="""Use the LIGO open science center (LOSC) data""",
            required=False)

    parser.add_argument("--ifo", type=str, default=None, required='--open-data'
            in sys.argv, help="""Interferometer label (e.g., H (LIGO Hanford), L
            (LIGO Livingston), V (Virgo), ...""")

    parser.add_argument("--frame-type", type=str, default=None,
            required='--open-data' not in sys.argv, help="""frame type (e.g.,
            H1_HOFT_C02. See e.g., https://dcc.ligo.org/LIGO-T010150/public)""")

    #parser.add_argument('--version', action='version', version=__version__)
    ap = parser.parse_args()

    return ap


class DatasetInjector(object):
    """
    General Class for injecting a LIGO dataset in rucio

    1) Find frames with gw_data_find
    2) Convert frame names to rucio DIDs
    3) Create Rucio dataset
    4) Register Rucio dataset
    """

    def __init__(self, start_time, end_time, frtype, site=None, rse=None,
            check=True, lifetime=None, dry_run=False, verbose=False):

        self.start_time = start_time
        self.end_time = end_time
        self.frtype = frtype
        self.verbose = verbose

        self.site = site

        if rse is None:
            rse = site
        self.rse = rse
        self.check = check
        self.lifetime = lifetime
        self.dry_run = dry_run

        self.gfal = Gfal2Context()

        # Locate frames
        frames = self.find_frames()

        # Create rucio names
        self.frames2rucio(frames)

    def find_frames(self):
        """
        Query the datafind server to find frame files matching time interval and
        frame type
        """

        # Datafind query
        if self.verbose:
            print "-------------------------"
            print "Querying datafind server:"
            print "Type: ", self.frtype
            print "Interval: [{0},{1})".format(self.start_time, self.end_time)

        frames = frame_paths(self.frtype, self.start_time, self.end_time,
                url_type='file', server=LIGO_DATAFIND_SERVER)

        if not hasattr(frames,"__iter__"):
            frames = [self.frames]

        if self.verbose:
            print "Query returned {0} frames in [{1},{2})".format(
                    len(frames), self.start_time, self.end_time)
            print "First frame: {}".format(frames[0])
            print "Last frame: {}".format(frames[-1])
            print "-------------------------"

        return frames

    def frames2rucio(self, frames):
        """
        Determine the Rucio DIDs for given frame URLs and add to a list of dictionaries
        """

        self.replicas = []
        for frame in frames:
            name = os.path.basename(frame)
            url = "file://"+frame

            size, checksum = self.check_storage(url)

            # Identify data run (scope)
            start = int(name.split('-')[2])
            for scope in DATA_RUNS:
                if DATA_RUNS[scope][0] <= start <= DATA_RUNS[scope][1]:
                    replica = {'scope':scope,
                            'name':name,
                            'bytes':size,
                            'adler32':checksum,
                            'pfn':url}
                    self.replicas.append(replica)
                    break
            else:
                warnstr=("Frame {frame} not in known data-gathering run. Setting"
                        " scope=AW".format(frame=name))
                warnings.warn(warnstr, Warning)


    def check_storage(self, url):
        """
        Check size and checksum of a file on storage
        """
        if self.verbose:
            print("checking url %s" % url)
        try:
            size = self.gfal.stat(str(url)).st_size
            checksum = self.gfal.checksum(str(url), 'adler32')
            if self.verbose:
                print("got size and checksum of file: pfn=%s size=%s checksum=%s"
                      % (url, size, checksum))
        except GError:
            print("no file found at %s" % url)
            return False
        return size, checksum


#########################################################################

def main():

    # Parse input
    ap = parse_cmdline()

    # XXX Testing area: tinker here then move to methods in DatasetInjector
    if ap.verbose:
        print "Finding RSE info:"
    rse_settings = rse_settingsmgr.get_rse_info(ap.rse)
    protocol = rse_settings['protocols'][0]

    schema=protocol['scheme']
    prefix=protocol['prefix']
#    prefix = proto['prefix'] + '/' + options.scope.replace('.', '/')
    port=protocol['port'] 
    hostname=protocol['hostname']

    if schema == 'srm':
        prefix = protocol['extended_attributes']['web_service_path'] + prefix
    url = schema + '://' + hostname
    if port != 0:
        url = url + ':' + str(port)
    url = url + prefix + '/' + "BLAH"

    print url

    sys.exit()

    # Find and create a data set
    dataset = DatasetInjector(ap.gps_start_time, ap.gps_end_time, ap.frame_type,
            verbose=ap.verbose)


    # XXX Testing area: tinker here then move to methods in DatasetInjector
    
    #
    # 1. Create the list of files to replicate
    #
    # --- This list is in dataset.replicas
    if ap.verbose:
        print "adding replicas to RSE"

    #replica_client.add_replicas(rse=ap.rse, files=dataset.replicas)

    #
    # 2. Register this list of replicas with a dataset
    #
    
    # -- We just need to attach each file to the dataset
    #
    # See e.g., attach_file in register() in cmsexample.py:

    # for filemd in block['files']:
    #     self.register_replica(filemd)
    #     self.attach_file(filemd['name'], block['name'])


if __name__ == "__main__":

    main()




