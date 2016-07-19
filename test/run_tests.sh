#!/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
JAKEBIN="python $DIR/../jake"


RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color


echo " ####### Testing Jake ################"


#for testdir in helloworld matrixmult flops imgfilt skewedgaussseidel
for testdir in matrixmult
do
    echo "  [[[     Running $testdir TEST     ]]]"
    cd $DIR/$testdir
    echo -n " * Cleaning possible early results/binaries "
    output=$( make clean )
    if [ $? == 0 ]; then echo -e "[${GREEN}SUCCESS${NC}]"; else echo -e "[${RED}FAILED${NC}]"; fi
    echo -n "  * Running Jake to transform source code: "
    output=$( $JAKEBIN mm.cc mm_auto.cc )
    if [ $? == 0 ]; then echo -e "[${GREEN}SUCCESS${NC}]"; else echo -e "[${RED}FAILED${NC}]"; fi
    echo -n "  * Compiling native code: "
    output=$( make cversion )
    if [ $? == 0 ]; then echo -e "[${GREEN}SUCCESS${NC}]"; else echo -e "[${RED}FAILED${NC}]"; fi
    echo -n "  * Running native code: "
    output=$( ./mm.cversion.exe )
    if [ $? == 0 ]; then echo -e "[${GREEN}SUCCESS${NC}]"; else echo -e "[${RED}FAILED${NC}]"; fi
    echo -n "  * Compiling jake code: "
    output=$( make tgauto )
    if [ $? == 0 ]; then echo -e "[${GREEN}SUCCESS${NC}]"; else echo -e "[${RED}FAILED${NC}]"; fi
    echo -n "  * Running Jake code: "
    output=$( ./mm.tgauto.exe )
    if [ $? == 0 ]; then echo -e "[${GREEN}SUCCESS${NC}]"; else echo -e "[${RED}FAILED${NC}]"; fi
    echo -n "  * Compiling manually optimized code: "
    output=$( make tgversion )
    if [ $? == 0 ]; then echo -e "[${GREEN}SUCCESS${NC}]"; else echo -e "[${RED}FAILED${NC}]"; fi
    echo -n "  * Running manually optimized code: "
    output=$( ./mm.tgversion.exe )
    if [ $? == 0 ]; then echo -e "[${GREEN}SUCCESS${NC}]"; else echo -e "[${RED}FAILED${NC}]"; fi

done

