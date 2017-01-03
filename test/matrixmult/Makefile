
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
	diff <(grep "Sum of" cversion.output) <(grep "Sum of" jakeversion.output)

mopt: mm_manual_opt.cc
	$(CC) $(CFLAGS) mm_manual_opt.cc -o mm.manualopt.exe

runmopt:
	./mm.manualopt.exe 1000

clean:
	rm  -f *.exe *.output mm.jake.*
