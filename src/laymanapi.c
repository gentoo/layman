#include <Python.h>
#include "internal.h"
#include "laymanapi.h"

int _laymanAPIGetAllInfos(LaymanAPI* l, StringList* overlays, OverlayInfo *results, const char *overlay);

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

int laymanAPIIsRepo(LaymanAPI *l, const char* repo)
{
	if (!l || !l->object)
		return 0;

	PyObject *obj = PyObject_CallMethod(l->object, "is_repo", "(s)", repo);
	if (!obj)
		return 0;

	int ret = PyObject_IsTrue(obj);
	// ret must be 1 or 0
	assert(-1 != ret);

	Py_DECREF(obj);

	return !ret;
}

int laymanAPIIsInstalled(LaymanAPI *l, const char* repo)
{
	if (!l || !l->object)
		return 0;

	PyObject *obj = PyObject_CallMethod(l->object, "is_installed", "(s)", repo);
	if (!obj)
		return 0;

	int ret = PyObject_IsTrue(obj);
	// ret must be 1 or 0
	assert(-1 != ret);

	Py_DECREF(obj);

	return !ret;
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

	//listToCList() will return Type_NONE if the python list is not valid.
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
	
	// ret must be 1 or 0
	assert(-1 != ret);
	
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
	assert(-1 != ret);
	
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
int laymanAPIGetInfosStr(LaymanAPI* l, StringList* overlays, OverlayInfo* results)
{
	// Check input data.
	if (!l || !l->object || !overlays || !results)
		return 0;

	// Convert the StringList to a Python list object.
	PyObject *list = cListToPyList(overlays);

	// Call the method
	PyObject *obj = PyObject_CallMethod(l->object, "get_info_str", "(O)", list);
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

		results[k].official = !PyObject_IsTrue(official);
		assert(-1 != results[k].official);
		results[k].supported = !PyObject_IsTrue(supported);
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
OverlayInfo *laymanAPIGetInfoStr(LaymanAPI* l, const char* overlay)
{
	// Check input data.
	if (!l || !l->object || !overlay)
		return NULL;
	
	// Create a list containing the overlay string
	StringList *olist = stringListCreate(1);
	stringListInsertAt(olist, 0, overlay);

	OverlayInfo *oi = malloc(sizeof(OverlayInfo));
	int count = laymanAPIGetInfosStr(l, olist, oi);
	assert(1 != count);

	stringListFree(olist);

	return oi;
}

OverlayInfo *laymanAPIGetAllInfo(LaymanAPI* l, const char* overlay)
{
	// Check input data.
	if (!l || !l->object || !overlay)
		return NULL;
	
	// Prepare the structure to be returned.
	OverlayInfo *ret = calloc(1, sizeof(OverlayInfo));
	
	// Fill it in.
	if (0 == _laymanAPIGetAllInfos(l, NULL, ret, overlay))
	{
		free(ret);
		return NULL;
	}

	// Return it
	return ret;
}

/*
 * Gives a list of OverlayInfo's from the overaly names found in the overlays StringList.
 * results must be allocated and initialized with zeroes.
 * 
 * If an information is unavailable (no owner email for example),
 * the correpsonding field will stay to NULL
 * 
 * Returns the number of OverlayInfo structures filled.
 */
int laymanAPIGetAllInfos(LaymanAPI* l, StringList* overlays, OverlayInfo *results)
{
	return _laymanAPIGetAllInfos(l, overlays, results, NULL);
}

/*
 * Gives a list of OverlayInfo's from the overaly names found in the overlays StringList if it's not NULL
 * If it's NULL, and overlay is not NULL, the information for Overlay will be fetched.
 * results must be allocated and initialized with zeroes.
 * 
 * If an information is unavailable (no owner email for example),
 * the correpsonding field will stay to NULL
 * 
 * Returns the number of OverlayInfo structures filled.
 */
int _laymanAPIGetAllInfos(LaymanAPI* l, StringList* overlays, OverlayInfo *results, const char *overlay)
{
	// Check input data.
	if (!l || !l->object || !results || (!overlays && !overlay))
		return 0;

	PyObject *obj = NULL;

	// First case : overlay list
	if (overlays != NULL)
	{
		// Convert the StringList to a Python list object.
		PyObject *list = cListToPyList(overlays);

		// Call the method
		obj = PyObject_CallMethod(l->object, "get_all_info", "(O)", list);
		Py_DECREF(list);
	}
	// Second case : overlay name
	else if (overlay != NULL)
	{
		obj = PyObject_CallMethod(l->object, "get_all_info", "(s)", overlay);
	}

	// Check if the returned value is a dict as expected.
	if (!obj || !PyDict_Check(obj))
	{
		if (obj)
		{
			Py_DECREF(obj);
		}
		return 0;
	}

	PyObject *name, *dict;
	Py_ssize_t i = 0;

	int k = 0;

	// Loop in the dict to get all dicts.
	while (PyDict_Next(obj, &i, &name, &dict))
	{
		// If it's not a dict, it's ignored
		// FIXME:should an assert be used ?
		if (!dict || !PyDict_Check(dict))
			continue;

		PyObject *official = PyDict_GetItemString(dict, "official");
		PyObject *supported = PyDict_GetItemString(dict, "supported");
		PyObject *ownerName = PyDict_GetItemString(dict, "owner_name");
		PyObject *ownerEmail = PyDict_GetItemString(dict, "owner_email");
		PyObject *homepage = PyDict_GetItemString(dict, "homepage");
		PyObject *description = PyDict_GetItemString(dict, "description");
		PyObject *srcUris = PyDict_GetItemString(dict, "src_uris");
		PyObject *srcType = PyDict_GetItemString(dict, "src_type");
		PyObject *priority = PyDict_GetItemString(dict, "priority");
		PyObject *quality = PyDict_GetItemString(dict, "quality");
//'status':?? TODO

		// Copy values in the kth structure of the results.
		char* tmp = PyString_AsString(name);
		assert(NULL != tmp); //name must not be NULL
		results[k].name = strdup(tmp);

		tmp = PyString_AsString(ownerName);
		if (tmp != NULL)
			results[k].ownerName = strdup(tmp);

		tmp = PyString_AsString(ownerEmail);
		if (tmp != NULL)
			results[k].ownerEmail = strdup(tmp);

		tmp = PyString_AsString(homepage);
		if (tmp != NULL)
			results[k].homepage = strdup(tmp);

		tmp = PyString_AsString(description);
		if (tmp != NULL)
			results[k].description = strdup(tmp);

		tmp = PyString_AsString(srcType);
		if (tmp != NULL)
			results[k].srcType = strdup(tmp);

		tmp = PyString_AsString(quality);
		if (tmp != NULL)
			results[k].quality = strdup(tmp);

		results[k].priority = PyLong_AsLong(priority);

		results[k].srcUris = listToCList(srcUris);

		// If official or supported is neither True or False, abort.
		results[k].official = !PyObject_IsTrue(official);
		assert(-1 != results[k].official);
		results[k].supported = !PyObject_IsTrue(supported);
		assert(-1 != results[k].supported);

		k++;
	}
	
	//The returned value is not necessary anymore.
	Py_DECREF(obj);

	//Return the number of structures that have been filled.
	return k;
}

/*
 * Adds an overlay to layman
 *
 * Return True if it succeeded, False if not
 */
int laymanAPIAddRepo(LaymanAPI* l, const char *repo)
{
	if (!l || !l->object || !repo)
		return 0;

	// Call the method
	PyObject *obj = PyObject_CallMethod(l->object, "delete_repos", "(s)", repo);
	
	// If the call returned NULL, it failed.
	int ret;
	if (!obj)
		ret = 0;
	else
		ret = 1;
	
	Py_DECREF(obj);

	return ret;
}

/*
 * Adds a list of overlays to layman
 *
 * Return True if it succeeded, False if not
 */
int laymanAPIAddRepos(LaymanAPI* l, StringList *repos)
{
	if (!l || !l->object || !repos)
		return 0;

	// Converting the C list to a python list
	PyObject *pyrepos = cListToPyList(repos);

	// Call the method
	PyObject *obj = PyObject_CallMethod(l->object, "add_repos", "(O)", pyrepos);
	Py_DECREF(pyrepos);
	
	// If the call returned NULL, it failed.
	int ret;
	if (!obj)
		ret = 0;
	else
		ret = 1;
	
	Py_DECREF(obj);

	return ret;
}

/*
 * Deletes an overlay from layman
 *
 * Return True if it succeeded, False if not
 */
int laymanAPIDeleteRepo(LaymanAPI* l, const char *repo)
{
	if (!l || !l->object || !repo)
		return 0;

	// Call the method
	PyObject *obj = PyObject_CallMethod(l->object, "delete_repos", "(s)", repo);
	
	// If the call returned NULL, it failed.
	int ret;
	if (!obj)
		ret = 0;
	else
		ret = 1;
	
	Py_DECREF(obj);

	return ret;
}

/*
 * Deletes a list of overlays from layman
 *
 * Return True if it succeeded, False if not
 */
int laymanAPIDeleteRepos(LaymanAPI* l, StringList *repos)
{
	if (!l || !l->object || !repos)
		return 0;

	// Converting the C list to a python list
	PyObject *pyrepos = cListToPyList(repos);
	
	// Call the method
	PyObject *obj = PyObject_CallMethod(l->object, "delete_repos", "(O)", pyrepos);
	Py_DECREF(pyrepos);
	
	// If the call returned NULL, it failed.
	int ret;
	if (!obj)
		ret = 0;
	else
		ret = 1;
	
	Py_DECREF(obj);

	return ret;
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


/*
 * Function that properly frees an OverlayInfo structure's data
 */
void overlayInfoFree(OverlayInfo oi)
{
	if (oi.name)
		free(oi.name);
	if (oi.text)
		free(oi.text);
	if (oi.ownerEmail)
		free(oi.ownerEmail);
	if (oi.ownerName)
		free(oi.ownerName);
	if (oi.homepage)
		free(oi.homepage);
	if (oi.description)
		free(oi.description);
	if (oi.srcType)
		free(oi.srcType);
	if (oi.quality)
		free(oi.quality);
	if (oi.srcUris)
		stringListFree(oi.srcUris);
}
