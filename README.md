# LIGO Rucio
This repository has tools and notes for demonstration and evaluation of
[Rucio](https://rucio.cern.ch/) for LIGO bulk data management.

## Preliminaries

First step is to set up a simple script to:
 * Retrieve a list of frame files which corresponds to some nominal data set
 * Loop through the list and call the Ruico API

This can be easily achieved with a simple python script which makes use of
the [pycbc datafind
module](https://ldas-jobs.ligo.caltech.edu/~cbc/docs/pycbc/pycbc.workflow.html?highlight=datafind#module-pycbc.workflow.datafind) and a pip install of Rucio.  

Libraries/dependencies will be managed by building a docker image from publicly
available pycbc images.

## Example: CMS evaluation script
[cmsexample.py](https://github.com/astroclark/ligo-rucio/blob/master/cmsexample.py)
is a command line tool for registering a CMS dataset into rucio.  [This set of
slides](https://indico.fnal.gov/event/16010/contribution/1/material/slides/0.pdf)
describes the CMS evaluation.  The CMS hierachy is more complicated than (at
least our initial test) in LIGO.  In CMS:
 * Files: ~4GB
 * Blocks (Rucio dataset): chunks of ~100 files.  This is the typical unit of data transfer.
 * Datasets (Rucio container): N blocks with some physical meaning

The (current) proposed LIGO arrangement is simpler:
 * LIGO runs (ER8, O1, ...):  Rucio scope
 * LIGO dataset == Rucio dataset


Here's a run-through of [cmsexample.py](https://github.com/astroclark/ligo-rucio/blob/master/cmsexample.py):
 1. Instantiate the ```DataSetInjector``` object
