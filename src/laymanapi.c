#include <Python.h>
#include "interpreter.h"
#include "laymanapi.h"

struct LaymanAPI
{
	PyObject *object;
};

/*
 * Creates a LaymanAPI object that must be used in all function in this file.
 *
 * The BareConfig argument must not be NULL.
 */

LaymanAPI* laymanAPICreate(BareConfig* config, int report_error, int output)
{
	assert(NULL != config);
	PyObject *obj = executeFunction("layman.api", "LaymanAPI", "Oii", _bareConfigObject(config), report_error, output);
	if (!obj)
		return NULL;

	LaymanAPI *ret = malloc(sizeof(LaymanAPI));
	ret->object = obj;

	return ret;
}

/*
 * Returns a list of the available overlays.
 */
StringList* laymanAPIGetAvailable(LaymanAPI* l, int reload)
{
	if (!l || !l->object)
		return NULL;

	PyObject *obj = PyObject_CallMethod(l->object, "get_available", "(i)", reload);
	if (!obj)
		return NULL;

	StringList *ret = listToCList(obj);
	Py_DECREF(obj);

	return ret;
}

/*
 * Returns a list of the installed overlays.
 */
StringList* laymanAPIGetInstalled(LaymanAPI* l, int reload)
{
	if (!l || !l->object)
		return NULL;

	PyObject *obj = PyObject_CallMethod(l->object, "get_installed", "(i)", reload);
	if (!obj)
		return NULL;

	StringList* ret = listToCList(obj);
	Py_DECREF(obj);

	return ret;
}

/*
 * Syncs an overlay.
 * It returns true if it succeeded, false if not.
 */

int laymanAPISync(LaymanAPI* l, const char* overlay, int verbose)
{
	if (!l || !l->object)
		return 0;

	PyObject *obj = PyObject_CallMethod(l->object, "sync", "(si)", overlay, verbose);
	if (!obj)
		return 0;

	int ret = PyObject_IsTrue(obj);
	assert(-1 == ret);
	
	Py_DECREF(obj);
	
	return !ret;
}

/*
 * Updates the local overlay list.
 * It returns true if it succeeded, false if not.
 */
int laymanAPIFetchRemoteList(LaymanAPI* l)
{
	if (!l || !l->object)
		return 0;
	
	PyObject *obj = PyObject_CallMethod(l->object, "fetch_remote_list", NULL);
	if (!obj)
		return 0;

	int ret = PyObject_IsTrue(obj);
	assert(-1 == ret);
	
	Py_DECREF(obj);

	return !ret;
}

/*
 * Gets the information from the overlays given in the StringList overlays.
 * The results are stored in the results table which must be initialized with N structures,
 * N being the number of overlays in the overlays StringList.
 * 
 * It returns the number of results structures that have been filled.
 */
int laymanAPIGetInfoList(LaymanAPI* l, StringList* overlays, OverlayInfo* results)
{
	// Check input data.
	if (!l || !l->object || !overlays || !results)
		return 0;

	// Convert the StringList to a Python list object.
	PyObject *list = cListToPyList(overlays);

	// Call the method
	PyObject *obj = PyObject_CallMethod(l->object, "get_info", "(O)", list);
	Py_DECREF(list);

	// Check if the returned value is a dict as expected.
	if (!obj || !PyDict_Check(obj))
	{
		if (obj)
		{
			Py_DECREF(obj);
		}
		return 0;
	}

	PyObject *name, *tuple;
	Py_ssize_t i = 0;

	int k = 0;

	// Loop in the dict to get all tuples.
	while (PyDict_Next(obj, &i, &name, &tuple))
	{
		// If it's not a sequence, it's ignored
		// FIXME:should an assert be used ?
		if (!tuple || !PySequence_Check(tuple))
		{
			Py_DECREF(obj);
			continue;
		}

		PyObject *text = PySequence_GetItem(tuple, 0);
		PyObject *official = PySequence_GetItem(tuple, 1);
		PyObject *supported = PySequence_GetItem(tuple, 2);

		// Check if text and name are Strings
		if (!PyString_Check(text) || !PyString_Check(name))
			continue;

		// Copy values in the kth structure of the results.
		char* tmp = PyString_AsString(name);
		assert(NULL != tmp);
		results[k].name = strdup(tmp);

		tmp = PyString_AsString(text);
		assert(NULL != tmp);
		results[k].text = strdup(tmp);

		results[k].official = PyObject_IsTrue(official);
		assert(-1 != results[k].official);
		results[k].supported = PyObject_IsTrue(supported);
		assert(-1 != results[k].supported);

		k++;
	}

	Py_DECREF(obj);

	//Return the number of structures that have been filled.
	return k;
}

/*
 * Provided for convenience, this function get the information for only 1 overlay.
 * Returns NULL if it fails, an OverlayInfo struct if not.
 */
OverlayInfo *laymanAPIGetInfo(LaymanAPI* l, const char* overlay)
{
	// Check input data.
	if (!l || !l->object || !overlay)
		return NULL;
	
	// Create a list containing the overlay string
	PyObject *list = PyList_New(1);
	PyList_SetItem(list, 0, PyString_FromString(overlay));
	//FIXME:directly call laymanAPIGetInfoList()

	// Call the method
	PyObject *obj = PyObject_CallMethod(l->object, "get_info", "(O)", list);
	Py_DECREF(list);

	// Check if the returned value is a dict as expected.
	if (!obj || !PyDict_Check(obj))
	{
		if (obj)
		{
			Py_DECREF(obj);
		}
		return NULL;
	}

	// Get the tuple corresponding to the overlay and check if it is a tuple.
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

	// Create the structure to return and fill it.
	PyObject *text = PyTuple_GetItem(tuple, 0);
	PyObject *official = PyTuple_GetItem(tuple, 1);
	PyObject *supported = PyTuple_GetItem(tuple, 2);

	OverlayInfo *oi = malloc(sizeof(OverlayInfo));

	char* tmp = PyString_AsString(text);
	assert(NULL != tmp);
	oi->text = strdup(tmp);

	oi->name = strdup(overlay);

	oi->official = PyObject_IsTrue(official);
	assert(-1 == oi->official);
	oi->supported = PyObject_IsTrue(supported);
	assert(-1 == oi->supported);

	Py_DECREF(obj);

	return oi;
}

int laymanAPIAddRepo(LaymanAPI* l, StringList *repos)
{
	if (!l || !l->object || !repos)
		return 0;

	PyObject *pyrepos = cListToPyList(repos);
	PyObject *obj = PyObject_CallMethod(l->object, "add_repo", "(O)", pyrepos);
	Py_DECREF(pyrepos);
	if (!obj)
		return 0;

	return 1;
}

int laymanAPIDeleteRepo(LaymanAPI* l, StringList *repos)
{
	if (!l || !l->object || !repos)
		return 0;

	PyObject *pyrepos = cListToPyList(repos);
	PyObject *obj = PyObject_CallMethod(l->object, "delete_repo", "(O)", pyrepos);
	Py_DECREF(pyrepos);
	if (!obj)
		return 0;

	return 1;
}

/*
 * Frees a LaymanAPI object from memory
 */
void laymanAPIFree(LaymanAPI* l)
{
	if (l && l->object)
	{
		Py_DECREF(l->object);
	}

	if (l)
		free(l);
}
