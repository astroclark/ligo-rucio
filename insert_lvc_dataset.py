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
from rucio.client.didclient import DIDClient
from rucio.client.replicaclient import ReplicaClient
from rucio.common.exception import DataIdentifierAlreadyExists
from rucio.common.exception import RucioException
from rucio.common.exception import FileAlreadyExists

from gfal2 import Gfal2Context, GError
from rucio.client.replicaclient import ReplicaClient
import rucio.rse.rsemanager as rsemgr


def parse_cmdline():

    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument("--dataset_name", type=str, default=None, required=True,
            help="""Dataset name""")

    parser.add_argument("--rse", type=str, default=None, required=True,
            help="""Rucio storage element to host frames""")

    parser.add_argument("--dry-run", default=False, action="store_true",
            help="""Find frames, construct replica list but don't actually
            upload to rucio""") 

    parser.add_argument("--verbose", default=False, action="store_true",
            help="""Print extra info""")

    parser.add_argument("--scope", type=str, default=None, required=False,
            help="""Scope of the dataset (default: data run corresponding to
            requested times""")

    parser.add_argument("--lifetime", type=float, default=100, required=False,
            help="""Dataset lifetime in seconds (default=100 for testing)""")

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

    parser.add_argument("--datafind-server", type=str, default=None,
            required=False, help="""datafind server to find frames on.  Use
            datafind.ligo.org:443 for /cvmfs frames (defaults to whatever is in
            ${LIGO_DATAFIND_SERVER})""")

    ap = parser.parse_args()

    return ap

def get_scope(start_time, end_time):
    """
    Determine scope for given GPS times
    """

    # FIXME: These times are non-exhaustive and inexact/unverified
    DATA_RUNS={
            'ER8':(1123858817,1126623617),
            'O1':(1126623617,1137254417),
            'ER9':(1152136817,1152169157),
            'O2':(1164499217,1187654418)
            }

    # FIXME: What if times span multiple runs?? 
    for scope in DATA_RUNS:
        if DATA_RUNS[scope][0] <= start_time <= DATA_RUNS[scope][1]:
            return scope
    else:
        warnstr=("Requested time ({}) not in known data-gathering run. Setting"
                " scope=AW (astrowatch)".format(start_time))
        warnings.warn(warnstr, Warning)
        return "AW"



class DatasetInjector(object):
    """
    General Class for injecting a LIGO dataset in rucio

    1) Find frames with gw_data_find
    2) Convert frame names to rucio DIDs
    3) Create Rucio dataset
    4) Register Rucio dataset
    """

    def __init__(self, dataset_name, start_time, end_time, frtype,
            datafind_server=None, scope=None, site=None, rse=None, check=True,
            lifetime=None, dry_run=False, verbose=False):

        if datafind_server is None:
            # If undefined, use default from environment
            try:
                self.LIGO_DATAFIND_SERVER=os.environ['LIGO_DATAFIND_SERVER']
                # If no datafind server in env, use cvmfs server
            except:
                self.LIGO_DATAFIND_SERVER="datafind.ligo.org:443"
        else:
            self.LIGO_DATAFIND_SERVER=datafind_server

        self.dataset_name = dataset_name
        self.start_time = start_time
        self.end_time = end_time
        self.frtype = frtype
        self.verbose = verbose


        if self.verbose: print "Attempting to determine scope from GPS time"
        if scope is None:
            self.scope = get_scope(start_time, end_time)
        else:
            self.scope=scope
        if self.verbose: print "Scope: {}".format(self.scope)

        self.site = site

        if rse is None:
            rse = site
        self.rse = rse
        self.check = check
        self.lifetime = lifetime
        self.dry_run = dry_run

        # Initialization for dataset
        self.get_global_url()
        self.did_client = DIDClient()
        self.rep_client = ReplicaClient()

        self.gfal = Gfal2Context()

        # Locate frames
        frames = self.find_frames()

        # Create rucio names -- this should probably come from the lfn2pfn
        # algorithm, not me
        self.list_replicas(frames)


    def find_frames(self):
        """
        Query the datafind server to find frame files matching time interval and
        frame type
        """

        # Datafind query
        if self.verbose:
            print "-------------------------"
            print "Querying datafind server:{}".format(
                    self.LIGO_DATAFIND_SERVER)
            print "Type: ", self.frtype
            print "Interval: [{0},{1})".format(self.start_time, self.end_time)

        frames = frame_paths(self.frtype, self.start_time, self.end_time,
                url_type='file', server=self.LIGO_DATAFIND_SERVER)

        if not hasattr(frames,"__iter__"):
            frames = [self.frames]

        if self.verbose:
            print "Query returned {0} frames in [{1},{2})".format(
                    len(frames), self.start_time, self.end_time)
            print "First frame: {}".format(frames[0])
            print "Last frame: {}".format(frames[-1])
            print "-------------------------"

        return frames

    def list_replicas(self, frames):
        """
        Construct a list of file replicas with the following properties:

        :param rse: the RSE name.
        :param scope: The scope of the file.
        :param name: The name of the file.
        :param bytes: The size in bytes.
        :param adler32: adler32 checksum.
        :param pfn: PFN of the file for non deterministic RSE.
        :param md5: md5 checksum.
        :param meta: Metadata attributes.

        """

        self.replicas = []
        for frame in frames:

            base_name = os.path.basename(frame)
            name = base_name
            directory = os.path.dirname(frame)

            size, checksum = self.check_storage("file://"+frame)

            url = self.url + '/' + name

            replica = {
                    'rse':self.rse,
                    'scope':self.scope,
                    'name':name,
                    'bytes':size,
                    'filename':base_name,
                    'adler32':checksum}
