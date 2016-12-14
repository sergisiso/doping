all: compile

compile:
	cd src/runtime && make
	mv src/runtime/JakeRuntime.o bin/

run: compile
	python2 ./src/jake.py -- g++ test/matrixmult/mm.cc -o qtest
	./qtest 1000

test:
	echo "Not yet implemented"

clean:
	rm -rf bin/* *.log test/*.log qtest
	cd test/imgfilt && make clean
	cd test/matrixmult && make clean
	cd test/skewedgaussseidel && make clean

