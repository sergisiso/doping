
CC = g++
CFLAGS = -O2

DOPING=${DOPING_ROOT}/bin/dope

TGINCLUDE = -I$(TGPATH)/include
TGLIB = -L$(TGPATH)/lib

all: cversion

cversion: imgfilt-cpp.cc
	$(CC) $(CFLAGS) imgfilt-cpp.cc -o if.cversion.exe

runcversion:
	./if.cversion.exe 50 | tee cversion.output

doping: imgfilt-cpp.cc
	$(DOPING) -- $(CC) $(CFLAGS) imgfilt-cpp.cc -o if.dopingversion.exe

rundoping:
	./if.dopingversion.exe 50 | tee dopingversion.output

perfdoping:
	rm -f perfdoping.txt
	$(foreach it,$(ITERATIONS), echo $(it) $(shell (/usr/bin/time -f "%e" ./if.dopingversion.exe $$it) 2>&1 > /dev/null) >> perfdoping.txt ;)

perfcversion:
	rm -f perfcversion.txt
	$(foreach it,$(ITERATIONS), echo $(it) $(shell (/usr/bin/time -f "%e" ./if.cversion.exe $$it) 2>&1 > /dev/null) >> perfcversion.txt ;)

compare:
	diff cversion.output dopingversion.output

clean:
	rm  -f *.exe *.loop.cc imgfilt-cpp.doping.* *.txt *.output
