MUSL = x86_64-linux-musl-gcc -O2 -fno-tree-vectorize -idirafter /usr/include -no-pie
FLIB = ../autoidl/out/flib

TESTS = primitives snake debug-text rotating-textures simple-playback simple-playback-callback example zpipe qsort strlen

all: $(TESTS:%=bin/%)

LIB = $(FLIB)/libSDL3.so.0
bin/example bin/zpipe: LIB = $(FLIB)/libz.so.1
bin/qsort bin/strlen: LIB =

bin/%: src/%.c
	$(MUSL) src/$*.c $(LIB) -o bin/$*

clean:
	rm -f bin/*
