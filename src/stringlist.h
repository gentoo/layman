#ifndef STRINGLIST_H
#define STRINGLIST_H

#include <Python.h>

typedef struct StringList StringList;

StringList* stringListCreate(size_t);
StringList* listToCList(PyObject* list);
PyObject* cListToPyList(StringList*);
void stringListPrint(StringList*);
void stringListFree(StringList*);

#endif
