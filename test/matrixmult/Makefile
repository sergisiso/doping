
CC = g++
CFLAGS = -O3 -march=native

TGPATH = /home/sergi/jake/deps/taskgraph-20140613/install

TGINCLUDE = -I$(TGPATH)/include
TGLIB = -L$(TGPATH)/lib

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
