#!/usr/bin/env python
#
# datafind_rucio.py
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
Query a datafind server to locate a list of local frame files and pass that list
to rucio
"""

import warnings
warnings.simplefilter("ignore")

import os,sys
import argparse
from pycbc.frame import frame_paths
from pycbc.frame.losc import losc_frame_urls

# FIXME: These times are non-exhaustive and inexact
obs_runs={
        'ER8':(1123858817,1126623617),
        'O1':(1126623617,1137254417),
        'ER9':(1152136817,1152169157),
        'O2':(1164499217,1187654418)
        }

frame_path="/cvmfs/oasis.opensciencegrid.org/ligo/frames"

def parse():

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


def frame_urls(ap):

    # Datafind query
    print "Querying datafind server:"
    print "Type: ", ap.frame_type
    print "Interval: ({0},{1}]".format(ap.gps_start_time, ap.gps_end_time)

    if ap.open_data:
        frame_urls = losc_frame_urls(ap.ifo, ap.gps_start_time,
                ap.gps_end_time)
    else:
        frame_urls = frame_paths(ap.frame_type, ap.gps_start_time,
                ap.gps_end_time, url_type='file')
    return frame_urls

def ligo2rucio(frame_urls):
    """
    Determine the Rucio DIDs for given frame URLs

    Take scope=frame type for now
    """

    if not hasattr(frame_urls,"__iter__"):
        frame_urls = [frame_urls]

    dids = []
    for frame_url in frame_urls:
        name = os.path.basename(frame_url)
        start = int(name.split('-')[2])
        #end = str(int(start)+int(name.aplit('-')[-1].replace('.gwf','')))

        # Identify data run
        for scope in obs_runs:
            if obs_runs[scope][0] <= start <= obs_runs[scope][1]:
                dids.append(":".join([scope, name]))
                break
        else:
            print "Frame time not in known data-gathering run:"
            print obs_runs
            sys.exit(-1)

    return dids

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


def main():

    # Parse input
    ap = parse()

    # Retrieve URLs of frames matching query
    frames = frame_urls(ap)

    # Convert to Rucio DIDs:
    dids = ligo2rucio(frames)

    print "Frames converted to DIDs:"
    for frame, did in zip(frames, dids):
        print "%s -> %s" % (frame, did)

    # Convert DIDs back to frames
    frames = rucio2ligo(dids)

    print "DIDs converted to frames:"
    for did, frame in zip(dids, frames):
        print "%s -> %s" % (did, frame)


if __name__ == "__main__":

    main()




