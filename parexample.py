#!/usr/bin/env python
#
# parexample.py
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
Demonstration of embarrassingly parallel loops so I can understand / remember
how to apply this to the rucio script
"""

import numpy as np
import multiprocessing
from multiprocessing import Pool
import time

MAXTHREADS=multiprocessing.cpu_count()
print MAXTHREADS
USETHREADS=5

def f(x):
    return x*np.random.randn(100000)


if __name__ == '__main__':
    s = time.time()
    p = Pool(processes=USETHREADS)
    result = p.map(f, [1, 2, 3])
    time_taken = time.time() - s
    print("Time taken in pool: {}".format(time_taken))

    s = time.time()
    result = map(f, [1, 2, 3])
    time_taken = time.time() - s
    print("Time taken serially: {}".format(time_taken))




