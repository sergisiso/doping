
CC = g++
CFLAGS = -O3 -march=native
ITERATIONS=$(shell seq 10 10 100)

JAKE=${JAKEROOT}/src/jake.py


all: cversion jake

cversion: helloworld.c
	$(CC) $(CFLAGS) helloworld.c -o helloworld.exe

runcversion:
	./helloworld.exe | tee cversion.output

jake: helloworld.c
	$(JAKE) -- $(CC) $(CFLAGS) helloworld.c -o hw.jakeversion.exe

runjake:
	./hw.jakeversion.exe | tee jakeversion.output

perfjake:
	rm -f perfjake.txt
	$(foreach it,$(ITERATIONS), echo $(it) $(shell (/usr/bin/time -f "%e" ./hw.jakeversion.exe $$it) 2>&1 > /dev/null) >> perfjake.txt ;)

perfcversion:
	rm -f perfcversion.txt
	$(foreach it,$(ITERATIONS), echo $(it) $(shell (/usr/bin/time -f "%e" ./helloworld.exe $$it) 2>&1 > /dev/null) >> perfcversion.txt ;)



compare:
	diff cversion.output jakeversion.output

clean:
	rm  -f *.exe *.output *.txt
