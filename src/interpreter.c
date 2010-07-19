/*
 * Compile command :
 * gcc -o interpreter -W -Wall -g --std=c99 -I/usr/include/python3.1/ -lpython3.1 interpreter.c
 */
#include <Python.h>
#include <stdio.h>
#include <string.h>
#include "interpreter.h"

/**
 * PyObjectList
 * Stores modules in a linked list so that they don't have to be reloaded every time.
 */
typedef struct PyObjectListElem
{
	PyObject *object;
	struct PyObjectListElem *next;
} PyObjectListElem;

typedef struct PyObjectList
{
	PyObjectListElem *root;
	int count;
} PyObjectList;

PyObjectList *createObjectList()
{
	PyObjectList *ret = malloc(sizeof(PyObjectList));
	ret->count = 0;
	ret->root = 0;
	return ret;
}

void insert(PyObjectList* list, PyObject *object)
{
	if (!list || !object)
		return;
	PyObjectListElem *node = malloc(sizeof(PyObjectListElem));
	node->object = object;
	node->next = list->root;
	list->root = node;
	list->count++;
}

PyObject *moduleNamed(const char *name, PyObjectList *list)
{
	PyObjectListElem *node = list->root;
	while (node)
	{
		if (strcmp(PyModule_GetName(node->object), name) == 0)
			return node->object;
		node = node->next;
	}
	
	return NULL;
}

int listCount(PyObjectList *list)
{
	return (list ? list->count : 0);
}

void freeList(PyObjectList *list, int deref)
{
	if (!list)
		return;

	PyObjectListElem *node = list->root;
	while (node)
	{
		PyObjectListElem *tmp = node;
		node = node->next;
		if (deref)
		{
			Py_DECREF(tmp->object);
		}
		free(tmp);
	}

	free(list);
}

/*
 * Interpreter
 *
 * A Python interpreter object keeps the context like the loaded modules.
 */

struct Interpreter
{
	PyObjectList *modules;
} *in = 0;

/**
 * This is the first function that must be called before using the library.
 */
void laymanInit()
{
	if (in)
		return;

	if (!Py_IsInitialized())
		Py_Initialize();

	in = malloc(sizeof(struct Interpreter));
	in->modules = createObjectList();
}

/**
 * Call this function when you're done using the library.
 * It will free memory.
 */
void laymanFinalize()
{
	if (!in)
		return;
	freeList(in->modules, 1);
	free(in);

	if (Py_IsInitialized())
		Py_Finalize();
}

/**
 * printf() like function that executes a python function
 *
 * \param module name of the python module in which the function is
 * \param funcName the function name to call
 * \param format printf() like list of arguments. See Python documentation
 * \param ... arguments for the function
 *
 * \return the result of the execution. Can be NULL if the call failed.
 */
PyObject *executeFunction(const char *module, const char *funcName, const char* format, ...)
{
	if (!Py_IsInitialized())
		Py_Initialize();

	// Make argument list
	PyObject *args;
	if (format == NULL || strcmp(format, "") == 0)
		args = PyTuple_New(0);
	else
	{
		va_list listArgs;
		va_start(listArgs, format);

		args = Py_VaBuildValue(format, listArgs);
	}

	// Look for the module.
	PyObject *mod = 0;
	if (in->modules)
	{
		mod = moduleNamed(module, in->modules);
	}
	// If module is not loaded yet, do it.
	if (!mod)
	{
		mod = PyImport_ImportModule(module);
		if (!mod)
			return NULL;
		insert(in->modules, mod);
	}

	// Look for the function
	PyObject *func = PyObject_GetAttrString(mod, funcName);
	if (!PyCallable_Check(func))
		return NULL;

	// Execute it
	PyObject *val = PyObject_CallObject(func, args);

	if (args != NULL)
	{
		Py_DECREF(args);
	}

	return val;
}
