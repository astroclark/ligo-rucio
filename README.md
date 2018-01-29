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
