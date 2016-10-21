
CC = g++
CFLAGS = -O3 -march=native

JAKE=${JAKEROOT}/src/jake.py


all: cversion jake

cversion: helloworld.c
	$(CC) $(CFLAGS) helloworld.c -o helloworld.exe

runcversion:
	./helloworld.exe | tee cversion.output

jake: helloworld.c
	$(JAKE) -- $(CC) $(CFLAGS) helloworld.c -o hw.jakeversion.exe

runjake:
	./hw.jakeversion.exe | tee jakeversion.output

compare:
	diff cversion.output jakeversion.output

clean:
	rm  -f *.exe *.output
