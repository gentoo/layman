#!/bin/bash
echo Compile lib :
make

echo Compile tester:
gcc src/tester.c -llayman -g -W -Wall -I/usr/include/python2.6/ -Isrc/ -L.libs/ --std=c99 -o tester

echo Run :
LD_LIBRARY_PATH=.libs/ ./tester
