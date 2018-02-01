FROM ligo/software:el7
MAINTAINER James Alexander Clark <james.clark@ligo.org>

# Install Rucio
# Based on https://github.com/rucio/rucio/blob/master/etc/docker/daemons/Dockerfile
RUN pip install rucio

# Install dependecies
RUN yum install -y \
    gfal2 \
    gfal2-plugin-file \
    gfal2-plugin-gridftp \
    gfal2-plugin-http \
    gfal2-plugin-srm \
    gfal2-plugin-xrootd \
    gfal2-python

# PyCBC
USER root
RUN pip install --upgrade setuptools pip git+https://github.com/ligo-cbc/pycbc  

RUN groupadd -r ligo-rucio && useradd --no-log-init -r -g ligo-rucio ligo-rucio
USER ligo-rucio
WORKDIR /home/ligo-rucio

ENTRYPOINT ["/bin/bash"]


