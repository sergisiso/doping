#!/usr/bin/env bash

export DOPING_BENCHMARK=1
cd benchmark/scripts

# Test execution
#./bench.py --compiler nvc \
#           --parameters None \
#           --isa avx2 \
#           --results test \
#           --run-locally

           #--benchmark REDUCTIONS \
           #--run-novec \
           #--cmd-prefix 'dope --' \

#exit

# Run Clang
./bench.py --compiler clang \
           --parameters RUNTIME_ALL \
           --isa avx2 \
           --results test \
           --cmd-prefix 'dope --' \
           --run-novec \
           --run-locally

./bench.py --compiler clang \
           --parameters RUNTIME_ALL \
           --isa avx2 \
           --results test \
           --run-novec \
           --run-locally

./bench.py --compiler clang \
           --parameters None \
           --isa avx2 \
           --results test \
           --run-locally

# Run GCC
./bench.py --compiler gcc \
           --parameters RUNTIME_ALL \
           --isa avx2 \
           --results test \
           --cmd-prefix 'dope --' \
           --run-novec \
           --run-locally

./bench.py --compiler gcc \
           --parameters RUNTIME_ALL \
           --isa avx2 \
           --results test \
           --run-novec \
           --run-locally

./bench.py --compiler gcc \
           --parameters None \
           --isa avx2 \
           --results test \
           --run-locally

# Run Intel
./bench.py --compiler icc \
           --parameters RUNTIME_ALL \
           --isa avx2 \
           --results test \
           --cmd-prefix 'dope --' \
           --run-novec \
           --run-locally

./bench.py --compiler icc \
           --parameters RUNTIME_ALL \
           --isa avx2 \
           --results test \
           --run-novec \
           --run-locally

./bench.py --compiler icc \
           --parameters None \
           --isa avx2 \
           --results test \
           --run-locally

# Run Nvidia
./bench.py --compiler nvc \
           --parameters RUNTIME_ALL \
           --isa avx2 \
           --results test \
           --cmd-prefix 'dope --' \
           --run-novec \
           --run-locally

./bench.py --compiler nvc \
           --parameters RUNTIME_ALL \
           --isa avx2 \
           --results test \
           --run-novec \
           --run-locally

./bench.py --compiler nvc \
           --parameters None \
           --isa avx2 \
           --results test \
           --run-locally
