
CC = g++
CFLAGS = -O3 -march=native

JAKE=/home/sergi/jake/jake
TGPATH = /home/sergi/jake/deps/taskgraph-20140613/install

TGINCLUDE = -I$(TGPATH)/include
TGLIB = -L$(TGPATH)/lib

all: cversion mopt jake

cversion: imgfilt-cpp.cc
	$(CC) $(CFLAGS) imgfilt-cpp.cc -o if.cversion.exe

runcversion:
	./if.cversion.exe

jake: imgfilt-cpp.cc
	$(JAKE) imgfilt-cpp.cc if_auto.cc
	$(CC) $(CFLAGS) $(TGINCLUDE) $(TGLIB) -ltaskgraph if_auto.cc -o if.tgauto.exe

runjake:
	./if.tgauto.exe

mopt: imgfilt-tg.cc
	$(CC) $(CFLAGS) $(TGINCLUDE) $(TGLIB) -ltaskgraph imgfilt-tg.cc -o if.tgversion.exe

runmopt:
	./if.tgversion.exe

clean:
	rm  -f *.exe if_auto.cc
