FROM pycbc/pycbc-el7

RUN echo "Building ligo-rucio dev image"
MAINTAINER James Alexander Clark <james.clark@ligo.org>


# Install Rucio
USER root
RUN pip install --upgrade pip && pip install --upgrade rucio-clients

#USER ligo-rucio
RUN groupadd -r ligo-rucio && useradd --no-log-init -r -g ligo-rucio ligo-rucio
USER ligo-rucio
WORKDIR /home/ligo-rucio

ENTRYPOINT ["/bin/bash"]


