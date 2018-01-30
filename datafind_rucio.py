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

import sys
import argparse
from pycbc.frame import frame_paths
from pycbc.frame.losc import losc_frame_urls


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
    opts = parser.parse_args()

    return opts


def main():


    # Parse input
    opts = parse()

    # Datafind query
    print "Querying datafind server:"
    print "Type: ", opts.frame_type
    print "Interval: ({0},{1}]".format(opts.gps_start_time, opts.gps_end_time)

    if opts.open_data:
        frame_urls = losc_frame_urls(opts.ifo, opts.gps_start_time,
                opts.gps_end_time)
    else:
        frame_urls = frame_paths(opts.frame_type, opts.gps_start_time,
                opts.gps_end_time, url_type='file')

    return frame_urls

if __name__ == "__main__":

    frame_urls = main()

    print "Frames matching Type & Interval:"
    for fu in frame_urls:
        print fu



