
CC = g++
CFLAGS = -O3 -march=native
ITERATIONS=$(shell seq 10 10 100)

DOPING=${DOPING_ROOT}/bin/dope


all: cversion doping

cversion: helloworld.c
	$(CC) $(CFLAGS) helloworld.c -o helloworld.exe

runcversion:
	./helloworld.exe | tee cversion.output

doping: helloworld.c
	$(DOPING) -- $(CC) $(CFLAGS) helloworld.c -o hw.dopingversion.exe

rundoping:
	./hw.dopingversion.exe | tee dopingversion.output

perfdoping:
	rm -f perfdoping.txt
	$(foreach it,$(ITERATIONS), echo $(it) $(shell (/usr/bin/time -f "%e" ./hw.dopingversion.exe $$it) 2>&1 > /dev/null) >> perfdoping.txt ;)

perfcversion:
	rm -f perfcversion.txt
	$(foreach it,$(ITERATIONS), echo $(it) $(shell (/usr/bin/time -f "%e" ./helloworld.exe $$it) 2>&1 > /dev/null) >> perfcversion.txt ;)



compare:
	diff cversion.output dopingversion.output

clean:
	rm  -f *.exe *.output *.txt
