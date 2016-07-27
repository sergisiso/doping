#!/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
JAKEBIN="python $DIR/../jake"
LOGFILE="$PWD/test.log"

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo ""
echo " ####### Testing Jake ################"
echo ""


echo "TEST executed on $(date)" > $LOGFILE

execute () {
    echo "$1" >> $LOGFILE
    echo -n "$1"
    SECONDS=0
    output=$( $2 &>> $LOGFILE)
    if [ $? == 0 ]; then
        echo -e "[${GREEN}SUCCESS${NC} ($SECONDS sec) ]";
    else
        echo -e "[${RED}FAILED (see $LOGFILE) ${NC}]";
    fi
}

#for testdir in helloworld matrixmult flops imgfilt skewedgaussseidel
for testdir in helloworld matrixmult
do
    echo "  [[[     Running $testdir TEST     ]]]"
    echo ""
    cd $DIR/$testdir
    execute "  * Cleaning possible early results/binaries " "make clean"
    execute "  * Compiling native code: " "make cversion"
    execute "  * Running native code: " "make runcversion"
    execute "  * Compiling jake code: " "make jake"
    execute "  * Running Jake code: " "make runjake" 
    execute "  * Compiling manually optimized code: " "make mopt"
    execute "  * Running manually optimized code: " "make runmopt"
    echo ""
done

