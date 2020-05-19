#!/usr/bin/env bash

cd benchmark/scripts
 ./bench.py --compiler gcc \
            --parameters RUNTIME_ALL \
            --isa avx2 \
            --results test \
            --benchmark LINEAR_DEPENDENCE \
            --run-locally \
            --cmd-prefix 'dope --'
