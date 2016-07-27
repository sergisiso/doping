
CC = g++
CFLAGS = -O3 -march=native


JAKE=${JAKEROOT}/jake

#TGPATH = /home/sergi/jake/deps/taskgraph-20140613/install

TGINCLUDE = -I$(TGPATH)/include
TGLIB = -L$(TGPATH)/lib

all: cversion mopt jake

cversion: mm.cc
	$(CC) $(CFLAGS) mm.cc -o mm.cversion.exe

runcversion:
	./mm.cversion.exe

jake: mm.cc
	$(JAKE) -- $(CC) $(CFLAGS) $(TGINCLUDE) $(TGLIB) -ltaskgraph mm.cc -o mm.tgauto.exe

runjake:
	./mm.tgauto.exe

mopt: mm_manual_taskgraph.cc
	$(CC) $(CFLAGS) $(TGINCLUDE) $(TGLIB) -ltaskgraph mm_manual_taskgraph.cc -o mm.tgversion.exe

runmopt:
	./mm.tgversion.exe

clean:
	rm  -f mm.cversion.exe mm.profversion.exe mm.tgauto.exe mm.tgversion.exe mm_auto.cc
