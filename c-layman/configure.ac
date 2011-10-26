AC_INIT()
 
AC_PROG_CC
 
PACKAGE=layman
VERSION=0.1
 
AM_INIT_AUTOMAKE($PACKAGE, $VERSION)

LT_INIT([disable-static])

# Get Python 2.6 library and include locations
AC_ARG_WITH([python-include-path],
  [AS_HELP_STRING([--with-python-include-path],
    [location of the Python 2.6 headers, defaults to /usr/include/python2.6])],
  [PYTHON_CFLAGS="-I$withval"],
  [PYTHON_CFLAGS='-I/usr/include/python2.6'])
AC_SUBST([PYTHON_CFLAGS])

AC_ARG_WITH([python-lib-path],
  [AS_HELP_STRING([--with-python-lib-path], [location of the Python 2.6 library])],
  [PYTHON_LIBS="-L$withval -lpython2.6"],
  [PYTHON_LIBS='-lpython2.6'])
AC_SUBST([PYTHON_LIBS])
 
AC_OUTPUT(Makefile src/Makefile)
