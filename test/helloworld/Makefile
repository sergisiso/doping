
CC = g++
CFLAGS = -O3 -march=native

JAKE=/home/sergi/jake/jake
TGPATH = /home/sergi/jake/deps/taskgraph-20140613/install

TGINCLUDE = -I$(TGPATH)/include
TGLIB = -L$(TGPATH)/lib

all: cversion mopt jake

cversion: helloworld.c
	$(CC) $(CFLAGS) helloworld.c -o helloworld.exe

runcversion:
	./helloworld.exe

jake: helloworld.c
	$(JAKE) helloworld.c hw_auto.c
	$(CC) $(CFLAGS) $(TGINCLUDE) $(TGLIB) -ltaskgraph hw_auto.c -o hw.tgauto.exe

runjake:
	./hw.tgauto.exe

mopt: helloworld.c
	$(CC) $(CFLAGS) $(TGINCLUDE) $(TGLIB) -ltaskgraph helloworld.c -o hw.tgversion.exe

runmopt:
	./hw.tgversion.exe

clean:
	rm  -f *.exe hw_auto.c
