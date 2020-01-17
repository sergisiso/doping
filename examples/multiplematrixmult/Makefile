
CC = g++
CFLAGS = -O3 -march=native

ITERATIONS=$(shell seq 1000 1000 50000)

DOPING=${DOPING_ROOT}/dope

all: cversion mopt doping

cversion: mm.cc
	$(CC) $(CFLAGS) mm.cc -o mm.cversion.exe

runcversion:
	./mm.cversion.exe 50 10000 | tee cversion.output

doping: mm.cc
	$(DOPING) -- $(CC) $(CFLAGS) mm.cc -o mm.dopingversion.exe

rundoping:
	./mm.dopingversion.exe 50 10000 | tee dopingversion.output

compare:
	diff cversion.output dopingversion.output

mopt: mm_manual_opt.cc
	$(CC) $(CFLAGS) mm_manual_opt.cc -o mm.manualopt.exe

runmopt:
	./mm.manualopt.exe 1000

perfdoping:
	rm -f perfdoping.txt
	$(foreach it,$(ITERATIONS), \
		echo -n "$(it) " >> perfdoping.txt; \
		(/usr/bin/time -f "%e" ./mm.dopingversion.exe 50 $(it) 2>&1 > /dev/null) >> perfdoping.txt ; \
	)

perfcversion:
	rm -f perfcversion.txt
	$(foreach it,$(ITERATIONS), \
		echo -n "$(it) " >> perfcversion.txt; \
		(/usr/bin/time -f "%e" ./mm.cversion.exe 50 $(it) 2>&1 > /dev/null) >> perfcversion.txt ; \
	)



clean:
	rm  -f *.exe *.output mm.doping.* *.txt
