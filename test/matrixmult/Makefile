
CC = g++
CFLAGS = -O3 -march=native

TGINCLUDE = -I$(TGPATH)/include -I/gpfs/stfc/local/apps/intel/boost/1.59.0/include
TGLIB = -L$(TGPATH)/lib -I/gpfs/stfc/local/apps/intel/boost/1.59.0/lib

all: cversion profversion tgversion tgauto

cversion: mm.cc
	$(CC) $(CFLAGS) mm.cc -o mm.cversion.exe

profversion: mm_profile.cc
	$(CC) $(CFLAGS) mm_profile.cc -o mm.profversion.exe

tgauto: mm_auto.cc
	$(CC) $(CFLAGS) $(TGINCLUDE) $(TGLIB) -ltaskgraph mm_auto.cc -o mm.tgauto.exe

tgversion: mm_manual_taskgraph.cc
	$(CC) $(CFLAGS) $(TGINCLUDE) $(TGLIB) -ltaskgraph mm_manual_taskgraph.cc -o mm.tgversion.exe

clean:
	rm  -f mm.cversion.exe mm.profversion.exe mm.tgauto.exe mm.tgversion.exe