#                            'pfn':url}
            self.replicas.append(replica)



    def get_global_url(self):
        """
        Return the base path of the rucio url
        """
        # FIXME: this should probably interface with the LIGO lfn2pfn algorithm 
        if self.verbose:
            print("Getting parameters for rse %s" % self.rse)

        rse_settings = rsemgr.get_rse_info(self.rse)
        protocol = rse_settings['protocols'][0]

        schema=protocol['scheme']
        prefix=protocol['prefix']
        port=protocol['port'] 
        hostname=protocol['hostname']

        if schema == 'srm':
            prefix = protocol['extended_attributes']['web_service_path'] + prefix
        url = schema + '://' + hostname
        if port != 0:
            url = url + ':' + str(port)
        self.url = url + prefix 

        if self.verbose:
            print("Determined base url %s" % self.url)


    def check_storage(self, filepath):
        """
        Check size and checksum of a file on storage
        """
        if self.verbose:
            print("Checking url %s" % filepath)
        try:
            size = self.gfal.stat(str(filepath)).st_size
            checksum = self.gfal.checksum(str(filepath), 'adler32')
            if self.verbose:
                print("Got size and checksum of file: %s size=%s checksum=%s"
                      % (filepath, size, checksum))
        except GError:
            print("no file found at %s" % filepath)
            return False
        return size, checksum


#########################################################################

def main():

    # Parse input
    ap = parse_cmdline()

    #
    # 1. Create the list of files to replicate
    #
    dataset = DatasetInjector(ap.dataset_name, 
            ap.gps_start_time, ap.gps_end_time, ap.frame_type, 
            datafind_server=ap.datafind_server,
            scope=ap.scope, rse=ap.rse, lifetime=ap.lifetime,
            verbose=ap.verbose)


    # XXX Testing area: tinker here then move to methods in DatasetInjector

    # Recipe:
    #   a) create and register a dataset in the RSE
    #   b) register file replicas with the RSE
    #   c) attach files to the dataset
    
    #
    # 2. Create and register the dataset object
    #
    try:
        dataset.did_client.add_dataset(scope=dataset.scope,
                name=dataset.dataset_name, lifetime=dataset.lifetime,
                rse=dataset.rse)
        if ap.verbose:
            print("Creating dataset {}".format(dataset.dataset_name))
    except DataIdentifierAlreadyExists:
        if ap.verbose:
            print("Dataset {} already exists".format(dataset.dataset_name))


    #
    # 3. Register files for replication
    #

    # XXX: find the code i used to upload that 1 frame
    if ap.verbose:
        print("Registering file replicas")
    for replica in dataset.replicas:

        if ap.verbose:
            print("------")
            print("registering {}".format(replica['name']))

        print replica['rse']
        print replica['scope']
        print replica['name']
        print replica['adler32']
        print replica['bytes']
#        print replica['pfn']

#       rep_client.add_replicas(rse=dataset.rse, files=[{
#                       'scope': self.scope,
#                       'name': filemd['name'],
#                       'adler32': filemd['checksum'],
#                       'bytes': filemd['size'],
#                       'pfn': self.get_file_url(filemd['name'])
#                   }])


    #
    # 4. Attach replicas to the dataset
    #

#       dataset.did_client.attach_dids(scope=dataset.scope,
#               name=dataset.dataset_name, 
#               dids=[{'scope': dataset.scope, 'name': lfn}])
#

    #
    # 3. Attach files to dataset
    #


if __name__ == "__main__":

    main()




