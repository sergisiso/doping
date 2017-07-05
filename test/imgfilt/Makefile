
CC = g++
CFLAGS = -O2

JAKE=${JAKEROOT}/src/jake.py

TGINCLUDE = -I$(TGPATH)/include
TGLIB = -L$(TGPATH)/lib

all: cversion

cversion: imgfilt-cpp.cc
	$(CC) $(CFLAGS) imgfilt-cpp.cc -o if.cversion.exe

runcversion:
	./if.cversion.exe 50 | tee cversion.output

jake: imgfilt-cpp.cc
	$(JAKE) -- $(CC) $(CFLAGS) imgfilt-cpp.cc -o if.jakeversion.exe

runjake:
	./if.jakeversion.exe 50 | tee jakeversion.output

mopt: imgfilt-tg.cc
	$(CC) $(CFLAGS) $(TGINCLUDE) $(TGLIB) -ltaskgraph imgfilt-tg.cc -o if.tgversion.exe

runmopt:
	./if.tgversion.exe

perfjake:
	rm -f perfjake.txt
	$(foreach it,$(ITERATIONS), echo $(it) $(shell (/usr/bin/time -f "%e" ./if.jakeversion.exe $$it) 2>&1 > /dev/null) >> perfjake.txt ;)

perfcversion:
	rm -f perfcversion.txt
	$(foreach it,$(ITERATIONS), echo $(it) $(shell (/usr/bin/time -f "%e" ./if.cversion.exe $$it) 2>&1 > /dev/null) >> perfcversion.txt ;)

compare:
	diff cversion.output jakeversion.output




clean:
	rm  -f *.exe *.loop.cc imgfilt-cpp.jake.* *.txt *.output
