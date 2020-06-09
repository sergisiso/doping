#!/usr/bin/env bash

export DOPING_BENCHMARK=1
cd benchmark/scripts
./bench.py --compiler gcc \
           --parameters RUNTIME_ALL \
           --isa avx2 \
           --results test \
           --benchmark PACKING \
           --cmd-prefix 'dope --'

 #           --run-locally
