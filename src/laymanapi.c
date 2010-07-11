#include <Python.h>
#include "interpreter.h"
#include "laymanapi.h"

/*
 * FIXME: free memory !!!
 */

struct LaymanAPI
{
	PyObject *object;
};

OverlayInfo strToInfo(const char* str)
{
	OverlayInfo ret;
	return ret;
}

LaymanAPI* laymanAPICreate(BareConfig* config, int report_error, int output)
{
	PyObject *obj = executeFunction("layman.api", "LaymanAPI", "OII", _bareConfigObject(config), report_error, output);
	if (!obj)
		return NULL;

	LaymanAPI *ret = malloc(sizeof(LaymanAPI));
	ret->object = obj;

	return ret;
}

StringList* laymanAPIGetAvailable(LaymanAPI* l)
{
	if (!l || !l->object)
		return NULL;

	PyObject *obj = PyObject_CallMethod(l->object, "get_available", NULL);
	StringList* ret = listToCList(obj);
	Py_DECREF(obj);

	return ret;
}

StringList* laymanAPIGetInstalled(LaymanAPI* l)
{
	if (!l || !l->object)
		return NULL;

	PyObject *obj = PyObject_CallMethod(l->object, "get_installed", NULL);
	StringList* ret = listToCList(obj);
	Py_DECREF(obj);

	return ret;
}

int laymanAPISync(LaymanAPI* l, const char* overlay)
{
	if (!l || !l->object)
		return EXIT_FAILURE;

	PyObject *list = PyList_New(1);
	PyList_Insert(list, 0, PyBytes_FromString(overlay));

	PyObject *obj = PyObject_CallMethod(l->object, "sync", "O", list);
	Py_DECREF(list);

	if (!obj)
		return EXIT_FAILURE;

	PyObject *success = PyList_GetItem(obj, 1);
	if (success == Py_None)
		return EXIT_FAILURE;
	
	return EXIT_SUCCESS;
}

int laymanAPIFetchRemoteList(LaymanAPI* l)
{
	if (!l || !l->object)
		return EXIT_FAILURE;
	
	PyObject *obj = PyObject_CallMethod(l->object, "fetch_remote_list", NULL);

	int ret;

	if (PyObject_IsTrue(obj))
		ret = EXIT_SUCCESS;
	else
		ret = EXIT_FAILURE;
	
	Py_DECREF(obj);

	return ret;
}

const char* laymanAPIGetInfo(LaymanAPI* l, const char* overlay)
{
	if (!l || !l->object)
		return NULL;

	PyObject *list = PyList_New(1);
	PyList_Insert(list, 0, PyBytes_FromString(overlay));

	PyObject *obj = PyObject_CallMethod(l->object, "get_info", "O", list);
	Py_DECREF(list);

	if (!obj)
		return NULL;

	PyObject *result = PyList_GetItem(obj, 0);
	char* tmp = PyBytes_AsString(result);
	char* ret = malloc((strlen(tmp) + 1) * sizeof(char));
	strcpy(ret, tmp);
	Py_DECREF(result);

	return ret;
	//TODO:also return 'official' an 'supported' (see laymanapi.h)
}

void laymanAPIFree(LaymanAPI* l)
{
	if (l && l->object)
	{
		Py_DECREF(l->object);
	}

	if (l)
		free(l);
}
