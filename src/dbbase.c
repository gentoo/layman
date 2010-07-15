//#include "config.h"
#include "dbbase.h"
#include "interpreter.h"
#include "dict.h"
#include <Python.h>

struct DbBase
{
	PyObject *object;
};

DbBase* createDbBase(const char *paths[], unsigned int pathCount, Dict *dict, int ignore, int quiet, int ignore_init_read_errors)
{
	PyObject *pypaths = PyList_New(pathCount);
	for (unsigned int i = 0; i < pathCount; i++)
	{
		PyObject *path = PyBytes_FromString(paths[i]);
		PyList_Insert(pypaths, i, path);
	}

	PyObject *obj = executeFunction("layman.dbbase", "DbBase", "OOIII", pypaths, dictToPyDict(dict), ignore, quiet, ignore_init_read_errors);
	Py_DECREF(pypaths);

	if (!obj)
		return NULL;

	DbBase *ret = malloc(sizeof(DbBase));
	ret->object = obj;

	return ret;
}

void dbBaseFree(DbBase* db)
{
	if (db && db->object)
	{
		Py_DECREF(db->object);
	}
	if (db)
		free(db);
}
