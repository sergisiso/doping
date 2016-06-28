
CC = g++
CFLAGS = -O3 -march=native

TGINCLUDE = -I$(TGPATH)/include -I/gpfs/stfc/local/apps/intel/boost/1.59.0/include
TGLIB = -L$(TGPATH)/lib -I/gpfs/stfc/local/apps/intel/boost/1.59.0/lib

all: cversion tgversion tgauto

cversion: mm.cc
	$(CC) $(CFLAGS) mm.cc -o mm.cversion

tgauto: mm_auto.cc
	$(CC) $(CFLAGS) $(TGINCLUDE) $(TGLIB) -ltaskgraph mm_auto.cc -o mm.tgauto

tgversion: mm_manual_taskgraph.cc
	$(CC) $(CFLAGS) $(TGINCLUDE) $(TGLIB) -ltaskgraph mm_manual_taskgraph.cc -o mm.tgversion
