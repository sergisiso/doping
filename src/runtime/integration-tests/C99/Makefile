DOPINGSRC = ../../
DOPINGOBJ = dopingRuntime.o


all: gnucompiler

gnucompiler:
	gcc -I${DOPINGSRC} basic_doping.c -c -o basic.o
	g++ basic.o ${DOPINGSRC}/${DOPINGOBJ} -ldl -o basic

