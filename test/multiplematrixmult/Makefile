
CC = g++
CFLAGS = -O3 -march=native


JAKE=${JAKEROOT}/src/jake.py

all: cversion mopt jake

cversion: mm.cc
	$(CC) $(CFLAGS) mm.cc -o mm.cversion.exe

runcversion:
	./mm.cversion.exe 1000 | tee cversion.output

jake: mm.cc
	python $(JAKE) -- $(CC) $(CFLAGS) mm.cc -o mm.jakeversion.exe

runjake:
	./mm.jakeversion.exe 1000 | tee jakeversion.output

compare:
	diff cversion.output jakeversion.output

mopt: mm_manual_opt.cc
	$(CC) $(CFLAGS) mm_manual_opt.cc -o mm.manualopt.exe

runmopt:
	./mm.manualopt.exe 1000

perfjake:
	rm -f perfjake.txt
	$(foreach it,$(ITERATIONS), echo $(it) $(shell (/usr/bin/time -f "%e" ./hw.jakeversion.exe $$it) 2>&1 > /dev/null) >> perfjake.txt ;)

perfcversion:
	rm -f perfcversion.txt
	$(foreach it,$(ITERATIONS), echo $(it) $(shell (/usr/bin/time -f "%e" ./helloworld.exe $$it) 2>&1 > /dev/null) >> perfcversion.txt ;)



clean:
	rm  -f *.exe *.output mm.jake.*
