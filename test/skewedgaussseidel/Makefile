
CC = g++
CFLAGS = -O3 -march=native

DOPING=${DOPING_ROOT}/src/doping.py

TGINCLUDE = -I$(TGPATH)/include
TGLIB = -L$(TGPATH)/lib

all: cversion doping

cversion: skewedgaussseidel.cc
	$(CC) $(CFLAGS) skewedgaussseidel.cc -o sgs.cversion.exe

runcversion:
	./sgs.cversion.exe | tee cversion.output

doping: skewedgaussseidel.cc
	$(DOPING) -- $(CC) $(CFLAGS) skewedgaussseidel.cc -o sgs.dopingversion.exe

rundoping:
	./sgs.dopingversion.exe | tee dopingversion.output

mopt: imgfilt-tg.cc
	$(CC) $(CFLAGS) $(TGINCLUDE) $(TGLIB) -ltaskgraph imgfilt-tg.cc -o if.tgversion.exe

runmopt:
	./if.tgversion.exe

perfdoping:
	rm -f perfdoping.txt
	$(foreach it,$(ITERATIONS), echo $(it) $(shell (/usr/bin/time -f "%e" ./hw.dopingversion.exe $$it) 2>&1 > /dev/null) >> perfdoping.txt ;)

perfcversion:
	rm -f perfcversion.txt
	$(foreach it,$(ITERATIONS), echo $(it) $(shell (/usr/bin/time -f "%e" ./helloworld.exe $$it) 2>&1 > /dev/null) >> perfcversion.txt ;)

compare:
	diff cversion.output dopingversion.output


clean:
	rm  -f *.exe *.output skewedgaussseidel.doping.*
