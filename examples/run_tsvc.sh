#!/usr/bin/env bash

export DOPING_BENCHMARK=1
cd benchmark/scripts
./bench.py --compiler gcc \
           --parameters RUNTIME_ATTRIBUTES \
           --isa avx2 \
           --results test \
           --benchmark CONTROL_FLOW\
           --cmd-prefix 'dope --' \
           --run-locally
