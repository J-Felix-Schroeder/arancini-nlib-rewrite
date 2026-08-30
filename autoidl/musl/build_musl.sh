#!/bin/bash
curl -O https://musl.libc.org/releases/musl-1.2.5.tar.gz
tar xf musl-1.2.5.tar.gz
cd musl-1.2.5
./configure --prefix="$PWD/../musl-x86_64" CROSS_COMPILE=x86_64-linux-gnu-
make
make install
