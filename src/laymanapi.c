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
	PyObject *obj = executeFunction("layman.api", "LaymanAPI", "Oii", _bareConfigObject(config), report_error, output);
	if (!obj)
		return NULL;

	LaymanAPI *ret = malloc(sizeof(LaymanAPI));
	ret->object = obj;

	return ret;
}

StringList* laymanAPIGetAvailable(LaymanAPI* l, int reload)
{
	if (!l || !l->object)
		return NULL;

	PyObject *obj = PyObject_CallMethod(l->object, "get_available", "(i)", reload);
	StringList *ret = listToCList(obj);
	Py_DECREF(obj);

	return ret;
}

/*StringList* laymanAPIGetInstalled(LaymanAPI* l)
{
	return laymanAPIGetInstalled(l, 0);
}*/

StringList* laymanAPIGetInstalled(LaymanAPI* l, int reload)
{
	if (!l || !l->object)
		return NULL;

	PyObject *obj = PyObject_CallMethod(l->object, "get_installed", "(i)", reload);
	StringList* ret = listToCList(obj);
	Py_DECREF(obj);

	return ret;
}

int laymanAPISync(LaymanAPI* l, const char* overlay, int verbose)
{
	if (!l || !l->object)
		return 0;

	PyObject *obj = PyObject_CallMethod(l->object, "sync", "(si)", overlay, verbose);
	if (!obj)
		return 0;

	int ret;
	if (PyObject_IsTrue(obj))
		ret = 1;
	else
		ret = 0;
	
	Py_DECREF(obj);
	
	return ret;
}

int laymanAPIFetchRemoteList(LaymanAPI* l)
{
	if (!l || !l->object)
		return 0;
	
	PyObject *obj = PyObject_CallMethod(l->object, "fetch_remote_list", NULL);

	int ret;

	if (!PyObject_IsTrue(obj)) //FIXME : does this work ? It seems to return 1 when false and 0 when true
		ret = 1;
	else
		ret = 0;
	
	Py_DECREF(obj);

	return ret;
}

OverlayInfo *laymanAPIGetInfo(LaymanAPI* l, const char* overlay)
{
	if (!l || !l->object || !overlay)
		return NULL;

	PyObject *list = PyList_New(1);
	PyList_SetItem(list, 0, PyBytes_FromString(overlay));

	PyObject *obj = PyObject_CallMethod(l->object, "get_info", "(O)", list);
	Py_DECREF(list);

	if (!obj || !PyDict_Check(obj))
	{
		if (obj)
		{
			Py_DECREF(obj);
		}
		return NULL;
	}

	PyObject *tuple = PyDict_GetItemString(obj, overlay);

	if (!tuple || !PyTuple_Check(tuple))
	{
		if (tuple)
		{
			Py_DECREF(tuple);
		}
		Py_DECREF(obj);

		return NULL;
	}

	PyObject *text = PyTuple_GetItem(tuple, 0);
	PyObject *official = PyTuple_GetItem(tuple, 1);
	PyObject *supported = PyTuple_GetItem(tuple, 2);

	OverlayInfo *oi = malloc(sizeof(OverlayInfo));

	char* tmp = PyBytes_AsString(text);
	oi->text = malloc((strlen(tmp) + 1) * sizeof(char));
	strcpy(oi->text, tmp);

	oi->official = PyObject_IsTrue(official);
	oi->supported = PyObject_IsTrue(supported);

	Py_DECREF(obj);
	Py_DECREF(tuple);
	Py_DECREF(text);
	Py_DECREF(official);
	Py_DECREF(supported);

	return oi;
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
