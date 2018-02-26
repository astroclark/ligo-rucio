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
import logging
import time
import warnings
import multiprocessing
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

MAXTHREADS=multiprocessing.cpu_count()

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
            help="""Print all logging info""")

    parser.add_argument("--debug", default=False, action="store_true",
            help="""Print debug logging info""")

    parser.add_argument("--log-file", type=str,
            default=os.path.basename(__file__).replace('py','log'),
            help="""Direct logging information to this file""")

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

    parser.add_argument("--disable-multiprocessing", default=False,
            action="store_true", help="""Disable multiprocessing""")

    parser.add_argument("--nprocs", metavar="nprocs", type=int,
            help="""Number of processes to launch to retrieve LFN
            information""", default=MAXTHREADS)

    ap = parser.parse_args()

    return ap

def get_scope(start_time, end_time):
    """
    Determine scope for given GPS times

    See e.g., https://wiki.ligo.org/LSC/JRPComm/EngineeringRuns
    """

    # FIXME: These times are non-exhaustive and inexact/unverified
    DATA_RUNS={
            'ER8':(1123858817,1126623617),
            'O1':(1126623617,1134057617),
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

def unwrap_file_dict(arg, **kwarg):
    """
    External call to DatasetInjector method to permit multiprocessing
    """
    return DatasetInjector._file_dict(*arg, **kwarg)

def check_storage(filepath):
    """
    Check size and checksum of a file on storage
    """
    # FIXME: Gfal2Context cannot be pickled so we have to instantiate here to
    # use multiprocessing()
    gfal = Gfal2Context()
    logging.info("Checking url %s" % filepath)
    try:
        size = gfal.stat(str(filepath)).st_size
        checksum = gfal.checksum(str(filepath), 'adler32')
        logging.info("Got size and checksum of file: %s size=%s checksum=%s"
                % (filepath, size, checksum))
    except GError:
        logging.warning("no file found at %s" % filepath)
        return False
    return size, checksum

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
            lifetime=None, dry_run=False, no_multiprocs=False,
            nprocs=MAXTHREADS):

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
        self.no_multiprocs = no_multiprocs

        logging.info("Attempting to determine scope from GPS time")
        if scope is None:
            self.scope = get_scope(start_time, end_time)
        else:
            self.scope=scope
        logging.info("Scope: {}".format(self.scope))

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

        # Locate frames
        frames = self.find_frames()

        if dry_run:
            logging.info("Dry run: ending process before constructing replica list")
            sys.exit(0)

        # Create rucio names -- this should probably come from the lfn2pfn
        # algorithm, not me
        self.list_files(frames, nprocs=nprocs)


    def find_frames(self):
        """
        Query the datafind server to find frame files matching time interval and
        frame type
        """

        # Datafind query
        logging.info("Querying datafind server:{}".format(self.LIGO_DATAFIND_SERVER))
        logging.info("Type: {}".format(self.frtype))
        logging.info("Interval: [{0},{1})".format(self.start_time,
            self.end_time))

        frames = frame_paths(self.frtype, self.start_time, self.end_time,
                url_type='file', server=self.LIGO_DATAFIND_SERVER)

        if not hasattr(frames,"__iter__"):
            frames = [self.frames]

        logging.info("Query returned {0} frames in [{1},{2})".format(
            len(frames), self.start_time, self.end_time))
        logging.info("First frame: {}".format(frames[0]))
        logging.info("Last frame: {}".format(frames[-1]))

        return frames


    def list_files(self, frames, nprocs):
        """
        Construct a list of files with the following dictionary keys:

        :param rse: the RSE name.
        :param scope: The scope of the file.
        :param name: The name of the file.
        :param bytes: The size in bytes.
        :param adler32: adler32 checksum.
        :param pfn: PFN of the file for non deterministic RSE.
        :param md5: md5 checksum.
        :param meta: Metadata attributes.

        """
        logging.info("Constructing rucio file list")

        if self.no_multiprocs:
            logging.warning("Multiprocessing disabled")
            self.files = map(unwrap_file_dict, zip([self]*len(frames),frames))
        else:
            logging.info("Using multi-process pool with {} processes".format(nprocs))
            pool = multiprocessing.Pool(processes=nprocs)
            self.files = pool.map(unwrap_file_dict, zip([self]*len(frames),frames))
        

    def _file_dict(self, frame):
        """
        Create a dictionary with LFN properties
        """

        basename = os.path.basename(frame)
        name = basename
        directory = os.path.dirname(frame)

        size, checksum = check_storage("file://"+frame)
        url = os.path.join(self.global_url, basename)

        return {
                'rse':self.rse,
                'scope':self.scope,
                'name':name,
                'bytes':size,
                'filename':basename,
                'adler32':checksum}#,
                #'pfn':url}


    def get_global_url(self):
        """
        Return the base path of the rucio url
        """

        logging.info("Getting parameters for rse %s" % self.rse)

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
        self.global_url = url + prefix 

        logging.info("Determined base url %s" % self.global_url)


