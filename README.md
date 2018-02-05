# LIGO Rucio
This repository has tools and notes for demonstration and evaluation of
[Rucio](https://rucio.cern.ch/) for LIGO bulk data management.

## Preliminaries
Some notes on getting started

### Rucio Storage Element
The first thing we need is an
[RSE](http://tbeerman-rucio.readthedocs.io/en/latest/overview_Rucio_Storage_Element.html)
(container for files) to upload our files to.

 1. Create the RSE (see e.g., [CLI admin
    examples](https://rucio.readthedocs.io/cli_admin_examples.html):
    ```
    rucio-admin rse add LIGOTEST
    ```
 1. Add supported protocols (e.g., srm, gsift, http, ...).  To begin with, we can just use gsiftp:
    ```
    rucio-admin rse add-protocol  \
        --prefix /user/ligo/rucio \
        --domain-json '{"wan": {"read": 1, "write": 1, "delete": 1, "third_party_copy": 1}}' \
        --scheme gsiftp \
        --hostname red-gridftp.unl.edu \
        LIGOTEST
    ```

### CLI Example

### Python Example

A next step is to set up a python simple script to:
 * Retrieve a list of frame files which corresponds to some nominal data set
 * Loop through the list and call the Ruico API

This can be easily achieved with a simple python script which makes use of
the [pycbc datafind
module](https://ldas-jobs.ligo.caltech.edu/~cbc/docs/pycbc/pycbc.workflow.html?highlight=datafind#module-pycbc.workflow.datafind) and a pip install of Rucio.  


## Python data-insertion module
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
 1. Instantiate the `DataSetInjector` object, a general class for injecting a
    cms dataset into rucio
 1. `DataSetInjector` has methods to create containers and register files and
    datasets
 1. This class has methods for finding the rucio url and filenames

I do not need anything to do with rucio containers (yet) so can just mimic the
parts associated with file and data set registration, and some of the sanity
checking.  I should be able to swap out my existing routines for translating
LIGO file URLs to Rucio DIDs.
