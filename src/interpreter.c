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
			Py_DECREF(tmp->object);
		free(tmp);
	}

	free(list);
}

/*
 * Interpreter
 *
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
 * @param arg_types printf() like list of arguments. See Python documentation
 * @param ... arguments for the function
 * FIXME:why are default arguments necessary ?
 */

PyObject *executeFunction(Interpreter *interpreter, const char *module, const char *funcName, const char* format, ...)
{
	if (!Py_IsInitialized())
		Py_Initialize();

	// Make argument list
	PyObject *args;
	if (format == NULL)
		args = Py_None;
	else
	{
		va_list listArgs;
		va_start(listArgs, format);

		args = Py_VaBuildValue(format, listArgs);
	}

	// Look for the module.
	PyObject *mod = 0;
	if (interpreter->modules)
	{
		mod = moduleNamed(module, interpreter->modules);
	}
	if (!mod)
	{
		mod = PyImport_ImportModule(module);
		if (!mod)
			return NULL;
		insert(interpreter->modules, mod);
	}

	/*printf("mod: %p ", mod);
	PyObject_Print(mod, stdout, 0);
	printf("\n");*/

	// Look for the function
	PyObject *func = PyObject_GetAttrString(mod, funcName);
	if (!PyCallable_Check(func))
		return NULL;

	// Call the function
	/*printf("func: %p\n", func);
	PyObject_Print(func, stdout, 0);
	printf("\n");*/

	PyObject *val = PyObject_Call(func, args, NULL);

	// Add return value object in a local list so it can be DECREF'ed when the interpreter is deleted.
	// TODO
	Py_DECREF(args);

	return val;
}
/*
PyObject *executeMethod(PyObject *object, const char *methName, const char* format, ...)
{
	if (!Py_IsInitialized())
		Py_Initialize();

	// Make argument list
	PyObject *args;
	if (format == NULL)
		args = Py_None;
	else
	{
		va_list listArgs;
		va_start(listArgs, format);

		args = Py_VaBuildValue(format, listArgs);
	}

	PyObject *ret = PyObject_CallMethod(object, methName, )
}*/

int main(int argc, char *argv[])
{
	Interpreter *in = createInterpreter();

	executeFunction(in, "portage.data", "portage_group_warning", NULL);

	PyObject *arg1 = executeFunction(in, "portage", "pkgsplit", "sI", "app-portage/kuroo4-4.2", 1);
	PyObject *arg2 = executeFunction(in, "portage", "pkgsplit", "sI", "app-portage/kuroo4-4.1", 1);
	PyObject *ret = executeFunction(in, "portage", "pkgcmp", "OO", arg1, arg2);

	if (!ret)
		printf("failed :-( \n");
	else
		printf("Return %ld\n", PyLong_AsLong(ret));

	Py_DECREF(ret);
	Py_DECREF(arg1);
	Py_DECREF(arg2);
	
	PyObject *tbz = executeFunction(in, "portage.output", "ProgressBar", "sIs", "titre", 100, "status");
	ret = PyObject_CallMethod(tbz, "inc", "I", 25);
	Py_DECREF(tbz);
	Py_DECREF(ret);

	freeInterpreter(in);

	return 0;
}
