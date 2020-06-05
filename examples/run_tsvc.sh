#!/usr/bin/env bash

cd benchmark/scripts
 ./bench.py --compiler gcc \
            --parameters RUNTIME_ALL \
            --isa avx2 \
            --results test \
            --benchmark LOOP_REROLLING \
            --cmd-prefix 'dope --'

 #           --run-locally
