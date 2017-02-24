all: compile

compile:
	cd src/runtime && make
	mv src/runtime/JakeRuntime.o bin/

run: compile
	@#MultipleMatrixmult
	@#python2 ./src/jake.py -- g++ -O3 -march=native test/multiplematrixmult/mm.cc -o qtest
	@#time ./qtest 50 100000

	#g++ -O3 -march=native test/multiplematrixmult/mm.cc -o qtest_original
	#time ./qtest_original 50 1000
	
	#Imgfilt
	python2 ./src/jake.py -- g++ -O3 -march=native test/imgfilt/imgfilt-cpp.cc -o qtest
	time ./qtest 1000
	g++ -O3 -march=native test/imgfilt/imgfilt-cpp.cc -o qtest_original
	time ./qtest_original 1000

test: compile
	cd test && ./run_tests.sh

clean:
	rm -rf bin/* *.log test/*.log qtest qtest_original
	cd test/helloworld && make clean
	cd test/imgfilt && make clean
	cd test/matrixmult && make clean
	cd test/multiplematrixmult && make clean
	cd test/skewedgaussseidel && make clean

