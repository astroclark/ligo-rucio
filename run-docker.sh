#!/bin/bash
docker run -it -u $(id -u):$(id -g) --rm --name ligo-rucio \
    -v ${PWD}:/home/ligo-rucio jclarkastro/ligo-rucio
