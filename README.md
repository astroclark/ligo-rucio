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
 1. Add supported protocols (e.g., srm, gsiftp, http, ...).  To begin with, we can just use gsiftp:
    ```
    rucio-admin rse add-protocol  \
        --prefix /user/ligo/rucio \
        --domain-json '{"wan": {"read": 1, "write": 1, "delete": 1, "third_party_copy": 1}}' \
        --scheme gsiftp \
        --hostname red-gridftp.unl.edu \
        LIGOTEST
    ```
Note that rucio-admin operations should be performed with `RUCIO_ACCOUNT=root`

### Scope
At least for testing, we will designate scopes according to data-taking runs
(engineering and observing runs).   To create an ER8 scope:
```
rucio-admin scope add --account jclark --scope ER8
```
See e.g., [rucio scope
docs](https://rucio.readthedocs.io/cli_admin_examples.html#scope])

### CLI Example
Now that we have an RSE and a scope we can experiment with the [CLI
examples](https://rucio.readthedocs.io/cli_examples.html)

 1. Uploading a single frame with scope "ER8"

```
rucio -v upload \
    /hdfs/frames/ER8/hoft_C02/H1/H-H1_HOFT_C02-11262/H-H1_HOFT_C02-1126256640-4096.gwf
    --rse LIGOTEST --scope ER8 \
    --name H-H1_HOFT_C02-1126256640-4096.gwf
```

Should generate something like,

```
2018-02-05 13:33:31,104    DEBUG    Extracting filesize (457680774) and checksum
(ef00cf51) for file ER8:H-H1_HOFT_C02-1126256640-4096
2018-02-05 13:33:31,106    DEBUG    Automatically setting new GUID
2018-02-05 13:33:31,381    DEBUG    Using account root
2018-02-05 13:33:31,381    DEBUG    Skipping dataset registration
2018-02-05 13:33:31,381    DEBUG    Processing file
ER8:H-H1_HOFT_C02-1126256640-4096 for upload
2018-02-05 13:33:39,285    INFO    Local files and file
ER8:H-H1_HOFT_C02-1126256640-4096 recorded in Rucio have the same checksum. Will
try the upload
2018-02-05 13:33:56,808    INFO    File ER8:H-H1_HOFT_C02-1126256640-4096.gwf
successfully uploaded on the storage
2018-02-05 13:33:56,809    DEBUG    sending trace
2018-02-05 13:33:57,270    DEBUG    Finished uploading files to RSE.
2018-02-05 13:33:57,505    INFO    Will update the file replicas states
2018-02-05 13:33:57,586    INFO    File replicas states successfully updated
Completed in 34.7796 sec.
```


## Python Example

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
