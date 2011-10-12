#include <Python.h>
// temp workaround for my environment
// since at times it fails to find Python.h
#include <python2.6/Python.h>
#include <stdio.h>
#include <string.h>

#include "interpreter.h"
#include "internal.h"


static PyObjectList			py_create_ObjectList();
static void						py_ObjectList_insert(PyObjectList list, PyObject *object);
static int 						py_ObjectList_Count(PyObjectList list);
static PyObject 			*	py_moduleNamed(const char *name, PyObjectList list);
static void 						py_ObjectList_free(PyObjectList list, int deref);
static void 						py_Initialize(PythonInterpreter *interpreter);
static void 						py_Finalize(PythonInterpreter *interpreter);
static PyObject 			*	py_executeFunction(PythonInterpreter *interpreter,
																		const char *module,
																		const char *funcName,
																		const char *format,
																		...);





static PyObjectList
py_create_ObjectList()
{
	PyObjectList *ret = malloc(sizeof(PyObjectList));
	ret->count = 0;
	ret->root = 0;
	return ret;
}


static void 
py_ObjectList_insert(PyObjectList list, PyObject *object)
{
	if (!list || !object)
		return;
	PyObjectListElem node = malloc(sizeof(PyObjectListElem));
	node->object = object;
	node->next = list->root;
	list->root = node;
	list->count++;
}

static PyObject *
py_moduleNamed(const char *name, PyObjectList list)
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

static int 
py_ObjectList_Count(PyObjectList list)
{
	return (list ? list->count : 0);
}

static void 
py_ObjectList_free(PyObjectList list, int deref)
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


/** \defgroup base Layman base
 * 
 * \brief Base functions
 *
 * These functions are used when you want to begin or end using the library.
 */

/** \addtogroup base
 * @{
 */


/**
 * This is the first function that must be called before using the library.
 * It initializes the Python interpreter.
 */
static void 
py_Initialize(PythonInterpreter *interpreter)
{
	if (interpreter)
		return;

	if (!Py_IsInitialized())
		Py_Initialize();

	interpreter = malloc(sizeof(struct session->Interpreter));
	interpreter->modules = createObjectList();
	interpreter->execute = py_executeFunction;
}

/**
 * Call this function when you're done using the library.
 * It will free memory.
 */
static void 
py_Finalize(PythonInterpreter *interpreter)
{
	if (!nterpreter)
		return;
	freeList(interpreter->modules, 1);
	free(interpreter);
	interpreter = NULL;

	if (Py_IsInitialized())
		Py_Finalize();
}

/** @} */

/**
 * \internal
 * printf() like function that executes a python function
 *
 * \param module name of the python module in which the function is
 * \param funcName the function name to call
 * \param format printf() like list of arguments. See Python documentation
 * \param ... arguments for the function
 *
 * \return the result of the execution. Can be NULL if the call failed.
 */
static PyObject *
py_executeFunction(PythonInterpreter *interpreter, const char *module, 
								const char *funcName, const char *format, ...)
{

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
	if (session->interpreter->modules)
	{
		mod = moduleNamed(module, interpreter->modules);
	}
	// If module is not loaded yet, do it.
	if (!mod)
	{
		mod = PyImport_ImportModule(module);
		if (!mod)
			return NULL;
		insert(interpreter->modules, mod);
	}

	// Look for the function
	PyObject *func = PyObject_GetAttrString(mod, funcName);
	if (!PyCallable_Check(func))
		return NULL;

	// Execute it
	PyObject *val = PyObject_CallObject(func, args);

	Py_XDECREF(args);

	return val;
}


/** Opens an interactive python session */
PythonSessionStruct
PySession_create()
{
	PythonSessionStruct session;
	py_Initialize(session);
	session->Finalize = py_Finalize;
	return session;
}

/** Closes an interactive python session */
void
PySession_free(PythonSessionStruct *session)
{
	py_Finalize(session->interpreter);
	free(session);
}
