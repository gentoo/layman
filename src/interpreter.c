/*
 * Compile command :
 * gcc -o interpreter -W -Wall -g --std=c99 -I/usr/include/python3.1/ -lpython3.1 interpreter.c
 */
#include <Python.h>
#include <stdio.h>
#include <string.h>

/*
 * PyObjectList
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

PyObject *elementAt(PyObjectList* list, int pos)
{
	if (!list || list->count < pos)
		return NULL;

	PyObjectListElem *node = list->root;
	for (int i = 0; i < pos; i++)
	{
		node = node->next;
	}
	if (!node)
		return 0;

	return node->object;
}

PyObject *moduleNamed(const char *name, PyObjectList *list)
{
	PyObjectListElem *node = list->root;
	while (node)
	{
		if (strcmp(PyModule_GetName(node->object), name))
			return node->object;
		node = node->next;
	}
	
	return NULL;
}

PyObject *toTuple(PyObjectList *list)
{
	if (!list)
		return NULL;

	PyObject *ret = PyTuple_New(list->count);
	PyObjectListElem *node = list->root;
	int i = 0;
	while (node)
	{
		if (node->object)
			PyTuple_SetItem(ret, i++, node->object);
		node = node->next;
	}

	return ret;
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
			Py_DECREF(tmp->object);
		free(tmp);
	}

	free(list);
}

/*
 * Interpreter
 */

/*
 * A Python interpreter object keeps the context like the loaded modules.
 */

typedef struct Interpreter
{
	PyObjectList *modules;
} Interpreter;

Interpreter *createInterpreter()
{
	Interpreter *ret = malloc(sizeof(Interpreter));
	ret->modules = createObjectList();
	return ret;
}

void freeInterpreter(Interpreter *inter)
{
	if (!inter)
		return;
	freeList(inter->modules, 1);
	free(inter);

	Py_Finalize();
}

/*
 * printf() like function that executes a python function
 * @param interpreter Python interpreter object on which the function should be ran
 * @param module name of the python module in which the function is
 * @param funcName the function name to call
 * @param arg_types printf() like list of arguments TODO:explain more --> See Python documentation
 * @param ... arguments for the function
 */

PyObject *executeFunction(Interpreter *interpreter, const char *module, const char *funcName, const char* format, ...)
{
	if (!Py_IsInitialized())
		Py_Initialize();

	// Make arguments
	// FIXME: use Py_BuildValue.
	// FIXME: is it possible to pass this function's arguments to another function ?
	PyObjectList *argList = createObjectList();
	int i = 0;
	while (format[i] != '\0')
	{
		while(format[i] != '%' && format[i] != '\0')
			i++;
		
		if (format[i] == '\0')
			break;

		PyObject *arg = NULL;
		switch(format[++i])
		{
		case 'd': //number
			break;
		case 's': //string
			break;
		case 'P': //PyObject
			break;
		default: //skip or abort ?
			break;
		}

		insert(argList, arg);
		i++;
	}

	PyObject *args = toTuple(argList);
	freeList(argList, 1);

	// Look for the module.
	PyObject *mod = 0;
	if (interpreter->modules)
	{
		mod = moduleNamed(module, interpreter->modules);
	}
	if (!mod)
	{
		mod = PyImport_ImportModule(module);
		insert(interpreter->modules, mod);
	}

	// Look for the function
	PyObject *dict = PyModule_GetDict(mod);
	PyObject *func = PyDict_GetItemString(dict, funcName);

	if (!PyCallable_Check(func))
		return NULL;

	// Call the function
	PyObject *val = PyObject_CallObject(func, args);

	// Add return value object in a local list so it can be DECREF'ed when the interpreter is deleted.
	// TODO

	Py_DECREF(args);

	return val;
}


int main(int argc, char *argv[])
{
	Interpreter *in = createInterpreter();

	PyObject *ret = executeFunction(in, "portage.data", "portage_group_warning", "");

	if (!ret)
		printf("failed :-( \n");

	freeInterpreter(in);

	return 0;
}
