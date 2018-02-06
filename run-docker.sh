#!/bin/bash

docker run -it -u $(id -u):$(id -g) --rm --name ligo-rucio \
    -v $(grid-proxy-info -path):/tmp/x509up_u1001 \
    -v ${PWD}:/home/ligo-rucio \
    -v /etc/group:/etc/group:ro -v /etc/passwd:/etc/passwd:ro \
        jclarkastro/ligo-rucio

#   docker run -it  --rm --name ligo-rucio \
#       -v ${PWD}:/home/ligo-rucio jclarkastro/ligo-rucio

#   docker run -it --rm --name ligo-rucio \
#       -v $(grid-proxy-info -path):/tmp/x509up_u1000 \
#       -v ${PWD}:/home/ligo-rucio jclarkastro/ligo-rucio
