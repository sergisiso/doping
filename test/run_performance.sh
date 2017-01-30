#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
JAKEBIN="python $DIR/../jake"
LOGFILE="$PWD/test.log"

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

dateformat=$( date '+%Y-%b-%d-%k-%M' )
resultsdir="$(pwd)/performance-$dateformat"
cpuinfo=$(cat /proc/cpuinfo | grep -m 1 'model name' | sed 's/.*://')
commitinfo="Git commit: $(git log --format="%h" -n 1)"

echo ""
echo " ####### Testing Jake - $resultsdir ################"
echo ""

echo "PERFORMANCE TEST executed on $dateformat" > $LOGFILE
rm -rf $resultsdir
mkdir $resultsdir

execute () {
    echo "$1" >> $LOGFILE
    echo -n "$1"
    SECONDS=0
    output=$( $2 &>> $LOGFILE )
    if [ $? == 0 ]; then
        echo -e "[${GREEN}SUCCESS${NC} ($SECONDS sec) ]";
    else
        echo -e "[${RED}FAILED (see $LOGFILE) ${NC}]";
        exit
    fi
    echo "" >> $LOGFILE
}


#for testdir in helloworld matrixmult imgfilt skewedgaussseidel
for testdir in matrixmult
do
    echo "  [[[     Running $testdir TEST     ]]]"
    echo ""
    cd $DIR/$testdir
    execute "  * Cleaning possible early results/binaries " "make clean"
    execute "  * Compiling native code: " "make cversion"
    execute "  * Compiling jake code: " "make jake"
    execute "  * Running native code: " "make perfcversion"
    execute "  * Running Jake code: " "make perfjake"
    #execute "  * Compare native and jake outputs: " "make compare"
    cp perfcversion.txt $resultsdir/perfcversion_$testdir.txt
    cp perfjake.txt $resultsdir/perfjake_$testdir.txt
    compilerinfo="$(grep "CC =" Makefile) $(grep "CFLAGS =" Makefile)"
    cp $DIR/plot.sh $resultsdir/${testdir}_plot.sh
    sed  -i "s/#Info/#Info\ncompilerinfo=\"$compilerinfo\"/" $resultsdir/${testdir}_plot.sh
    sed  -i "s/#Info/#Info\ncommitinfo=\"$commitinfo\"/" $resultsdir/${testdir}_plot.sh
    sed  -i "s/#Info/#Info\ncpuinfo=\"$cpuinfo\"/" $resultsdir/${testdir}_plot.sh
    sed  -i "s/#Info/#Info\ntestname=\"$testdir\"/" $resultsdir/${testdir}_plot.sh
    #execute "  * Compiling manually optimized code: " "make mopt"
    #execute "  * Running manually optimized code: " "make runmopt"
    echo ""
done

