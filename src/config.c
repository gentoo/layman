#include "config.h"
#include "interpreter.h"
#include <Python.h>

struct Config
{
	PyObject *object;
};

PyObject *_object(Config *c)
{
	return c ? c->object : NULL;
}

Config *createConfig(const char *argv[], int argc)
{
	PyObject *pyargs = PyList_New(argc);
	for (int i = 0; i < argc; i++)
	{
		PyObject *arg = PyBytes_FromString(argv[i]);
		PyList_Insert(pyargs, i, arg);
	}

	PyObject *obj = executeFunction("layman.config", "Config", "O", pyargs);
	Py_DECREF(pyargs);
	if (!obj)
		return NULL;

	Config *ret = malloc(sizeof(Config));
	ret->object = obj;

	return ret;
}
