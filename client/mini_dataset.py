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
import argparse
from rucio.client.didclient import DIDClient
from rucio.client.replicaclient import ReplicaClient
from rucio.common.exception import DataIdentifierAlreadyExists
from rucio.common.exception import RucioException
from rucio.common.exception import FileAlreadyExists
from rucio.common.utils import adler32, md5

from rucio.client.replicaclient import ReplicaClient
import rucio.rse.rsemanager as rsemgr
import ligo_lfn2pfn


def parse_cmdline():

    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument("--dataset-name", type=str, default=None, required=True,
            help="""Dataset name""")

    parser.add_argument("--scope", type=str, default="TEST", required=False,
            help="""Scope of the dataset (default: data run corresponding to
            requested times""")

    parser.add_argument("--lifetime", type=float, default=3600, required=False,
            help="""Dataset lifetime in seconds (default=3600 for testing)""")

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


    parser.add_argument("--file-list", type=str, default=None,
            required=True, help="""A text file with a list of files for this dataset""")

    ap = parser.parse_args()

    return ap


def unwrap_file_dict(arg, **kwarg):
    """
    External call to DatasetInjector method to permit multiprocessing
    """
    return DatasetInjector._file_dict(*arg, **kwarg)


def check_storage(filepath):
    """
    Check size and checksum of a file on storage
    """
    logging.info("Checking %s" % filepath)
    try:
        size = os.stat(filepath).st_size
        adler_checksum = adler32(filepath)
        md5_checksum = md5(filepath)

        # FIXME: some frames have len(adler_checksum)=7, is there a better way to
        # force len(adler_checksum)=8 than prepending a zero manually?
        if len(adler_checksum)!=8: adler_checksum="0{}".format(adler_checksum)
        logging.info("Got size and checksum of file: %s size=%s adler32 checksum=%s md5 checksum=%s"
                % (filepath, size, adler_checksum, md5_checksum))
    except:
        logging.warning("no file found at %s" % filepath)
        return False
    return size, adler_checksum, md5_checksum

class DatasetInjector(object):
    """
    General Class for injecting a LIGO dataset in rucio

    1) Load list of files for dataset from text file
    2) Get their checksums
    2) Convert frame names to rucio DIDs
    3) Create Rucio dataset
    4) Register Rucio dataset
    """

    def __init__(self, filelist=None, dataset_name=None, scope=None, rse=None,
                 lifetime=None):

        self.dataset_name = dataset_name
        self.filelist = filelist
        self.rse = rse
        self.lifetime = lifetime

        # Initialization for dataset
        self.get_global_url()
        self.did_client = DIDClient()
        self.rep_client = ReplicaClient()

        # Locate frames
        frames = self.find_frames()

        # Create list of rucio replicas
        self.list_files(frames, nprocs=nprocs)

        print self.files
        sys.exit()


    def find_frames(self):
        """
        Query the datafind server to find frame files matching time interval and
        frame type
        """

        # Datafind query
        logging.info("Loading file list:{}".format(self.filelist))

        f = open(self.filelist)
        frames = f.readlines()
        f.close()

        if not hasattr(frames,"__iter__"):
            frames = [self.frames]

        logging.info("Will use {} frames".format( len(frames)))

        return frames


    def list_files(self, frames):
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
        self.files = map(unwrap_file_dict, zip([self]*len(frames),frames))
        

    def _file_dict(self, frame):
        """
        Create a dictionary with LFN properties
        """


        basename = os.path.basename(frame)
        name = basename
        directory = os.path.dirname(frame)

        size, adler_checksum, md5_checksum = check_storage(frame)
        url = os.path.join(self.global_url, basename)

        pfn = ligo_lfn2pfn.ligo_lab(self.scope, name, None, None, None)

        return {'rse':self.rse,
                'scope':self.scope,
                'name':name,
                'bytes':size,
                'filename':basename,
                'adler32':adler_checksum,
                'md5':md5_checksum,
                'pfn':pfn}


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
    logging.getLogger("gfal2").setLevel(logging.WARNING)

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
    dataset = DatasetInjector(ap.file_list, ap.dataset_name, scope=ap.scope,
                              rse=ap.rse, lifetime=ap.lifetime)

    logging.info("File identification/verification took {:.2} mins".format(
        (time.time()-start_time)/60.))

    if ap.dry_run:
        logging.info("Dry run: ending process before rucio interactions")
        sys.exit(0)


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
                        'md5': filemd['md5'],
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




