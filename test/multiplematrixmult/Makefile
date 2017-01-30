
CC = g++
CFLAGS = -O3 -march=native

ITERATIONS=$(shell seq 1000 1000 50000)

JAKE=${JAKEROOT}/src/jake.py

all: cversion mopt jake

cversion: mm.cc
	$(CC) $(CFLAGS) mm.cc -o mm.cversion.exe

runcversion:
	./mm.cversion.exe 50 10000 | tee cversion.output

jake: mm.cc
	python $(JAKE) -- $(CC) $(CFLAGS) mm.cc -o mm.jakeversion.exe

runjake:
	./mm.jakeversion.exe 50 10000 | tee jakeversion.output

compare:
	diff cversion.output jakeversion.output

mopt: mm_manual_opt.cc
	$(CC) $(CFLAGS) mm_manual_opt.cc -o mm.manualopt.exe

runmopt:
	./mm.manualopt.exe 1000

perfjake:
	rm -f perfjake.txt
	$(foreach it,$(ITERATIONS), \
		echo -n "$(it) " >> perfjake.txt; \
		(/usr/bin/time -f "%e" ./mm.jakeversion.exe 50 $(it) 2>&1 > /dev/null) >> perfjake.txt ; \
	)

perfcversion:
	rm -f perfcversion.txt
	$(foreach it,$(ITERATIONS), \
		echo -n "$(it) " >> perfcversion.txt; \
		(/usr/bin/time -f "%e" ./mm.cversion.exe 50 $(it) 2>&1 > /dev/null) >> perfcversion.txt ; \
	)



clean:
	rm  -f *.exe *.output mm.jake.* *.txt
