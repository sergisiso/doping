all: compile

CC=g++
FLAGS=-O2

compile:
	cd src/runtime && make
	mv src/runtime/dopingRuntime.o bin/

run: compile
	# MultipleMatrixmult
	python2 ./src/doping.py -- ${CC} ${FLAGS} examples/multiplematrixmult/mm.cc -o qtest
	#time ./qtest 20 1000000
	#${CC} ${FLAGS} examples/multiplematrixmult/mm.cc -o qtest_original
	#time ./qtest_original 20 1000000
	
	# Imgfilt
	#python2 ./src/doping.py -- g++ -O2 examples/imgfilt/imgfilt-cpp.cc -o qtest
	#time ./qtest 50
	#g++ -O2 examples/imgfilt/imgfilt-cpp.cc -o qtest_original
	#time ./qtest_original 50

	# Skewedgaussseidel
	#python2 ./src/doping.py -- g++ -O2 examples/skewedgaussseidel/skewedgaussseidel.cc -o qtest
	#time ./qtest 50
	#g++ -O2 examples/skewedgaussseidel/skewedgaussseidel.cc -o qtest_original
	#time ./qtest_original 50

	# miniLBE
	#python2 ./src/doping.py -- g++ -O2 examples/imgfilt/imgfilt-cpp.cc -o qtest
	#time ./qtest 50
	#g++ -O2 examples/imgfilt/imgfilt-cpp.cc -o qtest_original
	#time ./qtest_original 50

unittest:
	cd src && python -m pytest

test: compile
	cd examples && ./run_examples.sh

clean:
	rm -rf bin/*.o *.log examples/*.log qtest qtest_original Doping.egg-info dist
	cd examples/helloworld && make clean
	cd examples/imgfilt && make clean
	cd examples/multiplematrixmult && make clean
	cd examples/skewedgaussseidel && make clean
	cd doc && make clean

