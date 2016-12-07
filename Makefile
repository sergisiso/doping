all: compile

compile:
	echo "Not yet implemented"

run:
	python2 ./src/jake.py -- g++ test/matrixmult/mm.cc -o qtest

test:
	echo "Not yet implemented"

clean:
	rm -rf bin/* *.log test/*.log
	cd test/imgfilt && make clean
	cd test/matrixmult && make clean
	cd test/skewedgaussseidel && make clean

