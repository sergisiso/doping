#!/usr/bin/env bash

export DOPING_BENCHMARK=1
cd benchmark/scripts

# Test execution
./bench.py --compiler gcc \
           --parameters RUNTIME_ALL \
           --isa avx2 \
           --results test \
           --cmd-prefix 'dope --' \
           --run-locally

           #--cmd-prefix 'dope --' \
           #--benchmark REDUCTIONS \

exit



# Doping execution
./bench.py --compiler pgi \
           --parameters RUNTIME_ALL \
           --isa avx2 \
           --results test \
           --cmd-prefix 'dope --' \
           --run-locally

# Baseline execution
./bench.py --compiler pgi \
           --parameters RUNTIME_ALL \
           --isa avx2 \
           --results test \
           --run-locally

# Expected results execution (it should be without RUNTIME ATTRIBUTES)
./bench.py --compiler pgi \
           --parameters None \
           --isa avx2 \
           --results test \
           --run-locally

