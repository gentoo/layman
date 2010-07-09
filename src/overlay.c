#include <Python.h>

#include "interpreter.h"
#include "overlay.h"

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

void overlayFree(Overlay *o)
{
	if (o && o->object)
		Py_DECREF(o->object);
	if (o)
		free(o);
}
