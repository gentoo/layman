#!/bin/bash
echo Compile lib :
make
echo 
echo libs compiled and linked

echo
echo Compile tester:
gcc src/tester.c -llayman -g -W -Wall -Isrc/ -L.libs/ --std=c99 -o tester

echo
echo Run :
LD_LIBRARY_PATH=.libs/ ./tester
