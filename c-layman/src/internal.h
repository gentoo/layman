#ifndef INTERNAL_H
#define INTERNAL_H

#include <Python.h>

#include "stringlist.h"
#include "dict.h"
#include "config.h"
#include "message.h"

 
PyObject *executeFunction(const char *module, const char *funcName, const char *format, ...);

PyObject *_ConfigObject(BareConfig*);

PyObject *_messagePyObject(Message *m);

StringList *listToCList(PyObject *list);
PyObject *cListToPyList(StringList*);

PyObject *dictToPyDict(Dict *dict);

/**
 * \internal
 * Stores modules in a linked list so that they don't have to be reloaded every time.
 */
typedef struct PyObjectListElem
{
	PyObject *object;
	struct PyObjectListElem *next;
}


typedef struct PyObjectList
{
	PyObjectListElem root;
	int count;
}


/**
 * \internal
 * A Python interpreter object keeps the context like the loaded modules.
 */
typedef struct Interpreter
{
	PyObjectList modules;
}


#endif
