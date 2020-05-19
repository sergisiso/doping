#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
LOGFILE="$PWD/test.log"

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo ""
echo " ####### Testing doping ################"
echo ""


echo "TEST executed on $(date)" > $LOGFILE

execute () {
    echo "$1" >> $LOGFILE
    echo -n "$1"
    SECONDS=0
    output=$( $2 &>> $LOGFILE )
    if [ $? == 0 ]; then
        echo -e "[${GREEN}SUCCESS${NC} ($SECONDS sec) ]";
    else
        echo -e "[${RED}FAILED (see $LOGFILE) ${NC}]";
    fi
    echo "" >> $LOGFILE
}

for testdir in helloworld multiplematrixmult imgfilt skewedgaussseidel
#for testdir in helloworld matrixmult
do
    echo "[[[     Running $testdir TEST     ]]]" | tee -a $LOGFILE
    echo "==================================================" | tee -a $LOGFILE
    echo ""
    cd $DIR/quick_examples/$testdir
    execute "> Cleaning possible early results/binaries " "make clean"
    execute "> Compiling native code: " "make cversion"
    execute "> Running native code: " "make runcversion"
    execute "> Compiling doping code: " "make doping"
    execute "> Running doping code: " "make rundoping"
    execute "> Compare native and doping outputs: " "make compare"
    #execute "  * Compiling manually optimized code: " "make mopt"
    #execute "  * Running manually optimized code: " "make runmopt"
    echo ""
done

