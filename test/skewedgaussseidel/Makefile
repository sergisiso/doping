
CC = g++
CFLAGS = -O3 -march=native

JAKE=${JAKEROOT}/src/jake.py

TGINCLUDE = -I$(TGPATH)/include
TGLIB = -L$(TGPATH)/lib

all: cversion jake

cversion: skewedgaussseidel.cc
	$(CC) $(CFLAGS) skewedgaussseidel.cc -o sgs.cversion.exe

runcversion:
	./sgs.cversion.exe | tee cversion.output

jake: skewedgaussseidel.cc
	$(JAKE) -- $(CC) $(CFLAGS) skewedgaussseidel.cc -o sgs.jakeversion.exe

runjake:
	./sgs.jakeversion.exe | tee jakeversion.output

mopt: imgfilt-tg.cc
	$(CC) $(CFLAGS) $(TGINCLUDE) $(TGLIB) -ltaskgraph imgfilt-tg.cc -o if.tgversion.exe

runmopt:
	./if.tgversion.exe

perfjake:
	rm -f perfjake.txt
	$(foreach it,$(ITERATIONS), echo $(it) $(shell (/usr/bin/time -f "%e" ./hw.jakeversion.exe $$it) 2>&1 > /dev/null) >> perfjake.txt ;)

perfcversion:
	rm -f perfcversion.txt
	$(foreach it,$(ITERATIONS), echo $(it) $(shell (/usr/bin/time -f "%e" ./helloworld.exe $$it) 2>&1 > /dev/null) >> perfcversion.txt ;)

compare:
	diff cversion.output jakeversion.output


clean:
	rm  -f *.exe *.output skewedgaussseidel.jake.*
