#ifndef STRINGLIST_H
#define STRINGLIST_H

#include <Python.h>

typedef struct StringList StringList;

StringList*	stringListCreate(size_t);
unsigned int	stringListCount(StringList*);
int		stringListInsertAt(StringList*, unsigned int, const char*);
char*		stringListGetAt(StringList*, unsigned int);
StringList*	listToCList(PyObject* list);
PyObject*	cListToPyList(StringList*);
void		stringListPrint(StringList*);
void		stringListFree(StringList*);

#endif
