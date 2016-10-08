
CC = g++
CFLAGS = -O3 -march=native

JAKE=${JAKEROOT}/src/jake.py


all: cversion mopt jake

cversion: helloworld.c
	$(CC) $(CFLAGS) helloworld.c -o helloworld.exe

runcversion:
	./helloworld.exe

jake: helloworld.c
	$(JAKE) -- $(CC) $(CFLAGS) helloworld.c -o hw.jakeversion.exe

runjake:
	./hw.jakeversion.exe

clean:
	rm  -f *.exe hw_auto.c
