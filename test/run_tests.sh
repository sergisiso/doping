#!/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
JAKEBIN="python $DIR/../jake"


RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo ""
echo " ####### Testing Jake ################"
echo ""

#for testdir in helloworld matrixmult flops imgfilt skewedgaussseidel
for testdir in helloworld matrixmult
do
    echo "  [[[     Running $testdir TEST     ]]]"
echo ""
    cd $DIR/$testdir
    echo -n "  * Cleaning possible early results/binaries "
    output=$( make clean )
    if [ $? == 0 ]; then echo -e "[${GREEN}SUCCESS${NC}]"; else echo -e "[${RED}FAILED${NC}]"; fi
    echo -n "  * Compiling native code: "
    output=$( make cversion )
    if [ $? == 0 ]; then echo -e "[${GREEN}SUCCESS${NC}]"; else echo -e "[${RED}FAILED${NC}]"; fi
    echo -n "  * Running native code: "
    output=$( make runcversion )
    if [ $? == 0 ]; then echo -e "[${GREEN}SUCCESS${NC}]"; else echo -e "[${RED}FAILED${NC}]"; fi
    echo -n "  * Compiling jake code: "
    output=$( make jake )
    if [ $? == 0 ]; then echo -e "[${GREEN}SUCCESS${NC}]"; else echo -e "[${RED}FAILED${NC}]"; fi
    echo -n "  * Running Jake code: "
    output=$( make runjake )
    if [ $? == 0 ]; then echo -e "[${GREEN}SUCCESS${NC}]"; else echo -e "[${RED}FAILED${NC}]"; fi
    echo -n "  * Compiling manually optimized code: "
    output=$( make mopt )
    if [ $? == 0 ]; then echo -e "[${GREEN}SUCCESS${NC}]"; else echo -e "[${RED}FAILED${NC}]"; fi
    echo -n "  * Running manually optimized code: "
    output=$( make runmopt )
    if [ $? == 0 ]; then echo -e "[${GREEN}SUCCESS${NC}]"; else echo -e "[${RED}FAILED${NC}]"; fi
    echo ""
done

