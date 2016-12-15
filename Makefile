all: compile

compile:
	cd src/runtime && make
	mv src/runtime/JakeRuntime.o bin/

run: compile
	python2 ./src/jake.py -- g++ -O3 -march=native test/matrixmult/mm.cc -o qtest
	time ./qtest 1000
	g++ -O3 -march=native test/matrixmult/mm.cc -o qtest_original
	time ./qtest_original 1000

test:
	echo "Not yet implemented"

clean:
	rm -rf bin/* *.log test/*.log qtest qtest_original
	cd test/imgfilt && make clean
	cd test/matrixmult && make clean
	cd test/multiplematrixmult && make clean
	cd test/skewedgaussseidel && make clean

