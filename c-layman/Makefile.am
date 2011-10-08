AUTOMAKE_OPTIONS = subdir-objects
ACLOCAL_AMFLAGS = ${ACLOCAL_FLAGS}
lib_LTLIBRARIES = liblayman.la
 
AM_CFLAGS = $(PYTHON_CFLAGS) --std=c99 -W -Wall
 
liblayman_la_SOURCES = src/config.c src/dict.c src/interpreter.c src/laymanapi.c src/message.c src/stringlist.c src/layman.c
#src/tester.c
liblayman_la_LIBADD = $(PYTHON_LIBS)

layman_includedir = $(includedir)/layman
layman_include_HEADERS = src/layman.h src/config.h src/dict.h src/interpreter.h src/laymanapi.h src/message.h src/stringlist.h

#bin_PROGRAMS = tester

#AM_CFLAGS = $(PYTHON_CFLAGS) --std=c99 -W -Wall
  
#tester_SOURCES = tester.c
#tester_LDADD = $(PYTHON_LIBS) -llayman

#pkgconfigdir = $(libdir)/pkgconfig
#pkgconfig_DATA = layman.pc

#dist_noinst_SCRIPTS = autogen.sh
