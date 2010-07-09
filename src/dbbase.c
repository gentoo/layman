#include "config.h"
#include "dbbase.h"
#include "interpreter.h"
#include <Python.h>

struct DbBase
{
	PyObject *object;
};

DbBase* createDbBase(const char *paths[], unsigned int pathCount, Config *c, int ignore, int quiet, int ignore_init_read_errors)
{
	PyObject *pypaths = PyList_New(pathCount);
	for (unsigned int i = 0; i < pathCount; i++)
	{
		PyObject *path = PyBytes_FromString(paths[i]);
		PyList_Insert(pypaths, i, path);
	}
	
	PyObject *cfg = _object(c);
	
	PyObject *obj = executeFunction("layman.dbbase", "DbBase", "OOIII", pypaths, cfg, ignore, quiet, ignore_init_read_errors);
	Py_DECREF(pypaths);

	if (!obj)
		return NULL;

	DbBase *ret = malloc(sizeof(DbBase));
	ret->object = obj;

	return ret;
}
