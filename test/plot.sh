#!/usr/bin/env bash

#Info


gnuplot <<- EOF
    set title " "
    set label "Test: $testname" at screen 0.1, 0.97
    set label "$compilerinfo" at screen 0.1, 0.93
    set label "$cpuinfo" right at screen 0.95, 0.97
    set label "$commitinfo" right at screen 0.95, 0.93
    set xlabel "Iteration"
    set ylabel "Time (s)"
    set term png nocrop enhanced size 800,400
    set output "$testname.png"
    plot "perfcversion_$testname.txt" using 1:2 with pointlines title "Baseline", \
         "perfdoping_$testname.txt" using 1:2 with pointlines title "Compiled with DOpIng"
EOF

