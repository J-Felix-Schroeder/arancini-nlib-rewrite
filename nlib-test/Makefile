MUSL = REALGCC=x86_64-linux-gnu-gcc ../autoidl/musl/musl-x86_64/bin/musl-gcc -O2 -fno-tree-vectorize -idirafter /usr/include -no-pie
FLIB = ../autoidl/out/flib

TESTS = primitives snake debug-text rotating-textures simple-playback simple-playback-callback example zpipe

all: $(TESTS:%=bin/%)

LIB = libSDL3.so.0
bin/example bin/zpipe: LIB = libz.so.1

bin/%: src/%.c
	$(MUSL) src/$*.c $(FLIB)/$(LIB) -o bin/$*

clean:
	rm -f bin/*
