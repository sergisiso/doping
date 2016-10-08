
CC = g++
CFLAGS = -O3 -march=native


JAKE=${JAKEROOT}/src/jake.py

all: cversion mopt jake

cversion: mm.cc
	$(CC) $(CFLAGS) mm.cc -o mm.cversion.exe

runcversion:
	./mm.cversion.exe 1000

jake: mm.cc
	python $(JAKE) -- $(CC) $(CFLAGS) mm.cc -o mm.jakeversion.exe

runjake:
	./mm.jakeversion.exe 1000

mopt: mm_manual_opt.cc
	$(CC) $(CFLAGS) mm_manual_opt.cc -o mm.manualopt.exe

runmopt:
	./mm.manualopt.exe 1000

clean:
	rm  -f mm.cversion.exe mm.jakeversion.exe  mm.manualopt.exe mm.jake.*
