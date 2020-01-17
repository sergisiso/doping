DOPINGSRC = ../../include
LDFLAGS = -L../../build -ldoping -ldl
CFLAGS= -pedantic-errors -Wall -Wextra


all: gnucompiler

gnucompiler:
	gcc ${CFLAGS} -I${DOPINGSRC} basic_doping.c $(LDFLAGS) -o basic

run:
	LD_LIBRARY_PATH=$(shell pwd)/../../build ./basic

debug:
	LD_LIBRARY_PATH=$(shell pwd)/../../build DOPING_VERBOSE=1 ./basic

clean:
	-@rm -rvf  ./basic
