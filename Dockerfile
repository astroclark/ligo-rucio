#FROM containers.ligo.org/lscsoft/lalsuite:nightly
FROM ligo/software:jessie

RUN echo "Building ligo-rucio dev image"
MAINTAINER James Alexander Clark <james.clark@ligo.org>

# Dependencies
RUN python -m pip install --upgrade setuptools pip \
	&& python -m pip install git+https://github.com/ligo-cbc/pycbc --process-dependency-links  \
    && python -m pip install --upgrade rucio-clients
	#&& python -m pip install git+https://github.com/ligo-cbc/pycbc@v1.9.0#egg=pycbc --process-dependency-links  \


#USER ligo-rucio
RUN groupadd -r ligo-rucio && useradd --no-log-init -r -g ligo-rucio ligo-rucio
USER ligo-rucio
WORKDIR /home/ligo-rucio

ENTRYPOINT ["/bin/bash"]


