
CC = g++
CFLAGS = -O3 -march=native

JAKE=${JAKEROOT}/src/jake.py

TGINCLUDE = -I$(TGPATH)/include
TGLIB = -L$(TGPATH)/lib

all: cversion jake

cversion: skewedgaussseidel.cc
	$(CC) $(CFLAGS) skewedgaussseidel.cc -o sgs.cversion.exe

runcversion:
	./sgs.cversion.exe

jake: skewedgaussseidel.cc
	$(JAKE) -- $(CC) $(CFLAGS) skewedgaussseidel.cc -o sgs.jakeversion.exe

runjake:
	./sgs.jakeversion.exe

mopt: imgfilt-tg.cc
	$(CC) $(CFLAGS) $(TGINCLUDE) $(TGLIB) -ltaskgraph imgfilt-tg.cc -o if.tgversion.exe

runmopt:
	./if.tgversion.exe

clean:
	rm  -f *.exe 
