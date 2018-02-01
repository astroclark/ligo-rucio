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
from pycbc.frame.losc import losc_frame_urls

from gfal2 import Gfal2Context, GError
import rucio.rse.rsemanager as rsemgr
from rucio.client.didclient import DIDClient
from rucio.client.replicaclient import ReplicaClient
from rucio.common.exception import DataIdentifierAlreadyExists
from rucio.common.exception import RucioException
from rucio.common.exception import FileAlreadyExists

# FIXME: These times are non-exhaustive and inexact
DATA_RUNS={
        'ER8':(1123858817,1126623617),
        'O1':(1126623617,1137254417),
        'ER9':(1152136817,1152169157),
        'O2':(1164499217,1187654418)
        }

DATAFIND_SERVER="datafind.ligo.org:443"

def rucio2ligo(dids):
    """
    Construct the expected path to frames, given a Rucio DID

    Path should be <run>/<type>/<ifo>/<site>-<type>-<day>

    E.g., ER8/H1_HOFT_C00/H1/H-H1_HOFT_C00-1126
    """

    if not hasattr(dids,"__iter__"):
        dids = [dids]

    frame_urls = []
    for did in dids:
        run=did.split(":")[0]
        name=did.split(":")[1]
        ftype=name.split("-")[1]
        ifo=ftype[0]
        day=name.split('-')[2][:4]
        frame_urls.append(os.path.join(frame_path,run,ftype,ifo,day,name))
    return frame_urls

class DatasetInjector(object):
    """
    General Class for injecting a LIGO dataset in rucio

    1) Find frames with gw_data_find
    2) Convert frame names to rucio DIDs
    3) Create Rucio dataset
    4) Register Rucio dataset
    """

    def __init__(self, start_time, end_time, frtype, site=None, rse=None,
            check=True, lifetime=None, dry_run=False):

        self.start_time = start_time
        self.end_time = end_time

        self.site = site

        if rse is None:
            rse = site
        self.rse = rse
        self.scope = scope
        self.uuid = uuid
        self.check = check
        self.lifetime = lifetime
        self.dry_run = dry_run

        # Locate frames
        self.find_frames()

        # Create rucio names
        self.frames2rucio()

    def find_frames(self):
        """
        Query the datafind server to find frame files matching time interval and
        frame type
        """

	# Datafind query
	print "Querying datafind server:"
	print "Type: ", self.frtype
        print "Interval: ({0},{1}]".format(self.start_time, self.end_time)

        self.frames = frame_paths(self.frtype, self.start_time, self.end_time,
                url_type='file')

        if not hasattr(self.frames,"__iter__"):
            self.frames = [self.frames]

    def frames2rucio(self):
        """
        Determine the Rucio DIDs for given frame URLs
        """

        self.rucio_frames = []
        for frame in self.frames:
            name = os.path.basename(frame)
            # FIXME check frame name is valid (hard to see how it wouldn't be if
            # it came from gw_data_find)
            start = int(name.split('-')[2])

            # Identify data run (scope)
            for scope in DATA_RUNS:
                if DATA_RUNS[scope][0] <= start <= DATA_RUNS[scope][1]:
                    self.rucio_frames.append(":".join([scope, name]))
                    break
            else:
                warnstr=("Frame {frame} not in known data-gathering run. Setting"
                        " scope=AW".format(frame=name))
                warnings.warn(warnstr, Warning)

#        self.url = ''

#       self.getmetadata()
#       self.get_global_url()
#       self.didc = DIDClient()
#       self.repc = ReplicaClient()
#
#       self.gfal = Gfal2Context()


def parse_cmdline():

    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument("--verbose", default=False, action="store_true",
            help="""Instead of a progress bar, Print distances & SNRs to
            stdout""")

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


#########################################################################

def main():

    # Parse input
    ap = parse_cmdline()

    dataset = DatasetInjector(ap.gps_start_time, ap.gps_end_time, ap.frame_type)
    print dataset.frames


if __name__ == "__main__":

    main()




