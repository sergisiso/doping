all: compile

CC=g++
FLAGS=-O2

.PHONY: dependencies compile test test-codegen test-runtime examples quickrun clean

dependencies:
	pip install -e .[dev]
	git submodule init && git submodule update

compile:
	cd src/runtime && make
	cp src/runtime/build/libdoping.so bin/libdoping.so
	cp src/runtime/include/dopingRuntime.h bin/doping.h

test-codegen:
	pytest src/codegen --compile  # Doping Unit tests

test-runtime:
	cd src/runtime && make test  # Runtime Unit tests

test: test-codegen test-runtime examples

examples:
	cd examples && ./run_examples.sh  # Integration tests

quickrun: compile
	cd examples/quick_examples/multiplematrixmult/ && make doping
	cd examples/quick_examples/multiplematrixmult/ && DOPING_VERBOSE=1 make rundoping

clean:
	rm -rf ./src/clang/__pycache__ ./src/codegen/CodeTransformations/__pycache__
	rm -rf ./src/codegen/DopingAST/__pycache__ ./src/codegen/__pycache__ ./src/codegen/test/__pycache__
	rm -rf bin/*.o bin/*.so bin/*.h *.log examples/*.log qtest qtest_original Doping.egg-info dist
	cd examples/quick_examples/helloworld && make clean
	cd examples/quick_examples/imgfilt && make clean
	cd examples/quick_examples/multiplematrixmult && make clean
	cd examples/quick_examples/skewedgaussseidel && make clean
	cd doc && make clean
	cd src/runtime && make clean

