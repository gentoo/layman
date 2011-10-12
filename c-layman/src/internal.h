#ifndef INTERNAL_H
#define INTERNAL_H

#include <Python.h>
// temp workaround for my environment
// since at times it fails to find Python.h
#include <python2.6/Python.h>

#include "stringlist.h"
#include "dict.h"
#include "config.h"
#include "message.h"

 
PyObject *executeFunction(const char *module, const char *funcName, const char *format, ...);

PyObject *_ConfigObject(BareConfigStruct*);

PyObject *_messagePyObject(MessageStruct *m);

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
} PyObjectListElem;


typedef struct PyObjectList
{
	PyObjectListElem root;
	int count;
} PyObjectList;


/**
 * \internal
 * A Python interpreter object keeps the context like the loaded modules.
 */
typedef struct PythonInterpreter
{
	PyObjectList modules;
	void  (* execute) (PythonInterpreter *interpreter,
								const char *module,
								const char *funcName,
								const char *format,
								...);

} PythonInterpreter;


#endif
