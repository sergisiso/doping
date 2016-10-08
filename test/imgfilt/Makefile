
CC = g++
CFLAGS = -O3 -march=native

JAKE=${JAKEROOT}/src/jake.py

TGINCLUDE = -I$(TGPATH)/include
TGLIB = -L$(TGPATH)/lib

all: cversion mopt jake

cversion: imgfilt-cpp.cc
	$(CC) $(CFLAGS) imgfilt-cpp.cc -o if.cversion.exe

runcversion:
	./if.cversion.exe

jake: imgfilt-cpp.cc
	$(JAKE) -- $(CC) $(CFLAGS) imgfilt-cpp.cc -o if.jakeversion.exe

runjake:
	./if.jakeversion.exe

mopt: imgfilt-tg.cc
	$(CC) $(CFLAGS) $(TGINCLUDE) $(TGLIB) -ltaskgraph imgfilt-tg.cc -o if.tgversion.exe

runmopt:
	./if.tgversion.exe

clean:
	rm  -f *.exe 
