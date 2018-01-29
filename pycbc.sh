#!/bin/bash
docker run -it -u $(id -u):$(id -g) --rm --name pycbc_session -v ${PWD}:/work -w /work pycbc/pycbc-el7