#########################################################################

def main():

    # Parse input
    ap = parse_cmdline()

    #logging.getLogger().addHandler(logging.StreamHandler())

    if ap.verbose: logging.basicConfig(level=logging.INFO)
    if ap.debug: logging.basicConfig(level=logging.DEBUG)

    logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
    rootLogger = logging.getLogger()

    fileHandler = logging.FileHandler(ap.log_file)
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)

    logging.info("Aquiring rucio configuration")

    global_start=time.time()
    #
    # 1. Create the list of files to replicate
    #
    start_time = time.time()
    dataset = DatasetInjector(ap.dataset_name, 
            ap.gps_start_time, ap.gps_end_time, ap.frame_type, 
            datafind_server=ap.datafind_server,
            scope=ap.scope, rse=ap.rse, lifetime=ap.lifetime,
            no_multiprocs=ap.disable_multiprocessing,
            dry_run=ap.dry_run)

    logging.info("File identification/verification took {:.2} mins".format(
        (time.time()-start_time)/60.))

    # Recipe:
    #   a) create and register a dataset in the RSE
    #   b) register file replicas with the RSE
    #   c) attach files to the dataset
    
    #
    # 2. Create and register the dataset object
    #
    start_time=time.time()
    try:
        logging.info("Registering dataset {}\n".format(dataset.dataset_name))
        dataset.did_client.add_dataset(scope=dataset.scope,
                name=dataset.dataset_name, lifetime=dataset.lifetime,
                rse=dataset.rse)
    except DataIdentifierAlreadyExists:
        logging.warning("Dataset {} already exists".format(dataset.dataset_name))

    try:
        logging.info("attaching dataset {}".format(dataset.dataset_name))
        dataset.did_client.attach_dids(scope=dataset.scope,
                name=dataset.dataset_name, dids=[{'scope': dataset.scope,
                    'name': dataset.dataset_name}])
    except RucioException:
        logging.warning(" Dataset already attached")

    logging.info("Dataset registration took {:.2} mins".format(
        (time.time()-start_time)/60.))


    #
    # 3. Register files for replication
    #
    logging.info("Registering file replicas")

    start_time = time.time()
    for filemd in dataset.files:

        logging.info("Registering {}".format(filemd['name']))

        # --- Check if a replica of the given file at the site already exists.
        logging.info("checking if file %s with scope %s has already a replica at %s"
              % (filemd['name'], filemd['scope'], dataset.rse))

        existing_replicas = list(dataset.rep_client.list_replicas([{'scope':
            filemd['scope'], 'name': filemd['name']}]))

        if existing_replicas:
            existing_replicas = existing_replicas[0]
            if 'rses' in existing_replicas:
                if dataset.rse in existing_replicas['rses']:
                    logging.warning("File %s with scope %s has already a replica at %s"
                          % (filemd['name'], dataset.scope, dataset.rse))
        else:
            # Register replica
            if dataset.rep_client.add_replicas(rse=dataset.rse, 
                    files=[{
                        'scope': dataset.scope,
                        'name': filemd['name'],
                        'adler32': filemd['adler32'],
                        'bytes': filemd['bytes']}]):

                        # PFN is determined on its own
                        #'pfn': replica['pfn']}]):

                logging.info("File {} registered".format(filemd['name']))
            else:
                logging.warning("File {} registration failed".format(filemd['name']))

        # End check

        #
        # 4. Attach replicas to the dataset
        #
        try:
            logging.info("Attaching file {0} to datset {1}".format(filemd['name'],
                dataset.dataset_name))
            dataset.did_client.attach_dids(scope=dataset.scope,
                    name=dataset.dataset_name, 
                    dids=[{'scope': dataset.scope, 'name': filemd['name']}])

        except FileAlreadyExists:
            logging.warning("File already exists")

        logging.info("File replica registration took {:.2} mins".format(
        (time.time()-start_time)/60.))

    logging.info("Data replication process complete!")
    logging.info("Total time elapsed: {:.2f} mins".format(
        (time.time()-global_start)/60.))

if __name__ == "__main__":

    main()




