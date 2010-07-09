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

Interpreter *in = 0;

/*
 * printf() like function that executes a python function
 * @param interpreter Python interpreter object on which the function should be ran
 * @param module name of the python module in which the function is
 * @param funcName the function name to call
 * @param arg_types printf() like list of arguments. See Python documentation
 * @param ... arguments for the function
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
	if (!mod)
	{
		mod = PyImport_ImportModule(module);
		if (!mod)
			return NULL;
		insert(in->modules, mod);
	}

	//printf("Using module named %s\n", PyModule_GetName(mod));

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

	//PyObject_Print(args, stdout, 0);
	//printf("\n");

	PyObject *val = PyObject_CallObject(func, args);

	if (args != NULL)
		Py_DECREF(args);

	return val;
}

typedef struct Overlay Overlay;

struct Overlay
{
	PyObject *object;
};

/*
 * FIXME: should the xml argument be an expat element ?
 */
Overlay *createOverlay(const char *xml, const char *config, int ignore, int quiet)
{
	//First argument must be a xml.etree.Element
	//PyObject *elem = executeFunction("layman.overlays.overlay", "testfunc", NULL);
	PyObject *elem = executeFunction("xml.etree.ElementTree", "fromstring", "(s)", xml);
	if (!elem)
		return NULL;

	config = config;
	PyObject *cfg = PyDict_New();
	if (!cfg)
		return NULL;

	PyObject *overlay = executeFunction("layman.overlays.overlay", "Overlay", "(OOIb)", elem, cfg, ignore, quiet);
	if (!overlay)
		return NULL;
	Overlay *ret = malloc(sizeof(Overlay));
	ret->object = overlay;

	return ret;
}

const char *overlayName(Overlay *o)
{
	if (!o || !o->object)
		return NULL;

	PyObject *name = PyObject_GetAttrString(o->object, "name");

	//TODO:Py_DECREF me !

	return PyBytes_AsString(name);
}

const char *overlayOwnerEmail(Overlay *o)
{
	if (!o || !o->object)
		return NULL;

	PyObject *ret = PyObject_GetAttrString(o->object, "owner_email");

	//TODO:Py_DECREF me !

	return PyBytes_AsString(ret);
}

int overlayPriority(Overlay *o)
{
	if (!o || !o->object)
		return -1;

	PyObject *prio = PyObject_GetAttrString(o->object, "priority");

	//TODO:Py_DECREF me !

	return (int) PyLong_AsLong(prio);
}

const char *overlayDescription(Overlay *o)
{
	if (!o || !o->object)
		return NULL;

	PyObject *desc = PyObject_GetAttrString(o->object, "description");

	//TODO:Py_DECREF me !

	return PyBytes_AsString(desc);
}

int overlayIsOfficial(Overlay *o)
{
	if (!o || !o->object)
		return -1;

	PyObject *iso = PyObject_CallMethod(o->object, "is_official", NULL);

	//TODO:Py_DECREF me !

	return (int) PyLong_AsLong(iso);
}

int main(int argc, char *argv[])
{
	in = createInterpreter();
	
	Overlay *o = createOverlay("<overlay type='svn' src='https://overlays.gentoo.org/svn/dev/wrobel' contact='nobody@gentoo.org' name='wrobel' status='official' priorit='10'><description>Test</description></overlay>", "", 1, 0);

	if (!o)
	{
		printf("Error creating overlay.\n");
		return 0;
	}
	
	printf("Overlay name = %s, owner email : %s, description : %s, priority : %d, it is %sofficial.\n", overlayName(o), overlayOwnerEmail(o), overlayDescription(o), overlayPriority(o), overlayIsOfficial(o) ? "" : "not ");

	freeInterpreter(in);

	return 0;
}
