#ifndef DICT_H
#define DICT_H

#include <Python.h>

typedef struct Dict Dict;

Dict*		dictCreate();
//char*		tableFind(Dict *table, char* key);
void		dictFree(Dict *t, int);
void		dictInsert(Dict* list, const char* key, const char* value);
unsigned int	dictCount(Dict *table);
PyObject*	dictToPyDict(Dict *dict);
#endif
