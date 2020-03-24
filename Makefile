all: compile

CC=g++
FLAGS=-O2

.PHONY: dependencies compile test clean

dependencies:
	pip install -e .[dev]
	git submodule init && git submodule update

compile:
	cd src/runtime && make
	cp src/runtime/build/libdoping.so bin/libdoping.so
	cp src/runtime/include/dopingRuntime.h bin/doping.h

run: compile
	# MultipleMatrixmult
	dope -- ${CC} ${FLAGS} examples/multiplematrixmult/mm.cc -o qtest
	#time ./qtest 20 1000000
	#${CC} ${FLAGS} examples/multiplematrixmult/mm.cc -o qtest_original
	#time ./qtest_original 20 1000000
	
	# Imgfilt
	# dope -- g++ -O2 examples/imgfilt/imgfilt-cpp.cc -o qtest
	#time ./qtest 50
	#g++ -O2 examples/imgfilt/imgfilt-cpp.cc -o qtest_original
	#time ./qtest_original 50

	# Skewedgaussseidel
	# dope -- g++ -O2 examples/skewedgaussseidel/skewedgaussseidel.cc -o qtest
	#time ./qtest 50
	#g++ -O2 examples/skewedgaussseidel/skewedgaussseidel.cc -o qtest_original
	#time ./qtest_original 50

	# miniLBE
	# dope -- g++ -O2 examples/imgfilt/imgfilt-cpp.cc -o qtest
	#time ./qtest 50
	#g++ -O2 examples/imgfilt/imgfilt-cpp.cc -o qtest_original
	#time ./qtest_original 50

test: compile
	cd examples && ./run_examples.sh

clean:
	rm -rf ./src/clang/__pycache__ ./src/codegen/CodeTransformations/__pycache__
	rm -rf ./src/codegen/DopingAST/__pycache__ ./src/codegen/__pycache__ ./src/codegen/test/__pycache__
	rm -rf bin/*.o bin/*.so bin/*.h *.log examples/*.log qtest qtest_original Doping.egg-info dist
	cd examples/helloworld && make clean
	cd examples/imgfilt && make clean
	cd examples/multiplematrixmult && make clean
	cd examples/skewedgaussseidel && make clean
	cd doc && make clean
	cd src/runtime && make clean

