#ifndef INTERNAL_H
#define INTERNAL_H

#include <Python.h>
#include "stringlist.h"
#include "dict.h"
#include "config.h"
#include "message.h"

PyObject*	executeFunction(const char *module, const char *funcName, const char* format, ...);

PyObject* 	_bareConfigObject(BareConfig*);

PyObject*	_messageObject(Message* m);

StringList*	listToCList(PyObject* list);
PyObject*	cListToPyList(StringList*);

PyObject*	dictToPyDict(Dict *dict);

#endif
