#!/usr/bin/env python
# -*- coding:utf-8 -*-
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
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# Authors:
# - James Alexander Clark, <james.clark@ligo.org>, 2018-2019
"""Setup script for ligo_rucio"""
from distutils.core import setup

setup(
    name='gw_rucio',
    version='0.1dev',
    packages=['ligo_rucio',],
    scripts=['bin/ligo_lfn2pfn'],
    license='GPL',
    long_description=open('README.md').read(),
    )

